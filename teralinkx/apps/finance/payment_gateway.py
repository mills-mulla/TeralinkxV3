# apps/finance/payment_gateway.py
import os
import time
import re
import logging
import requests
import base64
import json
from datetime import datetime
from decimal import Decimal

from django.db import IntegrityError
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from users.models import ClientH
from packages.models import PackageType, AvailableVoucher, DispatchVoucher, Coupon
from core.services.rewards_service import RewardsService
from notifications.models import Notification


from core.router.ros_api.api import Api
from core.router.ros_api.api import RouterOSTrapError 
from core.services.notification_service import create_and_notify

from locations.models import Location
from .models import (
    PaymentTransaction,
    PaymentGateway,
    TransactionQueue,
    BalanceTransaction,
    Currency,
    ExchangeRate
)

logger = logging.getLogger(__name__)

# M-Pesa Configuration
MPESA_GATEWAY_TYPE = 'mpesa'

class MpesaGatewayHelper:
    """Handles all M-Pesa gateway operations using PaymentGateway model"""
    
    @staticmethod
    def get_gateway_config():
        """Get M-Pesa gateway configuration.
        Cached in Redis for 1 hour — invalidated on gateway save via admin.
        The gateway ORM object is NOT cached (holds DB state).
        """
        from django.core.cache import cache
        CACHE_KEY = 'mpesa_gateway_config'
        CACHE_TTL = 3600  # 1 hour

        cached = cache.get(CACHE_KEY)
        if cached:
            return cached

        try:
            gateway = PaymentGateway.objects.get(
                gateway_type=MPESA_GATEWAY_TYPE,
                status='active',
                is_default=True
            )
            config = gateway.config

            result = {
                'gateway_id':            gateway.id,
                'consumer_key':          config.get('consumer_key',          os.getenv('CONSUMER_KEY', '')),
                'consumer_secret':       config.get('consumer_secret',       os.getenv('CONSUMER_SECRET', '')),
                'shortcode':             config.get('shortcode',             os.getenv('SHORTCODE', '')),
                'lipa_na_mpesa_passkey': config.get('lipa_na_mpesa_passkey', os.getenv('LIPA_NA_MPESA_PASSKEY', '')),
                'api_base_url':          config.get('api_base_url',          'https://api.safaricom.co.ke'),
                'callback_url':          gateway.callback_url,  # Use database callback URL
                'is_test_mode':          gateway.test_mode,
                'pull_consumer_key':     config.get('pull_consumer_key',     os.getenv('PULL_CONSUMER_KEY',    os.getenv('CONSUMER_KEY', ''))),
                'pull_consumer_secret':  config.get('pull_consumer_secret',  os.getenv('PULL_CONSUMER_SECRET', os.getenv('CONSUMER_SECRET', ''))),
            }
        except PaymentGateway.DoesNotExist:
            logger.warning("No M-Pesa gateway in DB, using environment variables")
            result = {
                'gateway_id':            None,
                'consumer_key':          os.getenv('CONSUMER_KEY', ''),
                'consumer_secret':       os.getenv('CONSUMER_SECRET', ''),
                'shortcode':             os.getenv('SHORTCODE', ''),
                'lipa_na_mpesa_passkey': os.getenv('LIPA_NA_MPESA_PASSKEY', ''),
                'api_base_url':          os.getenv('MPESA_API_BASE_URL', 'https://api.safaricom.co.ke'),
                'callback_url':          'https://srv.teralinkxwaves.uk/api/payments/callback/',  # Updated fallback
                'is_test_mode':          os.getenv('MPESA_TEST_MODE', 'False').lower() == 'true',
                'pull_consumer_key':     os.getenv('PULL_CONSUMER_KEY',    os.getenv('CONSUMER_KEY', '')),
                'pull_consumer_secret':  os.getenv('PULL_CONSUMER_SECRET', os.getenv('CONSUMER_SECRET', '')),
            }

        cache.set(CACHE_KEY, result, CACHE_TTL)
        return result
    
    @staticmethod
    def get_access_token():
        """Retrieve access token from M-Pesa API"""
        from django.db import connection
        
        global _mpesa_token_cache
        
        # Check cache first
        if hasattr(MpesaGatewayHelper, '_mpesa_token_cache'):
            token_data, expiry_time = MpesaGatewayHelper._mpesa_token_cache
            if time.time() < expiry_time:
                return token_data['access_token']
        
        config = MpesaGatewayHelper.get_gateway_config()
        
        # Use sandbox for test mode
        if config['is_test_mode']:
            api_base_url = 'https://sandbox.safaricom.co.ke'
        else:
            api_base_url = config['api_base_url']
        
        access_token_url = f'{api_base_url}/oauth/v1/generate?grant_type=client_credentials'
        
        auth_string = f"{config['consumer_key']}:{config['consumer_secret']}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_auth}'
        }
        
        for attempt in range(3):
            try:
                # Close any stale DB connections before external API call
                connection.close_if_unusable_or_obsolete()
                
                response = requests.get(access_token_url, headers=headers, timeout=10)
                response.raise_for_status()
                token_data = response.json()
                
                # Cache the token
                expires_in_raw = token_data.get('expires_in', 3599)
                try:
                    expires_in = int(expires_in_raw)
                except (TypeError, ValueError):
                    expires_in = 3599
                MpesaGatewayHelper._mpesa_token_cache = (
                    token_data, 
                    time.time() + expires_in - 60  # Refresh 1 min early
                )
                
                logger.info("M-Pesa access token retrieved successfully")
                return token_data['access_token']
                
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1}: Failed to get M-Pesa token: {e}")
                # Close DB connection on error to prevent leaks
                connection.close_if_unusable_or_obsolete()
                if attempt == 2:
                    logger.error("Could not retrieve M-Pesa access token after retries")
                    raise RuntimeError("Could not retrieve M-Pesa access token")
                time.sleep(1)

    @staticmethod
    def normalize_phone(phone: str) -> str:
        """
        Normalize phone number to Safaricom expected format (2547XXXXXXXX).
        - Strip non-digits and leading '+'
        - If starts with '0' and 10 digits -> replace leading 0 with 254
        - If 9 digits -> prefix 254
        - If already 2547... keep as is
        """
        if not phone:
            return phone
        digits = ''.join(filter(str.isdigit, str(phone)))
        # Already full international format
        if digits.startswith('254') and len(digits) == 12:
            return digits
        # Local leading 0: 07XXXXXXXX
        if digits.startswith('0') and len(digits) == 10:
            return '254' + digits[1:]
        # 9-digit local: 7XXXXXXXX
        if len(digits) == 9 and digits.startswith('7'):
            return '254' + digits
        return digits
    
    @staticmethod
    def initiate_stk_push(phone, amount, account_reference, description, package_data=None):
        """Initiate STK push payment"""
        from django.db import connection
        
        config = MpesaGatewayHelper.get_gateway_config()
        token = MpesaGatewayHelper.get_access_token()

        # Normalize phone number to correct format
        phone_normalized = MpesaGatewayHelper.normalize_phone(phone)
        
        # Use sandbox for test mode
        if config['is_test_mode']:
            api_base_url = 'https://sandbox.safaricom.co.ke'
        else:
            api_base_url = config['api_base_url']
        
        payment_url = f'{api_base_url}/mpesa/stkpush/v1/processrequest'
        
        # Generate password
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(
            f"{config['shortcode']}{config['lipa_na_mpesa_passkey']}{timestamp}".encode()
        ).decode()
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        
        payload = {
            "BusinessShortCode": config['shortcode'],
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_normalized,
            "PartyB": config['shortcode'],
            "PhoneNumber": phone_normalized,
            "CallBackURL": config['callback_url'],
            "AccountReference": account_reference,
            "TransactionDesc": description,
            "Items": package_data or []
        }
        
        for attempt in range(3):
            try:
                # Close any stale DB connections before external API call
                connection.close_if_unusable_or_obsolete()
                
                response = requests.post(payment_url, headers=headers, json=payload, timeout=15)
                response.raise_for_status()
                try:
                    result = response.json()
                except ValueError:
                    logger.error(f"STK push non-JSON response: {response.text}")
                    return {
                        'success': False,
                        'error': f"Non-JSON response from M-Pesa: {response.text}"
                    }
                
                if result.get('ResponseCode') == '0':
                    logger.info(f"STK push initiated successfully for {phone}")
                    return {
                        'success': True,
                        'checkout_request_id': result.get('CheckoutRequestID'),
                        'merchant_request_id': result.get('MerchantRequestID'),
                        'response_code': result.get('ResponseCode'),
                        'response_description': result.get('ResponseDescription'),
                        'customer_message': result.get('CustomerMessage')
                    }
                else:
                    logger.error(f"STK push failed: {result.get('ResponseDescription')}")
                    return {
                        'success': False,
                        'error': result.get('ResponseDescription'),
                        'response_code': result.get('ResponseCode')
                    }
                    
            except requests.RequestException as e:
                body = None
                try:
                    if e.response is not None:
                        try:
                            body = e.response.json()
                        except ValueError:
                            body = e.response.text
                except Exception:
                    body = None
                logger.warning(f"STK push attempt {attempt + 1} failed: {e}, body={body}")
                # Close DB connection on error to prevent leaks
                connection.close_if_unusable_or_obsolete()
                if attempt == 2:
                    return {
                        'success': False,
                        'error': str(e),
                        'body': body
                    }
                time.sleep(1)


class TransactionQueueHelper:
    """Handles transaction queue operations"""
    
    @staticmethod
    def create_payment_queue(user, package_code, initiator_phone, checkout_id, 
                           recipient_account, package_name, price,result, used_credit=0,
                           location_id=None):
        """Create a new transaction queue record"""
        from django.core.cache import cache
        
        # Cache currency lookup (1 hour)
        cache_key = 'currency:KES'
        currency = cache.get(cache_key)
        
        if not currency:
            try:
                currency = Currency.objects.get(code='KES')
                cache.set(cache_key, currency, 3600)
            except Currency.DoesNotExist:
                currency = Currency.objects.create(
                    code='KES',
                    name='Kenyan Shilling',
                    symbol='KSh',
                    is_base_currency=True,
                    decimal_places=2
                )
                cache.set(cache_key, currency, 3600)
        
        # Cache package lookup (5 minutes)
        cache_key_pkg = f'package:code:{package_code}'
        package = cache.get(cache_key_pkg)
        
        if not package:
            try:
                package = PackageType.objects.get(code=package_code)
                cache.set(cache_key_pkg, package, 300)
            except PackageType.DoesNotExist:
                package = None
        
        package_type = PackageType.objects.filter(name=package_name).first() if not package else package
        
        # Cache gateway lookup (1 hour)
        cache_key_gw = 'gateway:mpesa:KES'
        gateway = cache.get(cache_key_gw)
        
        if not gateway:
            gateway = PaymentGateway.get_gateway_by_type('mpesa', 'KES')
            if gateway:
                cache.set(cache_key_gw, gateway, 3600)
        
        queue_item = TransactionQueue.objects.create(
            queue_type='payment_processing',
            user=user,
            method='mpesa+balance' if used_credit and Decimal(str(used_credit)) > 0 else 'mpesa',
            initiator=initiator_phone,
            checkout_request_id=checkout_id,
            package_code=package_code,
            package=package_name,
            price=price,
            status='pending',
            account_reference=recipient_account,
            used_credit=used_credit,
            priority='high' if used_credit > 0 else 'normal',
            expires_at=timezone.now() + timezone.timedelta(minutes=30),
            gateway_result_data=result,
            metadata={
                'package_data': {
                    'desc': package_code,
                    'name': package_name,
                    'price': str(price),
                    'package_type_id': package_type.id if package_type else None,
                    'location_id': location_id
                },
                'user_info': {
                    'account': recipient_account,
                    'phone': initiator_phone,
                    'user_id': user.id if user else None
                },
                'created_via': 'api_payment'
            }
        )

        # Create partial PaymentTransaction immediately so every M-Pesa/mixed
        # payment has a financial record from the moment it is initiated.
        # It will be completed (receipt + raw_callback_data filled) when
        # the callback / poll / pull confirms the payment.
        try:
            pt_currency = currency  # already resolved above
            pt_gateway = gateway    # already resolved above
            mpesa_amount = Decimal(str(price)) - Decimal(str(used_credit or 0))
            PaymentTransaction.objects.create(
                transaction_id=f'PENDING_{checkout_id}',
                user=user,
                payment_method='mpesa+balance' if used_credit and used_credit > 0 else 'mpesa',
                payment_gateway=pt_gateway,
                amount=mpesa_amount,
                currency=pt_currency,
                amount_base=mpesa_amount,
                exchange_rate=Decimal('1.0'),
                initiator=initiator_phone,
                balance=Decimal('0'),
                date='',
                result_code=0,
                result_desc='Pending confirmation',
                merchant_request_id=result.get('merchant_request_id', '') if isinstance(result, dict) else '',
                checkout_request_id=checkout_id,
                gateway_reference='',
                account_reference=recipient_account,
                raw_callback_data={},
                status='pending',
                description=f'Initiated STK push for {package_name}'
            )
            logger.info(f"Created partial PaymentTransaction PENDING_{checkout_id}")
        except Exception as pt_err:
            # Non-fatal — queue is the source of truth during processing
            logger.warning(f"Could not create partial PaymentTransaction: {pt_err}")

        logger.info(f"Created queue item {queue_item.id} for {initiator_phone}")
        return queue_item
    
    @staticmethod
    def get_pending_by_checkout_id(checkout_id):
        """Get actionable queue record — delegates to model method for retry logic."""
        return TransactionQueue.get_pending_by_checkout_id(checkout_id)
    
    @staticmethod
    def process_successful_queue(queue_item, mpesa_data):
        """Process successful payment queue item — atomic claim via mark_processing."""
        if queue_item.status in ('completed', 'processed'):
            logger.info(f"Queue item {queue_item.id} already completed, skipping")
            return True

        if not queue_item.mark_processing():
            logger.warning(f"Queue item {queue_item.id} already claimed by another process, skipping")
            return False

        try:
            queue_item.gateway_request_data = {
                'mpesa_response': mpesa_data,
                'processed_at': timezone.now().isoformat()
            }
            queue_item.mark_completed()
            logger.info(f"Queue item {queue_item.id} marked as completed")
            return True

        except Exception as e:
            logger.error(f"Error processing queue item {queue_item.id}: {e}")
            queue_item.mark_failed(
                reason=str(e),
                error_code="QUEUE_PROCESSING_ERROR",
                failure_category="system_error"
            )
            return False


class VoucherHelper:
    """Handles voucher operations with new models"""
    
    @staticmethod
    def activate_voucher(package_code, mpesa_receipt, location_id=None):
        """Activate a voucher using the generate module"""
        try:
            # Import inside method to avoid circular imports
            from .generate import activate_voucher
            from packages.models import PackageType
            
            # Get device limit from package
            try:
                package = PackageType.objects.get(code=package_code)
                devices = package.device_limit
            except PackageType.DoesNotExist:
                devices = 1
            
            # Get location if provided
            location = None
            if location_id:
                location = Location.objects.get(id=location_id)
            
            result = activate_voucher(
                prefix=mpesa_receipt, 
                profile=package_code,
                devices=devices,
                location=location.location_code if location else None
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in voucher activation: {e}")
            return {"status": "failed", "error": str(e)}
    
    @staticmethod
    def create_dispatch_voucher_from_payment(queue_item, payment_transaction, voucher_code, package_type):
        """Create a DispatchVoucher from successful payment"""
        
        try:
            # Get user from queue item or payment transaction
            user = queue_item.user if queue_item else payment_transaction.user
            
            # Get location from metadata or default location
            location_id = queue_item.metadata.get('package_data', {}).get('location_id')
            if location_id:
                location = Location.objects.get(id=location_id)
            else:
                # Get default location for the user or system
                location = Location.objects.filter(is_default=True).first()
                if not location:
                    location = Location.objects.first()
            
            # Get home location (same as location for non-roaming)
            home_location = location
            
            # Create DispatchVoucher with new model structure
            dispatch_voucher = DispatchVoucher.objects.create(
                voucher_code=voucher_code,
                package=package_type,
                user=user,
                location=location,
                home_location=home_location,
                price_paid=queue_item.price if queue_item else payment_transaction.amount,
                activated_at=timezone.now(),
                expires_at=timezone.now() + package_type.duration,
                is_roaming=False,  # Default to non-roaming
                transaction_id=payment_transaction.transaction_id,
                payment_reference=payment_transaction.gateway_reference,
                status='active'
            )
            
            logger.info(f"Created dispatch voucher: {voucher_code} for user {user.account}")
            return dispatch_voucher
            
        except Exception as e:
            logger.error(f"Error creating dispatch voucher: {e}")
            return None
    
    @staticmethod
    def use_available_voucher_as_fallback(queue_item, user):
        """Use pre-generated voucher as fallback"""
        try:
            # Get package type from queue item metadata
            package_type_id = queue_item.metadata.get('package_data', {}).get('package_type_id')
            
            if not package_type_id:
                # Try to find package type by name
                package_type = PackageType.objects.filter(name=queue_item.package).first()
            else:
                package_type = PackageType.objects.get(id=package_type_id)
            
            if not package_type:
                logger.error(f"Package type not found for: {queue_item.package}")
                return None
            
            # Find available voucher for this package
            available_voucher = AvailableVoucher.objects.filter(
                package=package_type,
                is_used=False,
                is_valid=True  # Using property as filter
            ).first()
            
            if not available_voucher:
                logger.warning(f"No available voucher found for package: {package_type.name}")
                return None
            
            # Get location
            location_id = queue_item.metadata.get('package_data', {}).get('location_id')
            location = None
            if location_id:
                location = Location.objects.get(id=location_id)
            
            # Activate the pre-generated voucher
            dispatch_voucher = available_voucher.activate_as_fallback(
                user=user,
                location=location
            )
            
            logger.info(f"Used fallback voucher: {available_voucher.voucher_code}")
            return dispatch_voucher
            
        except Exception as e:
            logger.error(f"Error using fallback voucher: {e}")
            return None


class PaymentTransactionHelper:
    """Handles payment transaction operations"""
    
    @staticmethod
    def create_payment_transaction_from_callback(callback_data, queue_item=None):
        """Create payment transaction from callback data"""
        
        stk_callback = callback_data.get('Body', {}).get('stkCallback', {})
        if not stk_callback:
            return None
        
        merchant_id = stk_callback.get('MerchantRequestID')
        checkout_id = stk_callback.get('CheckoutRequestID')
        result_code = stk_callback.get('ResultCode')
        result_desc = stk_callback.get('ResultDesc')
        
        # Only create for successful transactions
        if result_code != 0:
            logger.info(f"Skipping transaction creation for failed payment: {result_desc}")
            return None
        
        # Extract metadata
        callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
        
        amount = Decimal('0')
        mpesa_receipt = ''
        balance = Decimal('0')
        transaction_date = ''
        initiator_phone = ''
        
        for item in callback_metadata:
            name = item.get('Name')
            value = item.get('Value')
            
            if name == 'Amount':
                amount = Decimal(str(value))
            elif name == 'MpesaReceiptNumber':
                mpesa_receipt = str(value)
            elif name == 'Balance':
                balance = Decimal(str(value)) if value else Decimal('0')
            elif name == 'TransactionDate':
                transaction_date = str(value)
            elif name == 'PhoneNumber':
                initiator_phone = str(value)
        
        # Resolve user — account_reference (CLI...) is the primary identifier.
        # Priority: queue.user > account_reference lookup > phone lookup (last resort)
        user = None
        if queue_item and queue_item.user:
            user = queue_item.user
        else:
            # Try account_reference from BillRefNumber
            bill_ref = callback_data.get('Body', {}).get('BillRefNumber', '') \
                or callback_data.get('_c2b_raw', {}).get('BillRefNumber', '')
            acct = ''
            if 'TERALINKX_WAVES_' in str(bill_ref):
                acct = str(bill_ref).replace('TERALINKX_WAVES_', '').strip()
            if acct:
                try:
                    user = ClientH.objects.get(account=acct)
                except ClientH.DoesNotExist:
                    pass
            # Last resort: phone
            if not user and initiator_phone:
                try:
                    clean = ''.join(filter(str.isdigit, str(initiator_phone)))
                    user = ClientH.objects.filter(
                        phone_number__in=[clean, f'+{clean}']
                    ).first()
                except Exception:
                    pass
            if not user:
                logger.warning(f"User not resolved for callback checkout={checkout_id}")
        
        # Get currency
        try:
            currency = Currency.objects.get(code='KES')
        except Currency.DoesNotExist:
            currency = Currency.objects.create(
                code='KES',
                name='Kenyan Shilling',
                symbol='KSh',
                is_base_currency=True,
                decimal_places=2
            )
        
        # Get gateway
        gateway = PaymentGateway.get_gateway_by_type('mpesa', 'KES')
        
        # Resolve account_reference from queue or raw callback BillRefNumber
        acct_ref = ''
        if queue_item:
            acct_ref = queue_item.account_reference
        else:
            raw_body = callback_data.get('Body', {})
            bill_ref = raw_body.get('BillRefNumber', '') or raw_body.get('_c2b_raw', {}).get('BillRefNumber', '')
            if 'TERALINKX_WAVES_' in str(bill_ref):
                acct_ref = str(bill_ref).replace('TERALINKX_WAVES_', '').strip()

        # Derive correct payment_method — preserve mpesa+balance if queue says so
        pt_method = 'mpesa'
        if queue_item and queue_item.method == 'mpesa+balance':
            pt_method = 'mpesa+balance'

        # Update existing pending PT if one was created at queue initiation,
        # otherwise create a new one (e.g. callback arrived without a prior poll).
        update_fields = dict(
            user=user,
            payment_method=pt_method,
            payment_gateway=gateway,
            amount=amount,
            currency=currency,
            amount_base=amount,
            exchange_rate=Decimal('1.0'),
            initiator=initiator_phone,
            balance=balance,
            date=transaction_date,
            result_code=result_code,
            result_desc=result_desc,
            merchant_request_id=merchant_id,
            gateway_reference=mpesa_receipt,
            account_reference=acct_ref,
            raw_callback_data=callback_data,
            status='completed',
            description=f'M-Pesa payment: {result_desc}'
        )
        real_txn_id = mpesa_receipt or f"MPESA_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        transaction, created = PaymentTransaction.objects.update_or_create(
            checkout_request_id=checkout_id,
            defaults={**update_fields, 'transaction_id': real_txn_id}
        )
        # If the row already existed with a PENDING_ id, update it
        if not created and (transaction.transaction_id.startswith('PENDING_') or not transaction.transaction_id):
            transaction.transaction_id = real_txn_id
            transaction.save(update_fields=['transaction_id'])

        action = 'Created' if created else 'Updated'
        logger.info(f"{action} PaymentTransaction {transaction.transaction_id}")
        
        # Create balance transaction if user exists
        if user and queue_item:
            PaymentTransactionHelper.create_balance_transaction(user, transaction, queue_item)
        
        return transaction
    
    @staticmethod
    def create_balance_transaction(user, payment_transaction, queue_item):
        """Create balance transaction for the payment with atomic balance updates"""
        
        
        # 🔴 FIX: Only create balance transactions for mixed payments with credit usage
        # Pure M-Pesa payments should NOT affect user balance
        if not queue_item.used_credit or queue_item.used_credit <= 0:
                return
        
        
        transaction_type = 'internet_purchase'
        credit = Decimal('0')  # No credit added for M-Pesa payments
        debit = queue_item.used_credit  # Only deduct the credit portion
        
        # 🔴 ATOMIC BALANCE UPDATE WITH VALIDATION
        from django.db import transaction
        with transaction.atomic():
            # Re-fetch user with SELECT FOR UPDATE to prevent race conditions
            user = ClientH.objects.select_for_update().get(id=user.id)
            
            # Get current balance
            balance_before = user.balance
            
            # Calculate net effect (should be negative for credit deduction)
            net_effect = credit - debit
            
            # Validate balance won't go negative
            if balance_before + net_effect < 0:
                raise ValueError(f"Transaction would result in negative balance: {balance_before + net_effect}")
            
            # Update user balance (deduct credit portion)
            user.balance += net_effect
            user.save()
            
            # Create balance transaction
            BalanceTransaction.objects.create(
                user=user,
                transaction_type=transaction_type,
                debit=debit,
                credit=credit,
                balance_before=balance_before,
                balance_after=user.balance,
                payment_transaction=payment_transaction,
                description=f"Credit portion of mixed payment for {queue_item.package_code}",
                reference=payment_transaction.transaction_id
            )
        
    
    @staticmethod
    def clean_phone_number(phone):
        """Normalize phone to match stored format (strips +, handles 0 prefix)"""
        clean_phone = ''.join(filter(str.isdigit, str(phone)))
        if clean_phone.startswith('0') and len(clean_phone) == 10:
            clean_phone = '254' + clean_phone[1:]
        elif len(clean_phone) == 9 and clean_phone.startswith('7'):
            clean_phone = '254' + clean_phone
        # Try exact match first, then with + prefix
        from users.models import ClientH as _ClientH
        try:
            return _ClientH.objects.get(phone_number=clean_phone).phone_number
        except _ClientH.DoesNotExist:
            try:
                return _ClientH.objects.get(phone_number=f'+{clean_phone}').phone_number
            except _ClientH.DoesNotExist:
                return clean_phone


class NotificationHelper:
    """Handles notification operations"""
    
    @staticmethod
    def send_websocket_message(room_name, sender, message):
        # TODO: V2 WebSocket notification via Room model - obsolete.
        # Will be reimplemented when notification app is cleaned up.
        return False

    @staticmethod
    def send_payment_notification(user, message, notification_type='info'):
        # WebSocket disabled - V2 Room model obsolete.
        # TODO: re-enable when notification app is updated.
        try:
            if user:
                create_and_notify(user, message, notification_type)
        except Exception as e:
            logger.warning(f"send_payment_notification failed: {e}")

    @staticmethod
    def send_voucher_notification(recipient, voucher_code, package_name):
        # TODO: V2 WebSocket notification - disabled until notification app updated.
        return False

    @staticmethod
    def send_voucher_details(user, dispatch_voucher):
        """Send detailed voucher information"""
        try:
            if not dispatch_voucher:
                return
            
            message = f"""
🎉 **Voucher Activated Successfully!** 🎉

**Voucher Code:** {dispatch_voucher.voucher_code}
**Package:** {dispatch_voucher.package.name}
**Location:** {dispatch_voucher.location.name}
**Price Paid:** KSh {dispatch_voucher.price_paid}
**Activated:** {dispatch_voucher.activated_at.strftime('%Y-%m-%d %H:%M')}
**Expires:** {dispatch_voucher.expires_at.strftime('%Y-%m-%d %H:%M')}
**Status:** {dispatch_voucher.get_status_display()}

**Package Details:**
- Duration: {dispatch_voucher.package.duration_display}
- Data Limit: {dispatch_voucher.package.data_limit_display}
- Speed: {dispatch_voucher.package.speed_display}
            """
            
            NotificationHelper.send_payment_notification(
                user,
                message,
                "success"
            )
            
        except Exception as e:
            logger.error(f"Error sending voucher details: {e}")


# JWT Protected API Views
class PaymentInitiateAPIView(APIView):
    """Initiate M-Pesa payment (JWT protected)"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Initiate STK push payment - ASYNC with Celery"""
        from .tasks import initiate_mpesa_stk_push
        
        data = request.data
        
        
        # Extract data
        account = (data.get('account') or '').strip()
        if not account and isinstance(jwt_payload, dict):
            account = (jwt_payload.get('client_account') or '').strip()
        
        items = data.get('Items', [])
        
        # Used balance: optional, default 0
        used_credit_raw = data.get('UsedCredit', '0')
        try:
            used_credit = Decimal(str(used_credit_raw))
        except (ValueError, TypeError, ArithmeticError):
            used_credit = Decimal('0')
        
        # Location: optional override, fallback to JWT location_id if present
        location_id = data.get('location_id')
        if location_id is None and isinstance(jwt_payload, dict):
            location_id = jwt_payload.get('location_id')
        
        if not items:
            return Response(
                {'error': 'No items provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        item = items[0]
        package_name = item.get('package', '')
        package_code = item.get('pkg_code', '')

        #get phone number from jwt payload if no initiator is provided in the request
        phone = (data.get('Initiator') or '').strip()
        if not phone and isinstance(jwt_payload, dict):
            phone = (jwt_payload.get('phone_number') or '').strip()

        # Handle coupon discount calculation
        coupon_code = data.get('coupon_code')
        coupon_discount = Decimal('0')
        
        # Get package for price calculation
        try:
            package = PackageType.objects.get(code=package_code)
            base_amount = package.price
        except PackageType.DoesNotExist:
            return Response(
                {'error': 'Package not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Apply coupon discount if provided
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                
                # Check if coupon is expired
                if coupon.valid_until < timezone.now():
                    return Response(
                        {'error': 'Coupon has expired'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Check usage limit
                if coupon.total_uses >= coupon.max_uses:
                    return Response(
                        {'error': 'Coupon usage limit reached'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Calculate discount with M-Pesa compatibility
                if coupon.coupon_type == 'percentage':
                    discount_amount = base_amount * (coupon.discount_value / 100)
                    
                    # 🔴 DYNAMIC M-PESA DISCOUNT ROUNDING SYSTEM
                    import math
                    if base_amount >= 50:
                        discount_amount = Decimal(str(math.ceil(float(discount_amount))))
                    else:
                        discount_amount = Decimal(str(math.floor(float(discount_amount))))
                    
                    coupon_discount = min(discount_amount, base_amount)
                else:  # fixed amount
                    coupon_discount = min(coupon.discount_value, base_amount)
                
                # Apply minimum order value check
                if coupon.minimum_order_value and base_amount < coupon.minimum_order_value:
                    return Response({
                        'error': f'Minimum order value of KES {coupon.minimum_order_value} required'
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except Coupon.DoesNotExist:
                return Response(
                    {'error': 'Invalid coupon code'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Calculate final amount after coupon discount
        final_amount = base_amount - coupon_discount
        final_amount = max(Decimal('1'), Decimal(str(int(final_amount))))
        
        # Use provided amount or calculated amount
        amount = data.get('Amount', '')
        if amount:
            amount = str(amount).strip()
        else:
            amount = str(final_amount)

        # Validate required fields
        if not all([account, amount, package_name, package_code]):
            return Response(
                {'error': 'Missing required fields'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not phone:
            return Response(
                {'error': 'Phone number missing and not available in token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get client/user
        try:
            client = ClientH.objects.get(account=account)
        except ClientH.DoesNotExist:
            return Response(
                {'error': 'Account not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user has sufficient balance if using balance
        if used_credit > 0 and client.balance < used_credit:
            return Response(
                {'error': 'Insufficient balance'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Convert amount to numeric forms
        try:
            amount_int = int(Decimal(amount))
            amount_decimal = Decimal(amount)
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid amount'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Send to Celery and WAIT for M-Pesa response
        try:
            # Call Celery task and wait for result (max 20 seconds)
            task = initiate_mpesa_stk_push.apply_async(
                args=[{
                    'user_id': client.id,
                    'package_code': package_code,
                    'initiator_phone': phone,
                    'recipient_account': account,
                    'package_name': package_name,
                    'price': float(amount_decimal),
                    'used_credit': float(used_credit),
                    'location_id': location_id,
                    'amount_int': amount_int
                }],
                expires=30
            )
            
            # Wait for M-Pesa response (blocks here, but in controlled way)
            result = task.get(timeout=20)
            
            if not result.get('success'):
                return Response(
                    {'error': result.get('error', 'Payment initiation failed')},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Now create queue with REAL checkout ID from M-Pesa
            queue_item = TransactionQueueHelper.create_payment_queue(
                user=client,
                package_code=package_code,
                initiator_phone=phone,
                checkout_id=result.get('checkout_request_id'),  # REAL ID from M-Pesa
                recipient_account=account,
                package_name=package_name,
                price=amount_decimal,
                used_credit=used_credit,
                location_id=location_id,
                result=result
            )
            
        except Exception as e:
            logger.error("Celery task error: %s", e, exc_info=True)
            return Response(
                {'error': 'Payment service temporarily unavailable. Please try again.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
            
        except Exception as e:
            logger.error("Payment queue creation error: %s", e, exc_info=True)
            return Response(
                {'error': 'Failed to queue payment'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Apply coupon if provided
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                coupon.total_uses += 1
                if coupon.total_uses >= coupon.max_uses:
                    coupon.is_active = False
                coupon.save()
                logger.info(f"Applied coupon {coupon_code} with discount {coupon_discount}")
            except Coupon.DoesNotExist:
                pass
        
        # Try to send notification
        try:
            NotificationHelper.send_payment_notification(
                client,
                "🎉 Payment initiated successfully! Please complete payment on your phone.",
                "success"
            )
        except Exception as e:
            logger.warning("Payment initiation notification error: %s", e, exc_info=True)
        
        # Return real checkout ID from M-Pesa
        return Response({
            'success': True,
            'message': 'Payment initiated successfully',
            'checkout_request_id': result.get('checkout_request_id'),
            'merchant_request_id': result.get('merchant_request_id'),
            'customer_message': result.get('customer_message'),
            'queue_id': queue_item.id
        }, status=status.HTTP_200_OK)


class PaymentCallbackAPIView(APIView):
    """Handle M-Pesa callbacks (public endpoint)"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Process M-Pesa callback — handles both STK push and C2B confirmation."""
        callback_data = request.data
        logger.info(f"Received M-Pesa callback: {callback_data}")

        # ── STK Push callback ────────────────────────────────────────────────
        stk_callback = callback_data.get('Body', {}).get('stkCallback', {})
        if stk_callback:
            return self._handle_stk_callback(callback_data, stk_callback)

        # ── C2B confirmation callback ────────────────────────────────────────
        # C2B payload has TransID at the top level (no Body/stkCallback wrapper)
        if 'TransID' in callback_data or 'TransactionType' in callback_data:
            return self._handle_c2b_callback(callback_data)

        logger.error("Unrecognised callback format")
        return Response({'error': 'Invalid callback format'}, status=status.HTTP_400_BAD_REQUEST)

    # ── STK Push ─────────────────────────────────────────────────────────────

    def _handle_stk_callback(self, callback_data, stk_callback):
        merchant_id = stk_callback.get('MerchantRequestID')
        checkout_id = stk_callback.get('CheckoutRequestID')
        result_code = stk_callback.get('ResultCode')
        result_desc = stk_callback.get('ResultDesc')

        logger.info(f"STK Callback: MID={merchant_id}, CID={checkout_id}, Code={result_code}")

        if result_code == 0:
            return self.handle_successful_payment(callback_data, checkout_id)
        elif result_code in [1, 2, 3, 4, 8, 17, 1019, 1025, 1032, 1037, 2001, 2028, 8006]:
            return self.handle_failed_payment(checkout_id, result_code, result_desc)
        else:
            # Unknown non-zero code — treat as failure to avoid stuck queues
            logger.warning(f"Unknown STK result code: {result_code} - {result_desc}")
            return self.handle_failed_payment(checkout_id, result_code, result_desc)

    # ── C2B Confirmation ──────────────────────────────────────────────────────

    def _handle_c2b_callback(self, callback_data):
        """
        C2B confirmation callback - customer paid via paybill independently.
        No TransactionQueue (queue only created for app-initiated STK push).

        Flow:
          1. Idempotency check on TransID
          2. Extract account from BillRefNumber
             Supports: 'TERALINKX_WAVES_CLI000003' or plain 'CLI000003'
          3. Find ClientH by account
          4. Create PaymentTransaction (completed)
          5. Credit client.balance atomically
          6. Create BalanceTransaction (topup) as audit trail
          7. Notify user (non-fatal)
        """
        from django.db import transaction as db_txn

        trans_id   = callback_data.get('TransID', '')
        amount_raw = callback_data.get('TransAmount', '0')
        bill_ref   = str(callback_data.get('BillRefNumber', ''))
        trans_time = callback_data.get('TransTime', '')
        msisdn     = callback_data.get('MSISDN', '')

        logger.info(f"C2B Callback: TransID={trans_id}, Amount={amount_raw}, BillRef={bill_ref}")

        # 1. Idempotency
        if PaymentTransaction.objects.filter(transaction_id=trans_id).exists():
            logger.info(f"C2B: duplicate callback for {trans_id}, ignoring")
            return Response({'message': 'Already processed'}, status=status.HTTP_200_OK)

        # 2. Parse amount
        try:
            amount = Decimal(str(amount_raw))
        except Exception:
            logger.error(f"C2B: invalid amount '{amount_raw}'")
            return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Extract account from BillRefNumber
        # Supports 'TERALINKX_WAVES_CLI000003' or plain 'CLI000003'
        if 'TERALINKX_WAVES_' in bill_ref:
            account = bill_ref.replace('TERALINKX_WAVES_', '').strip()
        else:
            account = bill_ref.strip() or None

        if not account:
            logger.warning(f"C2B: empty BillRefNumber for {trans_id}")
            return Response({'error': 'Invalid BillRefNumber'}, status=status.HTTP_400_BAD_REQUEST)

        # 4. Find client by account
        try:
            client = ClientH.objects.get(account=account)
        except ClientH.DoesNotExist:
            logger.error(f"C2B: no client found for account='{account}', TransID={trans_id}")
            return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            currency = Currency.objects.get(code='KES')
        except Currency.DoesNotExist:
            currency = Currency.objects.create(
                code='KES', name='Kenyan Shilling', symbol='KSh',
                is_base_currency=True, decimal_places=2
            )

        gateway = PaymentGateway.get_gateway_by_type('mpesa', 'KES')

        try:
            with db_txn.atomic():
                # 5. Create PaymentTransaction
                payment_txn = PaymentTransaction.objects.create(
                    transaction_id=trans_id,
                    user=client,
                    payment_method='mpesa',
                    payment_gateway=gateway,
                    amount=amount,
                    currency=currency,
                    amount_base=amount,
                    exchange_rate=Decimal('1.0'),
                    initiator=msisdn,
                    balance=Decimal('0'),
                    date=trans_time,
                    result_code=0,
                    result_desc='C2B paybill payment',
                    merchant_request_id='',
                    checkout_request_id='',
                    gateway_reference=trans_id,
                    account_reference=account,
                    raw_callback_data=callback_data,
                    status='completed',
                    description=f'C2B paybill payment from {msisdn} ref:{bill_ref}'
                )

                # 6. Credit client balance (row-level lock)
                client_locked = ClientH.objects.select_for_update().get(pk=client.pk)
                balance_before = client_locked.balance
                client_locked.balance += amount
                client_locked.save(update_fields=['balance'])

                # 7. Create BalanceTransaction (topup)
                BalanceTransaction.objects.create(
                    user=client_locked,
                    transaction_type='topup',
                    credit=amount,
                    debit=Decimal('0'),
                    balance_before=balance_before,
                    balance_after=client_locked.balance,
                    payment_transaction=payment_txn,
                    description=(
                        f'C2B paybill top-up - KES {amount} received via M-Pesa '
                        f'(TransID: {trans_id}). Use balance to purchase a package.'
                    ),
                    reference=trans_id
                )

            logger.info(
                f"C2B: processed {trans_id} - credited {amount} to {account} "
                f"(balance {balance_before} -> {client_locked.balance})"
            )

        except Exception as e:
            logger.error(f"C2B: error processing {trans_id}: {e}", exc_info=True)
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 8. Notify user (non-fatal - outside atomic block)
        try:
            NotificationHelper.send_payment_notification(
                client,
                f'KES {amount} received via M-Pesa and credited to your account balance. '
                f'Open the app to purchase a package.',
                'success'
            )
        except Exception as notify_err:
            logger.warning(f"C2B: notification failed for {trans_id}: {notify_err}")

        return Response(
            {'message': 'C2B payment processed', 'transaction_id': trans_id},
            status=status.HTTP_200_OK
        )

    # -- STK success / failure ----

    def handle_successful_payment(self, callback_data, checkout_id):
        """Handle successful payment callback"""
        try:
            # Find queue item
            queue_item = TransactionQueueHelper.get_pending_by_checkout_id(checkout_id)
            
            # Create payment transaction
            transaction = PaymentTransactionHelper.create_payment_transaction_from_callback(
                callback_data,
                queue_item
            )
            
            if not transaction:
                logger.error("Failed to create payment transaction")
                return Response(
                    {'error': 'Failed to process payment'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            
            # Process queue item if exists — atomic claim guard
            if queue_item:
                claimed = TransactionQueueHelper.process_successful_queue(queue_item, callback_data)
                if not claimed:
                    logger.warning(f"STK callback: queue {queue_item.id} already claimed, skipping voucher")
                    return Response(
                        {'message': 'Payment already processed'},
                        status=status.HTTP_200_OK
                    )

                # Try to activate voucher (only if we claimed the queue item)
                dispatch_voucher = self.process_voucher_activation(queue_item, transaction)

                if dispatch_voucher:
                    NotificationHelper.send_voucher_details(queue_item.user, dispatch_voucher)
                    # Auto-login (non-fatal)
                    try:
                        self.perform_auto_login(
                            account=queue_item.account_reference,
                            voucher_code=dispatch_voucher.voucher_code,
                            user=queue_item.user
                        )
                    except Exception as e:
                        logger.warning(f"Auto-login failed (non-fatal): {e}")
                else:
                    # Voucher activation failed — refund and mark refunded
                    logger.error(
                        f"STK callback: voucher activation failed for queue {queue_item.id}"
                    )
                    try:
                        from decimal import Decimal as _D
                        from django.db import transaction as _dbt
                        from users.models import ClientH as _C
                        from .models import BalanceTransaction as _BT
                        refund_amount = _D(str(queue_item.price)) - _D(str(queue_item.used_credit or 0))
                        if refund_amount > 0:
                            with _dbt.atomic():
                                client = _C.objects.select_for_update().get(pk=queue_item.user_id)
                                bal_before = client.balance
                                client.balance += refund_amount
                                client.save(update_fields=['balance'])
                                _BT.objects.create(
                                    user=client,
                                    transaction_type='refund',
                                    credit=refund_amount,
                                    debit=_D('0'),
                                    balance_before=bal_before,
                                    balance_after=client.balance,
                                    payment_transaction=transaction,
                                    description=(
                                        f'Refund - voucher activation failed for '
                                        f'{queue_item.package} (TransID: {transaction.transaction_id})'
                                    ),
                                    reference=transaction.transaction_id
                                )
                        queue_item.status = 'refunded'
                        queue_item.save(update_fields=['status'])
                        logger.info(
                            f"STK callback: refunded {refund_amount} to "
                            f"{queue_item.account_reference} queue={queue_item.id}"
                        )
                    except Exception as ref_err:
                        logger.error(f"STK callback: refund failed: {ref_err}")
                    NotificationHelper.send_payment_notification(
                        queue_item.user,
                        'Payment received but service activation failed. '
                        'Amount credited to your balance.',
                        'info'
                    )
            
            logger.info(f"Successfully processed payment: {transaction.transaction_id}")
            
            return Response(
                {'message': 'Payment processed successfully', 'transaction_id': transaction.transaction_id},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Error processing successful payment: {e}", exc_info=True)
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    

    def handle_failed_payment(self, checkout_id, result_code, result_desc):
        """Handle failed payment callback"""
        try:
            queue_item = TransactionQueueHelper.get_pending_by_checkout_id(checkout_id)
            if queue_item:
                # Mark as failed
                failure_reason = self.get_failure_reason(result_code, result_desc)
                queue_item.mark_failed(
                    reason=failure_reason,
                    error_code=f"MPESA_{result_code}",
                    failure_category='payment_gateway',
                    increment_retry=False
                )
                
                # Send notification to user
                if queue_item.user:
                    NotificationHelper.send_payment_notification(
                        queue_item.user,
                        f"❌ Payment failed: {failure_reason}",
                        "error"
                    )
            
            logger.info(f"Payment failed: {result_desc}")
            return Response(
                {'message': 'Failure handled'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Error handling failed payment: {e}")
            return Response(
                {'message': 'Callback received'},
                status=status.HTTP_200_OK
            )
    
    def process_voucher_activation(self, queue_item, payment_transaction):
        """Process voucher activation for successful payment"""
        try:
            if not queue_item:
                logger.warning("No queue item found for voucher activation")
                return None
            
            # Get location from queue metadata
            location_id = queue_item.metadata.get('package_data', {}).get('location_id')
            
            # Try to activate dynamic voucher
            activated_voucher = VoucherHelper.activate_voucher(
                queue_item.package_code,
                payment_transaction.gateway_reference,
                location_id
            )
            
            if activated_voucher.get("status") == "activated":
                voucher_code = activated_voucher["voucher_code"]
                
                # Get package type
                package_type_id = queue_item.metadata.get('package_data', {}).get('package_type_id')
                if package_type_id:
                    package_type = PackageType.objects.get(id=package_type_id)
                else:
                    package_type = PackageType.objects.filter(name=queue_item.package).first()
                
                if not package_type:
                    logger.error(f"Package type not found for: {queue_item.package}")
                    return None
                
                # Create dispatch voucher
                dispatch_voucher = VoucherHelper.create_dispatch_voucher_from_payment(
                    queue_item,
                    payment_transaction,
                    voucher_code,
                    package_type
                )
                
                if dispatch_voucher:
                    # 🎁 AWARD REWARD POINTS FOR M-PESA PURCHASE
                    # Only M-Pesa and M-Pesa + balance purchases earn points
                    # Balance-only purchases do NOT earn points
                    try:
                        user_client = queue_item.user if queue_item else payment_transaction.user
                        if user_client:
                            # Determine payment method from queue item
                            payment_method = getattr(queue_item, 'method', 'mpesa') if queue_item else 'mpesa'
                            
                            # Only award points for M-Pesa payments (pure or mixed)
                            if payment_method in ['mpesa', 'mpesa+balance']:
                                # For mpesa+balance payments, award points on M-Pesa portion only
                                if payment_method == 'mpesa+balance' and queue_item:
                                    # Award points only for the M-Pesa portion
                                    mpesa_amount = payment_transaction.amount  # This is the M-Pesa amount paid
                                    points_awarded = RewardsService.award_purchase_points(
                                        user=user_client,
                                        amount_spent=mpesa_amount,
                                        voucher=dispatch_voucher
                                    )
                                    logger.info(f"Awarded {points_awarded} reward points for M-Pesa portion ({mpesa_amount}) to {user_client.account}")
                                else:
                                    # Pure M-Pesa payment - award points for full amount
                                    points_awarded = RewardsService.award_purchase_points(
                                        user=user_client,
                                        amount_spent=payment_transaction.amount,
                                        voucher=dispatch_voucher
                                    )
                                    logger.info(f"Awarded {points_awarded} reward points for M-Pesa payment to {user_client.account}")
                            else:
                                logger.info(f"No reward points awarded for {payment_method} payment to {user_client.account} (policy)")
                    except Exception as e:
                        logger.error(f"Failed to award reward points: {e}")
                        # Don't fail the purchase if rewards fail
                    
                    logger.info(f"Voucher activated: {voucher_code}")
                    return dispatch_voucher
                else:
                    logger.error("Failed to create dispatch voucher")
                    
            # Try fallback voucher
            logger.info("Trying fallback voucher...")
            return VoucherHelper.use_available_voucher_as_fallback(
                queue_item,
                queue_item.user
            )
            
        except Exception as e:
            logger.error(f"Error in voucher processing: {e}")
            return None
    
    def get_failure_reason(self, result_code, result_desc):
        """Get user-friendly failure reason for all documented M-Pesa result codes"""
        failure_messages = {
            1:    'Insufficient funds in your M-Pesa account',
            2:    'Amount is below the minimum allowed',
            3:    'Amount exceeds the maximum allowed',
            4:    'Transaction would exceed your daily limit',
            8:    'Transaction would exceed maximum account balance',
            17:   'Duplicate transaction — please wait 2 minutes before retrying',
            1019: 'Transaction expired — please try again',
            1025: 'Payment request error — please try again',
            1032: 'Request cancelled by user',
            1037: 'Your phone could not be reached — please try again',
            2001: 'Incorrect M-Pesa PIN entered',
            2028: 'Invalid payment configuration',
            8006: 'M-Pesa account locked — contact Safaricom',
        }
        return failure_messages.get(result_code, result_desc or f'Payment failed (code {result_code})')
    
    def perform_auto_login(self, account, voucher_code, user=None):
        """Auto-login user to hotspot using RouterManager."""
        try:
            from .authentications import RouterManager, RouterConfig, validate_voucher
            from packages.models import DispatchVoucher
            from users.models import ClientH

            client = ClientH.objects.get(account=account)
            hotspot_ip = getattr(client, 'current_ip_address', None)
            if not hotspot_ip:
                logger.info(f"Auto-login skipped for {account}: no hotspot IP")
                return False

            is_valid, _ = validate_voucher(account, voucher_code)
            if not is_valid:
                logger.warning(f"Auto-login: voucher validation failed for {account}")
                return False

            router_config = RouterConfig.get_config()
            with RouterManager(router_config) as router:
                result = router.hotspot_login(
                    username=voucher_code,
                    ip_address=hotspot_ip
                )
            if result:
                logger.info(f"Auto-login successful for {account}")
            else:
                logger.warning(f"Auto-login failed for {account}")
            return bool(result)
        except Exception as e:
            logger.error(f"Auto-login error for {account}: {e}")
            return False


class MpesaPullReconciliation:
    """Handles M-Pesa Pull Transactions API for missed callback reconciliation"""

    @staticmethod
    def get_api_base_url():
        config = MpesaGatewayHelper.get_gateway_config()
        if config['is_test_mode']:
            return 'https://sandbox.safaricom.co.ke'
        return config.get('api_base_url', 'https://api.safaricom.co.ke')

    @staticmethod
    def register_pull(nominated_number, callback_url=None):
        """
        One-time registration of shortcode for Pull API.
        Must be called before querying transactions.
        """
        config = MpesaGatewayHelper.get_gateway_config()
        try:
            token = MpesaPullReconciliation._get_pull_access_token()
        except Exception as e:
            logger.error(f"Pull API register: failed to get token: {e}")
            raise
        base_url = MpesaPullReconciliation.get_api_base_url()

        payload = {
            'ShortCode': config['shortcode'],
            'RequestType': 'Pull',
            'NominatedNumber': nominated_number,
            'CallBackURL': callback_url or config['callback_url']
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        try:
            response = requests.post(
                f'{base_url}/pulltransactions/v1/register',
                headers=headers, json=payload, timeout=15
            )
            result = response.json()
            logger.info(f"Pull API register response: {result}")
            return result
        except Exception as e:
            logger.error(f"Pull API register error: {e}")
            raise

    @staticmethod
    def _get_pull_access_token():
        """
        Get access token for Pull API.
        Uses pull_consumer_key / pull_consumer_secret from gateway config if set,
        otherwise falls back to the standard M-Pesa consumer credentials.
        The Pull API product must be enabled on your Daraja app.
        """
        config = MpesaGatewayHelper.get_gateway_config()
        base_url = MpesaPullReconciliation.get_api_base_url()

        # Use dedicated Pull API credentials if configured, else fall back
        consumer_key = config.get('pull_consumer_key') or config['consumer_key']
        consumer_secret = config.get('pull_consumer_secret') or config['consumer_secret']

        auth_string = f"{consumer_key}:{consumer_secret}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()

        response = requests.get(
            f'{base_url}/oauth/v1/generate?grant_type=client_credentials',
            headers={'Authorization': f'Basic {encoded_auth}'},
            timeout=10
        )
        response.raise_for_status()
        token = response.json().get('access_token')
        if not token:
            raise RuntimeError(f"Pull API token response missing access_token: {response.json()}")
        logger.info("Pull API access token retrieved successfully")
        return token

    @staticmethod
    def query_transactions(start_date, end_date, offset=0):
        """
        Query M-Pesa Pull API for all C2B transactions in the given period.
        Handles pagination automatically — keeps fetching until no more results.
        Returns a flat list of all transaction dicts.
        """
        config = MpesaGatewayHelper.get_gateway_config()
        base_url = MpesaPullReconciliation.get_api_base_url()

        if isinstance(start_date, datetime):
            start_date = start_date.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(end_date, datetime):
            end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')

        all_transactions = []
        current_offset = offset

        while True:
            try:
                token = MpesaPullReconciliation._get_pull_access_token()
            except Exception as e:
                logger.error(f"Pull API: failed to get access token: {e}")
                break
            payload = {
                'ShortCode': config['shortcode'],
                'StartDate': start_date,
                'EndDate': end_date,
                'OffSetValue': str(current_offset)
            }
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
            try:
                response = requests.get(
                    f'{base_url}/pulltransactions/v1/query',
                    headers=headers, json=payload, timeout=15
                )
                result = response.json()
                logger.info(f"Pull API offset={current_offset} ResponseCode={result.get('ResponseCode')}")

                if result.get('ResponseCode') != '1000':
                    logger.warning(f"Pull API non-1000 response: {result}")
                    break

                raw = result.get('Response', {}).get('Transaction', [[]])
                # Safaricom returns [[]] when no more transactions
                if not raw or raw == [[]] or not isinstance(raw[0], dict):
                    break

                all_transactions.extend(raw)

                # If fewer than 100 returned, we've reached the last page
                if len(raw) < 100:
                    break

                current_offset += len(raw)

            except Exception as e:
                logger.error(f"Pull API query error at offset {current_offset}: {e}")
                break

        logger.info(f"Pull API total transactions fetched: {len(all_transactions)}")
        return all_transactions

    @staticmethod
    def pull_and_populate(start_date, end_date):
        """
        Pull API reconciliation - LAST RESORT after callback, polling and Celery all missed.

        Pull API only returns C2B transactions. Two scenarios:

        Scenario A - Missed STK push (app-initiated):
          PT exists with status='pending' (PENDING_...) - created at queue initiation.
          Match by: account_reference from billreference + amount + status=pending.
          Action:
            - Update PT: transaction_id=real receipt, status=completed
            - Find TQ via PT.checkout_request_id, mark processed
            - Credit M-Pesa portion to client.balance (no voucher - user is gone)
            - Create BalanceTransaction (topup)

        Scenario B - Missed C2B (customer manual paybill):
          No PT exists (C2B has no queue, no partial PT).
          Action:
            - Find ClientH by account from billreference
            - Create PT (completed)
            - Credit amount to client.balance
            - Create BalanceTransaction (topup)

        Always credit balance. Never activate voucher.
        Pull runs every 30min - by then Celery has had 15 cycles to resolve via Daraja.
        """
        from django.db import transaction as db_transaction

        pulled_txns = MpesaPullReconciliation.query_transactions(start_date, end_date)

        if not pulled_txns:
            logger.info("pull_and_populate: No transactions returned from Pull API")
            return {'pulled': 0, 'created': 0, 'skipped': 0, 'errors': 0, 'orphans': 0}

        created = skipped = errors = orphans = 0

        for pull_txn in pulled_txns:
            mpesa_receipt = pull_txn.get('transactionId', '')
            amount_raw    = pull_txn.get('amount', '0')
            bill_ref      = str(pull_txn.get('billreference', ''))
            msisdn        = str(pull_txn.get('msisdn', ''))
            trx_date      = str(pull_txn.get('trxDate', ''))

            # Idempotency - skip if already processed
            if PaymentTransaction.objects.filter(transaction_id=mpesa_receipt).exists():
                logger.debug(f"pull_and_populate: Skipping existing txn {mpesa_receipt}")
                skipped += 1
                continue

            try:
                amount = Decimal(str(amount_raw))
            except Exception:
                logger.error(f"pull_and_populate: Invalid amount '{amount_raw}' for {mpesa_receipt}")
                errors += 1
                continue

            # Extract account from billreference
            account = None
            if 'TERALINKX_WAVES_' in bill_ref:
                account = bill_ref.replace('TERALINKX_WAVES_', '').strip()
            else:
                account = bill_ref.strip() or None

            try:
                with db_transaction.atomic():
                    # --- Step 1: Find pending PT (Scenario A - missed STK push) ---
                    pending_pt = None
                    if account:
                        pending_pt = PaymentTransaction.objects.filter(
                            account_reference=account,
                            amount=amount,
                            status='pending'
                        ).order_by('created_at').first()

                    if pending_pt:
                        # Scenario A: app-initiated STK push, callback/poll/Celery all missed
                        checkout_id = pending_pt.checkout_request_id

                        # Update PT with real receipt
                        pending_pt.transaction_id    = mpesa_receipt
                        pending_pt.gateway_reference = mpesa_receipt
                        pending_pt.status            = 'completed'
                        pending_pt.date              = trx_date
                        pending_pt.initiator         = msisdn
                        pending_pt.raw_callback_data = {
                            'source': 'pull_reconciliation',
                            'pull_data': pull_txn
                        }
                        pending_pt.save()

                        # Find and mark TQ processed via checkout_request_id
                        tq = None
                        if checkout_id:
                            tq = TransactionQueue.objects.filter(
                                checkout_request_id=checkout_id,
                                status__in=['pending', 'processing']
                            ).first()
                            if tq:
                                if tq.mark_processing():
                                    # Use direct DB update to avoid stale in-memory status
                                    TransactionQueue.objects.filter(pk=tq.pk).update(
                                        status='processed',
                                        completed_at=timezone.now()
                                    )
                                    logger.info(
                                        f"pull_and_populate: TQ {tq.id} marked processed "
                                        f"via PT {pending_pt.id} -> {mpesa_receipt}"
                                    )
                                else:
                                    logger.info(
                                        f"pull_and_populate: TQ {tq.id} already claimed, skipping"
                                    )

                        # Credit M-Pesa portion to balance (price - used_credit)
                        # used_credit was never deducted at initiation
                        price       = Decimal(str(tq.price))       if tq else amount
                        used_credit = Decimal(str(tq.used_credit or 0)) if tq else Decimal('0')
                        credit_amt  = price - used_credit
                        if credit_amt <= 0:
                            credit_amt = amount

                        client = ClientH.objects.select_for_update().get(
                            pk=pending_pt.user_id
                        )
                        balance_before  = client.balance
                        client.balance += credit_amt
                        client.save(update_fields=['balance'])

                        BalanceTransaction.objects.create(
                            user=client,
                            transaction_type='topup',
                            credit=credit_amt,
                            debit=Decimal('0'),
                            balance_before=balance_before,
                            balance_after=client.balance,
                            payment_transaction=pending_pt,
                            description=(
                                f"Pull reconciliation - KES {credit_amt} credited "
                                f"(missed STK push, TransID: {mpesa_receipt}). "
                                f"Use balance to purchase a package."
                            ),
                            reference=mpesa_receipt
                        )

                        logger.info(
                            f"pull_and_populate: Scenario A recovered {mpesa_receipt} "
                            f"account={account} credited={credit_amt} "
                            f"balance {balance_before} -> {client.balance}"
                        )
                        created += 1

                    else:
                        # Scenario B: missed C2B (no PT, no TQ)
                        if not account:
                            logger.warning(
                                f"pull_and_populate: No account in billreference '{bill_ref}' "
                                f"for {mpesa_receipt} - skipping"
                            )
                            errors += 1
                            continue

                        try:
                            client = ClientH.objects.get(account=account)
                        except ClientH.DoesNotExist:
                            logger.warning(
                                f"pull_and_populate: No client for account={account} "
                                f"TransID={mpesa_receipt} - skipping"
                            )
                            errors += 1
                            continue

                        try:
                            currency = Currency.objects.get(code='KES')
                        except Currency.DoesNotExist:
                            currency = Currency.objects.create(
                                code='KES', name='Kenyan Shilling', symbol='KSh',
                                is_base_currency=True, decimal_places=2
                            )

                        gateway = PaymentGateway.get_gateway_by_type('mpesa', 'KES')

                        payment_txn = PaymentTransaction.objects.create(
                            transaction_id=mpesa_receipt,
                            user=client,
                            payment_method='mpesa',
                            payment_gateway=gateway,
                            amount=amount,
                            currency=currency,
                            amount_base=amount,
                            exchange_rate=Decimal('1.0'),
                            initiator=msisdn,
                            balance=Decimal('0'),
                            date=trx_date,
                            result_code=0,
                            result_desc='Pull API reconciliation - missed C2B',
                            merchant_request_id='',
                            checkout_request_id='',
                            gateway_reference=mpesa_receipt,
                            account_reference=account,
                            raw_callback_data={
                                'source': 'pull_reconciliation',
                                'pull_data': pull_txn
                            },
                            status='completed',
                            description=(
                                f"Pull reconciliation - missed C2B paybill "
                                f"ref:{bill_ref}"
                            )
                        )

                        client_locked  = ClientH.objects.select_for_update().get(pk=client.pk)
                        balance_before = client_locked.balance
                        client_locked.balance += amount
                        client_locked.save(update_fields=['balance'])

                        BalanceTransaction.objects.create(
                            user=client_locked,
                            transaction_type='topup',
                            credit=amount,
                            debit=Decimal('0'),
                            balance_before=balance_before,
                            balance_after=client_locked.balance,
                            payment_transaction=payment_txn,
                            description=(
                                f"Pull reconciliation - KES {amount} credited "
                                f"(missed C2B paybill, TransID: {mpesa_receipt}). "
                                f"Use balance to purchase a package."
                            ),
                            reference=mpesa_receipt
                        )

                        orphans += 1
                        created += 1
                        logger.info(
                            f"pull_and_populate: Scenario B C2B {mpesa_receipt} "
                            f"account={account} credited={amount} "
                            f"balance {balance_before} -> {client_locked.balance}"
                        )

            except Exception as e:
                logger.error(
                    f"pull_and_populate: Error processing {mpesa_receipt}: {e}",
                    exc_info=True
                )
                errors += 1

        summary = {
            'pulled':       len(pulled_txns),
            'created':      created,
            'skipped':      skipped,
            'errors':       errors,
            'orphans':      orphans,
            'period_start': start_date if isinstance(start_date, str) else start_date.isoformat(),
            'period_end':   end_date   if isinstance(end_date,   str) else end_date.isoformat(),
        }
        logger.info(f"pull_and_populate summary: {summary}")
        return summary

    @staticmethod
    def _credit_balance_for_queue(queue_item, payment_txn):
        """
        Credit-only flow for background recovery (Celery check_pending - Path 3).
        Credits the M-Pesa portion only (price - used_credit).
        used_credit was never deducted at initiation.
        Creates a BalanceTransaction topup as audit trail.
        """
        from django.db import transaction as db_txn
        try:
            mpesa_portion = Decimal(str(queue_item.price)) - Decimal(str(queue_item.used_credit or 0))
            if mpesa_portion <= 0:
                logger.info(f"_credit_balance_for_queue: nothing to credit for queue {queue_item.id}")
                return

            with db_txn.atomic():
                client = ClientH.objects.select_for_update().get(id=queue_item.user_id)
                balance_before  = client.balance
                client.balance += mpesa_portion
                client.save(update_fields=['balance'])

                BalanceTransaction.objects.create(
                    user=client,
                    transaction_type='topup',
                    credit=mpesa_portion,
                    debit=Decimal('0'),
                    balance_before=balance_before,
                    balance_after=client.balance,
                    payment_transaction=payment_txn,
                    description=(
                        f"Celery recovery credit for {queue_item.package} "
                        f"(M-Pesa portion KES {mpesa_portion})"
                    ),
                    reference=payment_txn.transaction_id
                )
            logger.info(
                f"_credit_balance_for_queue: credited {mpesa_portion} to "
                f"{queue_item.user} for queue {queue_item.id}"
            )
        except Exception as e:
            logger.error(f"_credit_balance_for_queue: failed for queue {queue_item.id}: {e}")

        # Keep reconcile_missed_callbacks as a thin wrapper that uses pull_and_populate
    @staticmethod
    def reconcile_missed_callbacks(hours_back=2):
        """
        Convenience wrapper used by the Celery periodic task.
        Pulls the last `hours_back` hours and populates PaymentTransaction.
        """
        now = timezone.now()
        start_date = now - timezone.timedelta(hours=hours_back)
        end_date = now - timezone.timedelta(minutes=5)  # give callbacks 5 min to arrive
        return MpesaPullReconciliation.pull_and_populate(start_date, end_date)

class C2BValidationAPIView(APIView):
    """
    C2B Validation URL endpoint (AllowAny - called by Safaricom).
    Only active if external validation is enabled on the shortcode.
    Default: accept all transactions.
    To reject a specific transaction, override this logic.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        bill_ref = request.data.get('BillRefNumber', '')
        msisdn   = request.data.get('MSISDN', '')
        amount   = request.data.get('TransAmount', '')
        logger.info(f"C2B Validation: BillRef={bill_ref}, MSISDN={msisdn}, Amount={amount}")

        # Extract account and validate it exists
        account = None
        if 'TERALINKX_WAVES_' in str(bill_ref):
            account = str(bill_ref).replace('TERALINKX_WAVES_', '').strip()
        else:
            account = str(bill_ref).strip() or None

        if account:
            try:
                ClientH.objects.get(account=account)
                logger.info(f"C2B Validation: account {account} found - accepting")
                return Response({'ResultCode': '0', 'ResultDesc': 'Accepted'})
            except ClientH.DoesNotExist:
                logger.warning(f"C2B Validation: account {account} not found - rejecting")
                return Response({'ResultCode': 'C2B00012', 'ResultDesc': 'Rejected'})

        # No recognisable account reference - reject
        logger.warning(f"C2B Validation: unrecognised BillRefNumber '{bill_ref}' - rejecting")
        return Response({'ResultCode': 'C2B00012', 'ResultDesc': 'Rejected'})


class C2BRegisterURLAPIView(APIView):
    """
    One-time registration of Confirmation and Validation URLs with Safaricom.
    JWT protected - admin only.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            config = MpesaGatewayHelper.get_gateway_config()
            token  = MpesaGatewayHelper.get_access_token()
            base_url = 'https://sandbox.safaricom.co.ke' if config['is_test_mode'] else config['api_base_url']

            confirmation_url = request.data.get('confirmation_url', config['callback_url'])
            validation_url   = request.data.get('validation_url', config['callback_url'].replace('callback', 'c2b/validate'))
            response_type    = request.data.get('response_type', 'Completed')

            payload = {
                'ShortCode':       config['shortcode'],
                'ResponseType':    response_type,
                'ConfirmationURL': confirmation_url,
                'ValidationURL':   validation_url,
            }
            headers = {
                'Content-Type':  'application/json',
                'Authorization': f'Bearer {token}'
            }
            response = requests.post(
                f'{base_url}/mpesa/c2b/v2/registerurl',
                headers=headers, json=payload, timeout=15
            )
            result = response.json()
            logger.info(f"C2B RegisterURL response: {result}")
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"C2B RegisterURL error: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReconciliationAPIView(APIView):
    """Manual trigger for Pull API reconciliation (admin/internal use)"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, action=None):
        """
        Pull transactions and populate PaymentTransaction.
        Query params:
          - start_date: 'YYYY-MM-DD HH:MM:SS'  (default: 2 hours ago)
          - end_date:   'YYYY-MM-DD HH:MM:SS'  (default: now)
        """
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date:
            start_date = timezone.now() - timezone.timedelta(hours=2)
        if not end_date:
            end_date = timezone.now()

        try:
            result = MpesaPullReconciliation.pull_and_populate(start_date, end_date)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"ReconciliationAPIView GET error: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, action=None):
        """Register shortcode with Pull API (one-time setup)"""
        if action == 'register':
            nominated_number = request.data.get('nominated_number')
            callback_url = request.data.get('callback_url')
            if not nominated_number:
                return Response({'error': 'nominated_number required'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                result = MpesaPullReconciliation.register_pull(nominated_number, callback_url)
                return Response(result, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Default POST: pull and populate with body-supplied date range
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        if not start_date:
            start_date = timezone.now() - timezone.timedelta(hours=2)
        if not end_date:
            end_date = timezone.now()
        try:
            result = MpesaPullReconciliation.pull_and_populate(start_date, end_date)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"ReconciliationAPIView POST error: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentStatusAPIView(APIView):
    """Check payment status (JWT protected)"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, checkout_request_id=None):
        """Get payment status by checkout_request_id"""
        if not checkout_request_id:
            return Response(
                {'error': 'checkout_request_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Check transaction queue
            queue_item = TransactionQueue.objects.filter(
                checkout_request_id=checkout_request_id
            ).first()
            
            if not queue_item:
                return Response(
                    {'error': 'Payment not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check payment transactions
            payment_transaction = PaymentTransaction.objects.filter(
                checkout_request_id=checkout_request_id
            ).first()
            
            # Check dispatch vouchers for this payment
            dispatch_voucher = None
            if payment_transaction:
                dispatch_voucher = DispatchVoucher.objects.filter(
                    transaction_id=payment_transaction.transaction_id
                ).first()
            
            response_data = {
                'status': queue_item.status,
                'queue_status': queue_item.status,
                'payment_status': payment_transaction.status if payment_transaction else 'pending',
                'transaction_id': payment_transaction.transaction_id if payment_transaction else None,
                'amount': float(payment_transaction.amount) if payment_transaction else float(queue_item.price),
                'voucher_created': dispatch_voucher is not None,
                'voucher_code': dispatch_voucher.voucher_code if dispatch_voucher else None,
                'voucher_status': dispatch_voucher.status if dispatch_voucher else None,
                'checkout_request_id': checkout_request_id
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error checking payment status: {e}")
            return Response(
                {'error': 'Failed to check payment status'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
