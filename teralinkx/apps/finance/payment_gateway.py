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
        """Get M-Pesa gateway configuration from database"""
        try:
            gateway = PaymentGateway.objects.get(
                gateway_type=MPESA_GATEWAY_TYPE,
                status='active',
                is_default=True
            )
            
            config = gateway.config
            
            # Ensure callback URLs are set
            if not gateway.callback_url:
                gateway.callback_url = 'https://teralinkxwaves.uk/api/payments/callback/'
                gateway.save()
            
            return {
                'gateway': gateway,
                'consumer_key': config.get('consumer_key', os.getenv('CONSUMER_KEY', '')),
                'consumer_secret': config.get('consumer_secret', os.getenv('CONSUMER_SECRET', '')),
                'shortcode': config.get('shortcode', '4989904'),
                'lipa_na_mpesa_passkey': config.get('lipa_na_mpesa_passkey', os.getenv('LIPA_NA_MPESA_PASSKEY', '')),
                'api_base_url': config.get('api_base_url', 'https://api.safaricom.co.ke'),
                'callback_url': gateway.get_effective_callback_url(),
                'is_test_mode': gateway.test_mode
            }
        except PaymentGateway.DoesNotExist:
            # Fallback to environment variables if no gateway configured
            logger.warning("No M-Pesa gateway found in database, using environment variables")
            return {
                'gateway': None,
                'consumer_key': os.getenv('CONSUMER_KEY', ''),
                'consumer_secret': os.getenv('CONSUMER_SECRET', ''),
                'shortcode': '4989904',
                'lipa_na_mpesa_passkey': os.getenv('LIPA_NA_MPESA_PASSKEY', ''),
                'api_base_url': 'https://api.safaricom.co.ke',
                'callback_url': 'https://teralinkxwaves.uk/api/payment/callback/',
                'is_test_mode': False
            }
    
    @staticmethod
    def get_access_token():
        """Retrieve access token from M-Pesa API"""
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
        
        # Get KES currency
        try:
            currency = Currency.objects.get(code='KES')
        except Currency.DoesNotExist:
            # Create KES currency if not exists
            currency = Currency.objects.create(
                code='KES',
                name='Kenyan Shilling',
                symbol='KSh',
                is_base_currency=True,
                decimal_places=2
            )
        
        # Get package for metadata
        try:
            package = PackageType.objects.get(code=package_code)
            package_type = PackageType.objects.filter(name=package_name).first()
        except PackageType.DoesNotExist:
            package = None
            package_type = None
        
        # Get gateway
        gateway = PaymentGateway.get_gateway_by_type('mpesa', 'KES')
        
        queue_item = TransactionQueue.objects.create(
            queue_type='payment_processing',
            user=user,
            method='mpesa',
            initiator=initiator_phone,
            checkout_request_id=checkout_id,
            package_code=package_code,
            package=package_name,
            price=price,
            status='pending',
            recipient=recipient_account,
            used_credit=used_credit,
            priority='high' if used_credit > 0 else 'normal',
            expires_at=timezone.now() + timezone.timedelta(minutes=30),
            gateway_result_data= result,
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
        
        logger.info(f"Created queue item {queue_item.id} for {initiator_phone}")
        return queue_item
    
    @staticmethod
    def get_pending_by_checkout_id(checkout_id):
        """Get pending queue record by checkout_request_id"""
        try:
            return TransactionQueue.objects.get(
                checkout_request_id=checkout_id,
                status__in=['pending', 'processing']
            )
        except TransactionQueue.DoesNotExist:
            return None
    
    @staticmethod
    def process_successful_queue(queue_item, mpesa_data):
        """Process successful payment queue item"""
        queue_item.mark_processing()
        
        try:
            # Update queue with payment result
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
            from .views.chekout_confirmation import get_device_by_package_code
            
            pkginst = get_device_by_package_code(package_code)
            devices = pkginst.devices if pkginst else 1
            
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
        
        # Get or create user
        try:
            # Clean phone number
            clean_phone = PaymentTransactionHelper.clean_phone_number(initiator_phone)
            user = ClientH.objects.get(phone_number=clean_phone)
        except ClientH.DoesNotExist:
            # Try to get user from queue item
            if queue_item and queue_item.user:
                user = queue_item.user
            else:
                logger.warning(f"User not found for phone: {initiator_phone}")
                user = None
        
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
        
        # Create payment transaction
        transaction = PaymentTransaction.objects.create(
            transaction_id=mpesa_receipt or f"MPESA_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            user=user,
            payment_method='mpesa',
            payment_gateway=gateway,
            amount=amount,
            currency=currency,
            amount_base=amount,  # KES is base currency
            exchange_rate=Decimal('1.0'),
            initiator=initiator_phone,
            balance=balance,
            date=transaction_date,
            result_code=result_code,
            result_desc=result_desc,
            merchant_request_id=merchant_id,
            checkout_request_id=checkout_id,
            gateway_reference=mpesa_receipt,
            raw_callback_data=callback_data,
            status='completed',
            description=f"M-Pesa payment: {result_desc}"
        )
        
        logger.info(f"Created payment transaction {transaction.transaction_id}")
        
        # Create balance transaction if user exists
        if user and queue_item:
            PaymentTransactionHelper.create_balance_transaction(user, transaction, queue_item)
        
        return transaction
    
    @staticmethod
    def create_balance_transaction(user, payment_transaction, queue_item):
        """Create balance transaction for the payment with atomic balance updates"""
        
        # 🔍 DEBUG: Log balance transaction attempt
        logger.info(f"BALANCE TRANSACTION DEBUG - User: {user.account}, Queue used_credit: {queue_item.used_credit if queue_item else 'N/A'}")
        
        # 🔴 FIX: Only create balance transactions for mixed payments with credit usage
        # Pure M-Pesa payments should NOT affect user balance
        if not queue_item.used_credit or queue_item.used_credit <= 0:
            logger.info(f"BALANCE TRANSACTION DEBUG - Pure M-Pesa payment - no balance transaction needed for {user.account}")
            return
        
        logger.info(f"BALANCE TRANSACTION DEBUG - Creating balance transaction for mixed payment: credit={queue_item.used_credit}")
        
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
        
        logger.info(f"BALANCE TRANSACTION DEBUG - Mixed payment balance transaction: {balance_before} → {user.balance} (deducted {debit}) for {user.account}")
    
    @staticmethod
    def clean_phone_number(phone):
        """Clean and format phone number"""
        clean_phone = ''.join(filter(str.isdigit, phone))
        if clean_phone.startswith('0') and len(clean_phone) == 10:
            clean_phone = '254' + clean_phone[1:]
        elif len(clean_phone) == 9:
            clean_phone = '254' + clean_phone
        return clean_phone


class NotificationHelper:
    """Handles notification operations"""
    
    @staticmethod
    def send_websocket_message(room_name, sender, message):
        """Send message via WebSocket"""
        try:
            room = Room.objects.get(room_name=room_name)
            Message.objects.create(room=room, sender=sender, message=message)
            
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"room_{room_name}",
                {
                    'type': 'send_message',
                    'message': {
                        'sender': sender,
                        'message': message,
                        'room_name': room_name,
                    }
                }
            )
            return True
        except Room.DoesNotExist:
            logger.error(f"Room {room_name} does not exist")
            return False
    
    @staticmethod
    def send_payment_notification(user, message, notification_type='info'):
        """Send payment notification to user"""
        if user:
            create_and_notify(user, message, notification_type)
        
        # Also send via WebSocket if possible
        if hasattr(user, 'account'):
            NotificationHelper.send_websocket_message(
                user.account,
                'system',
                message
            )
    
    @staticmethod
    def send_voucher_notification(recipient, voucher_code, package_name):
        """Send voucher notification"""
        success = NotificationHelper.send_websocket_message(
            recipient, 
            'system', 
            '🎉 Congratulations! Your purchase was successful. 🎉'
        )
        
        if success:
            NotificationHelper.send_websocket_message(
                recipient,
                'system',
                f'🎉 Your voucher for {package_name} is: {voucher_code}'
            )
        return success
    
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
        """Initiate STK push payment"""
        data = request.data
        
        # DEBUG: Inspect JWT / authenticated user
        auth_obj = getattr(request, "auth", None)
        jwt_payload = getattr(auth_obj, "payload", None)
        if settings.DEBUG:
            try:
                print(
                    "DEBUG PaymentInitiateAPIView JWT:",
                    "user_id=", getattr(request.user, "id", None),
                    "username=", getattr(request.user, "username", None),
                    "auth_raw=", auth_obj,
                    "auth_payload=", jwt_payload,
                )
            except Exception as e:
                print(f"DEBUG PaymentInitiateAPIView JWT inspection failed: {e}")
        
        # Extract data
        # Prefer explicit values from payload; fall back to JWT where possible
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
                    # For expensive packages (≥50 KES): Round UP (ceiling) - more generous
                    # For cheap packages (<50 KES): Round DOWN (floor) - conservative
                    import math
                    if base_amount >= 50:
                        # Expensive packages: Round UP for better customer experience
                        discount_amount = Decimal(str(math.ceil(float(discount_amount))))
                    else:
                        # Cheap packages: Round DOWN to maintain profitability
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
        
        # 🔴 ENSURE FINAL AMOUNT IS WHOLE NUMBER FOR M-PESA
        final_amount = max(Decimal('1'), Decimal(str(int(final_amount))))  # Minimum 1 KES
        
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
        
        # Initiate STK push and create queue record
        try:
            result = MpesaGatewayHelper.initiate_stk_push(
                phone=phone,
                amount=amount_int,
                account_reference=f"TERALINKX_WAVES_{account}",
                description=f"Payment for {package_name}",
                package_data=items
            )
            print(result)
            if not result.get('success'):
                return Response(
                    {'error': result.get('error', 'Payment initiation failed')},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            queue_item = TransactionQueueHelper.create_payment_queue(
                user=client,
                package_code=package_code,
                initiator_phone=phone,
                checkout_id=result.get('checkout_request_id'),
                recipient_account=account,
                package_name=package_name,
                price=amount_decimal,
                used_credit=used_credit,
                location_id=location_id,
                result=result
            )
            
            # Apply coupon if provided
            if coupon_code:
                try:
                    coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                    # Increment usage count
                    coupon.total_uses += 1
                    # If max uses reached, deactivate coupon
                    if coupon.total_uses >= coupon.max_uses:
                        coupon.is_active = False
                    coupon.save()
                    logger.info(f"Applied coupon {coupon_code} with discount {coupon_discount}")
                except Coupon.DoesNotExist:
                    pass  # Already validated above
        except Exception as e:
            logger.error("Payment initiation core error: %s", e, exc_info=True)
            return Response(
                {'error': 'Failed to initiate payment'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Try to send notification, but don't fail the payment if this breaks
        try:
            NotificationHelper.send_payment_notification(
                client,
                "🎉 Payment initiated successfully! Please complete payment on your phone.",
                "success"
            )
        except Exception as e:
            logger.warning("Payment initiation notification error: %s", e, exc_info=True)
        
        #review the response structure during frontend intergartion
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
        """Process M-Pesa callback"""
        callback_data = request.data
        logger.info(f"Received M-Pesa callback: {callback_data}")
        
        stk_callback = callback_data.get('Body', {}).get('stkCallback', {})
        if not stk_callback:
            logger.error("No stkCallback in request")
            return Response(
                {'error': 'Invalid callback format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        merchant_id = stk_callback.get('MerchantRequestID')
        checkout_id = stk_callback.get('CheckoutRequestID')
        result_code = stk_callback.get('ResultCode')
        result_desc = stk_callback.get('ResultDesc')
        
        logger.info(f"Callback: MID={merchant_id}, CID={checkout_id}, Code={result_code}")
        
        # Handle based on result code
        if result_code == 0:
            return self.handle_successful_payment(callback_data, checkout_id)
        elif result_code in [1, 1032, 1037, 2001]:
            return self.handle_failed_payment(checkout_id, result_code, result_desc)
        else:
            logger.warning(f"Unknown result code: {result_code} - {result_desc}")
            return Response(
                {'message': 'Callback received'},
                status=status.HTTP_200_OK
            )
    
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
            
            # Handle mixed payment credit deduction ONLY if credit was actually used
            if queue_item and queue_item.used_credit > 0:
                logger.info(f"CALLBACK DEBUG - Processing mixed payment with credit: {queue_item.used_credit}")
                # Credit deduction is already handled in create_balance_transaction
                # No additional deduction needed here
            else:
                logger.info(f"CALLBACK DEBUG - Pure M-Pesa payment - no credit deduction needed")
            
            # Process queue item if exists
            if queue_item:
                success = TransactionQueueHelper.process_successful_queue(queue_item, callback_data)
                if not success:
                    logger.error(f"Failed to process queue item for checkout: {checkout_id}")
            
            # Try to activate voucher
            dispatch_voucher = self.process_voucher_activation(queue_item, transaction)
            
            if dispatch_voucher:
                # Send detailed voucher notification
                user = queue_item.user if queue_item else transaction.user
                NotificationHelper.send_voucher_details(user, dispatch_voucher)
            
            # Perform auto-login if needed
            if queue_item and queue_item.recipient:
                self.perform_auto_login(queue_item.recipient)
            
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
                    try:
                        user_client = queue_item.user if queue_item else payment_transaction.user
                        if user_client:
                            points_awarded = RewardsService.award_purchase_points(
                                user=user_client,
                                amount_spent=payment_transaction.amount,
                                voucher=dispatch_voucher
                            )
                            logger.info(f"Awarded {points_awarded} reward points to {user_client.account}")
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
        """Get user-friendly failure reason"""
        failure_messages = {
            1: "Insufficient funds in your M-Pesa account",
            1032: "Request cancelled by user",
            1037: "Timeout - Please try again",
            2001: "Invalid phone number format"
        }
        return failure_messages.get(result_code, result_desc)
    
    def perform_auto_login(self, account):
        """Perform automatic login for the client"""
        try:
            from .authentications import validate_voucher, who, TeralinkxWaves, how
            
            client = ClientH.objects.get(account=account)
            current_ip = client.current_ip_address
            
            # Get the latest active voucher for this account
            latest_voucher = DispatchVoucher.objects.filter(
                user=client,
                status='active'
            ).order_by('-activated_at').first()
            
            if not latest_voucher:
                logger.warning(f"No active voucher found for {account}")
                return
            
            # Validate voucher
            is_valid, _ = validate_voucher(account, latest_voucher.voucher_code)
            if not is_valid:
                logger.error(f"Voucher validation failed for {account}")
                return
            
            # Perform auto-login
            router = Api(TeralinkxWaves, user=who, password=how, port=8728, verbose=True)
            router.talk(f'/ip/hotspot/active/login =user={latest_voucher.voucher_code} =ip={current_ip}')
            logger.info(f"Auto-login successful for {account}")
            
        except Exception as e:
            logger.error(f"Auto-login failed for {account}: {e}")


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
            queue_item = TransactionQueueHelper.get_pending_by_checkout_id(checkout_request_id)
            
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
                'queue_status': queue_item.status if queue_item else 'not_found',
                'payment_status': payment_transaction.status if payment_transaction else 'not_found',
                'transaction_id': payment_transaction.transaction_id if payment_transaction else None,
                'amount': float(payment_transaction.amount) if payment_transaction else None,
                'voucher_created': dispatch_voucher is not None,
                'voucher_code': dispatch_voucher.voucher_code if dispatch_voucher else None,
                'voucher_status': dispatch_voucher.status if dispatch_voucher else None
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error checking payment status: {e}")
            return Response(
                {'error': 'Failed to check payment status'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )