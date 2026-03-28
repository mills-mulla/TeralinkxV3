import os
import requests
import json
import base64
import logging
from datetime import datetime
from django.http import JsonResponse

logger = logging.getLogger(__name__)

CONSUMER_KEY    = os.environ.get('CONSUMER_KEY', '')
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET', '')


def get_access_token():
    from django.core.cache import cache

    cached = cache.get('mpesa_daraja_access_token')
    if cached:
        return cached

    logger.info("Fetching M-Pesa access token...")
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {base64.b64encode((CONSUMER_KEY + ":" + CONSUMER_SECRET).encode()).decode()}'
    }
    try:
        response = requests.get(
            'https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials',
            headers=headers, timeout=10
        )
        response.raise_for_status()
        result = response.json()
        access_token = result.get('access_token', '')
        if not access_token:
            logger.error("Access token not found in response")
            return JsonResponse({'error': 'Access token not found'})
        # Cache for 55 minutes (token valid 1 hour, 5 min buffer)
        cache.set('mpesa_daraja_access_token', access_token, timeout=3300)
        return access_token
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error fetching access token: {e}")
        return JsonResponse({'error': f"Request error: {e}"})
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error fetching access token: {e}")
        return JsonResponse({'error': f"JSON decoding error: {e}"})


def query_stk_status(checkout_request_id):
    access_token = get_access_token()
    if isinstance(access_token, JsonResponse):
        return access_token

    # Read shortcode and passkey from gateway config — same source as STK push initiation
    try:
        from finance.payment_gateway import MpesaGatewayHelper
        config = MpesaGatewayHelper.get_gateway_config()
        business_short_code = str(config.get('shortcode', os.environ.get('SHORTCODE', '')))
        passkey = config.get('lipa_na_mpesa_passkey', os.environ.get('LIPA_NA_MPESA_PASSKEY', ''))
        query_url = (
            'https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query'
            if config.get('is_test_mode')
            else 'https://api.safaricom.co.ke/mpesa/stkpushquery/v1/query'
        )
    except Exception as e:
        logger.warning(f"Could not load gateway config, falling back to env: {e}")
        business_short_code = os.environ.get('SHORTCODE', '')
        passkey = os.environ.get('LIPA_NA_MPESA_PASSKEY', '')
        query_url = 'https://api.safaricom.co.ke/mpesa/stkpushquery/v1/query'

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(
        (business_short_code + passkey + timestamp).encode()
    ).decode()

    query_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }
    query_payload = {
        'BusinessShortCode': business_short_code,
        'Password': password,
        'Timestamp': timestamp,
        'CheckoutRequestID': checkout_request_id
    }

    try:
        response = requests.post(query_url, headers=query_headers, json=query_payload, timeout=10)
        response.raise_for_status()
        response_data = response.json()

        if 'ResultCode' in response_data:
            result_code = response_data['ResultCode']
            message = {
                '4999': 'Transaction is still under processing',
                '1037': 'Timeout in completing transaction',
                '1032': 'Transaction has been canceled by the user',
                '1':    'The balance is insufficient for the transaction',
                '0':    'The transaction was successful',
            }.get(str(result_code), f'Unknown result code: {result_code}')
            response_data['message'] = message
        else:
            message = 'Error in response'
            response_data['message'] = message

        logger.info(f"STK Query Result: {message}")
        return response_data

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error querying STK status: {e}")
        return JsonResponse({'error': f"Network error: {e}"})
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error querying STK status: {e}")
        return JsonResponse({'error': f"JSON parsing error: {e}"})
