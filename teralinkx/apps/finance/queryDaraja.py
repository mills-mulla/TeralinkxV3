import os
import requests
import json
import base64
import logging
from datetime import datetime
from django.http import JsonResponse

# Setup logging
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Show logs in the console
    ]
)

API_BASE_URL = 'https://api.safaricom.co.ke'
ACCESS_TOKEN_URL = f'{API_BASE_URL}/oauth/v1/generate?grant_type=client_credentials'

CONSUMER_KEY = os.environ.get('CONSUMER_KEY', 'CPe46xBGjBKU38JTT8LplQ0ZfE4Mkj2W46GxtYtEoDGwGxDA')
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET','kdi0wBA13A6wODP1x3VujzRjijIYTmpJlF3LlswzIXL5XaMAN56PCmduLK2FrRAZ')

def get_access_token():
    global access_token

    logging.info("Fetching access token...")
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {base64.b64encode((CONSUMER_KEY + ":" + CONSUMER_SECRET).encode()).decode()}'
    }

    try:
        response = requests.get(ACCESS_TOKEN_URL, headers=headers, timeout=10)
        response.raise_for_status()  # Raise error for non-2xx responses
        
        result = response.json()
        access_token = result.get('access_token', '')

        if not access_token:
            logging.error("Access token not found in response")
            return JsonResponse({'error': 'Access token not found'})

        # logging.debug(f"Access Token: {access_token}")
        return access_token
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {e}")
        return JsonResponse({'error': f"Request error: {e}"})
    except json.JSONDecodeError as e:
        # logging.error(f"JSON decoding error: {e}")
        return JsonResponse({'error': f"JSON decoding error: {e}"})

def query_stk_status(checkout_request_id):
    # logging.info("Starting STK query process...")

    access_token = get_access_token()
    if isinstance(access_token, JsonResponse):
        return access_token  # Return the error response

    # logging.info("Access token retrieved successfully. Proceeding with STK query.")

    query_url = 'https://api.safaricom.co.ke/mpesa/stkpushquery/v1/query'
    business_short_code = '4989904'
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    passkey = "47edf3c3565c0c73aadd88633ac8b560b7fd7441b360d64afb66ed634dfffdb8"
    password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()
   

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

    # logging.debug(f"STK Query Payload: {query_payload}")

    try:
        response = requests.post(query_url, headers=query_headers, json=query_payload, timeout=10)
        response.raise_for_status()

        response_data = response.json()
        logging.debug(f"STK Query Response: {response_data}")

        if 'ResultCode' in response_data:
            result_code = response_data['ResultCode']
            message = {
                '4999': "Transaction is still under processing",
                '1037': "Timeout in completing transaction",
                '1032': "Transaction has been canceled by the user",
                '1': "The balance is insufficient for the transaction",
                '0': "The transaction was successful"
            }.get(result_code, f"Unknown result code: {result_code}")
            response_data['message'] = message 
        else:
            response_data['message'] = "Error in response"
        logging.info(f"STK Query Result: {message}")
        return response_data

    except requests.exceptions.RequestException as e:
        logging.error(f"Network error: {e}")
        return JsonResponse({'error': f"Network error: {e}"})
    except json.JSONDecodeError as e:
        logging.error(f"JSON parsing error: {e}")
        return JsonResponse({'error': f"JSON parsing error: {e}"})

if __name__ == "__main__":
    logging.info("Running queryDaraja.py directly...")
    result = query_stk_status()
    logging.info(f"Final result: {result.content.decode('utf-8')}")
