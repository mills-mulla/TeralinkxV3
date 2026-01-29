from dotenv import load_dotenv
import os
load_dotenv()

from rest_framework.permissions import AllowAny
import time
import logging
import re
import logging
import requests
import base64
import json
from datetime import datetime
from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db.models import Q
from .models import (
    Transaction, AvailableVoucher, DispatchVoucher,
    Queue, ClientH, Room, Message, Package
)

from .scheduler import task_update_active_users as update_active_users
from .router.ros_api.api import Api
from .router.ros_api.api import RouterOSTrapError 
from .services.notification_service import create_and_notify
from django.contrib.auth import get_user_model
User = get_user_model()

logger = logging.getLogger(__name__)

# M-Pesa Configuration
API_BASE_URL = 'https://api.safaricom.co.ke'
ACCESS_TOKEN_URL = f'{API_BASE_URL}/oauth/v1/generate?grant_type=client_credentials'
PAYMENT_URL = f'{API_BASE_URL}/mpesa/stkpush/v1/processrequest'
CALLBACK_URL = 'https://teralinkxwaves.uk/api/callback/'
CONSUMER_KEY = os.getenv('CONSUMER_KEY', '')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET', '')
SHORTCODE = '4989904'
LIPA_NA_MPESA_PASSKEY = os.getenv('LIPA_NA_MPESA_PASSKEY','')
TIMESTAMP = datetime.now().strftime('%Y%m%d%H%M%S')
PASSWORD = base64.b64encode(f"{SHORTCODE}{LIPA_NA_MPESA_PASSKEY}{TIMESTAMP}".encode('utf-8')).decode('utf-8')
access_token = ''

token_expiry = 0  # Unix timestamp of token expiration

class MpesaHelper:
    """Handles all M-Pesa related operations"""

    @staticmethod
    def get_access_token():
        """Retrieve access token from M-Pesa API, with refresh and retry"""
        global access_token, token_expiry

        # If token is still valid, return it
        if access_token and time.time() < token_expiry:
            return access_token

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {base64.b64encode((CONSUMER_KEY + ":" + CONSUMER_SECRET).encode()).decode()}'
        }

        for attempt in range(3):
            try:
                response = requests.get(ACCESS_TOKEN_URL, headers=headers, timeout=10)
                response.raise_for_status()
                result = response.json()
                access_token = result.get('access_token', '')
                expires_in = int(result.get('expires_in', 0))
                token_expiry = time.time() + expires_in - 60  # Refresh 1 min before actual expiry
                logger.info("M-Pesa access token retrieved")
                return access_token
            except (requests.RequestException, json.JSONDecodeError) as e:
                logger.warning("Attempt %d: Failed to get access token: %s", attempt + 1, e)
                time.sleep(1)

        raise RuntimeError("Could not retrieve M-Pesa access token after retries")

    @staticmethod
    def initiate_payment(account, amount, phone, package, package_code):
        """Initiate STK push payment, with token refresh and retry"""
        token = MpesaHelper.get_access_token()  # ensures valid token

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        payload = {
            "BusinessShortCode": SHORTCODE,
            "Password": PASSWORD,
            "Timestamp": TIMESTAMP,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": SHORTCODE,
            "PhoneNumber": phone,
            "CallBackURL": CALLBACK_URL,
            "AccountReference": "TERALINKX WAVES",
            "TransactionDesc": f"Payment for {package}",
            "Items": [{
                "package": package,
                "price": amount,
                "package_code": package_code,
                "phoneNumber": phone
            }]
        }

        for attempt in range(3):
            try:
                response = requests.post(PAYMENT_URL, headers=headers, json=payload, timeout=15)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                logger.warning("STK push attempt %d failed: %s", attempt + 1, e)
                if attempt == 2:
                    raise
                time.sleep(1)



class QueueHelper:
    """Handles queue operations"""
    
    @staticmethod
    def create_queue_record(package_code, initiator, checkout_id, recipient, package, price, used_credit):
        """Create a new queue record for pending transactions"""
        return Queue.objects.create(
            package_code=package_code,
            initiator=initiator,
            checkout_request_id=checkout_id,
            recipient=recipient,
            package=package,
            price=price,
            status='Pending...',
            method='mpesa',
            used_credit=used_credit
        )

    @staticmethod
    def get_pending_record(checkout_id):
        """
        Returns a pending Queue record based on:
        - initiator + amount
        - OR checkout_request_id as fallback
        """
       
        #First try finding by checkout_request_id
        if checkout_id:
            print(f"Searching for pending record with checkout_request_id: {checkout_id}")
            try:
                return Queue.objects.get(
                    checkout_request_id=checkout_id,
                    status='Pending...'
                )
            except Queue.DoesNotExist:
                pass
        
        
        return None  # No matching record found

    @staticmethod
    def delete_pending_records(initiator, amount):
        """Delete pending queue records"""
        Queue.objects.filter(initiator=initiator, price=amount, status='Pending...').delete()

    @staticmethod
    def mark_as_processed(queue_record):
        """Mark queue record as complete"""
        queue_record.status = 'success'
        queue_record.save()


class VoucherHelper:
    """Handles voucher operations"""
    
    @staticmethod
    def activate_voucher(package_code, mpesa_receipt):
        """Activate a voucher using the generate module"""
        from .generate import activate_voucher
        from .views.chekout_confirmation import get_device_by_package_code
        pkginst = get_device_by_package_code(package_code)

        return activate_voucher(prefix=mpesa_receipt, profile=package_code,devices=pkginst.devices)

    @staticmethod
    def get_available_voucher(package_code):
        """Get an available voucher for the given package"""
        return AvailableVoucher.objects.filter(package_code=package_code).first()

    @staticmethod
    def create_dispatch_record(account, voucher_code, package, package_code, duration, price, devices):
        """Create a dispatch voucher record"""
        return DispatchVoucher.objects.create(
            dispatch_account=account,
            dispatch_voucher_code=voucher_code,
            dispatch_package=package,
            dispatch_package_code=package_code,
            dispatch_package_duration=duration,
            dispatch_status='active',
            dispatch_price=str(price),
            dispatch_devices=str(devices)
        )

    @staticmethod
    def check_active_vouchers(account):
        """Check if account has active vouchers"""
        return DispatchVoucher.objects.filter(dispatch_account=account, dispatch_status='active').exists()


import logging
from django.db import IntegrityError, DatabaseError

logger = logging.getLogger(__name__)

class TransactionHelper:
    """Handles transaction operations"""

    @staticmethod
    def create_or_update_transaction_from_result(merchant_id, checkout_id, result_code, result_desc,
                amount, mpesa_receipt, initiator, balance, transaction_date):
        """
        Create a transaction entry from STK result data.
        Only fills what is available at this stage.
        Logs errors instead of failing silently.
        """
        try:
            if result_code != 0:
                logger.info("📦 Skipping transaction creation: ResultCode is not '0'")
                return

            if not merchant_id or not checkout_id:
                logger.warning("⚠️ Missing MerchantRequestID or CheckoutRequestID in result: %s", checkout_id)
                return

            # Avoid duplicates
            if Transaction.objects.filter(checkout_request_id=checkout_id).exists():
                logger.info("🔁 Transaction already exists for CheckoutRequestID: %s", checkout_id)
                return

            # Create transaction
            Transaction.objects.create(
                merchant_request_id=merchant_id,
                checkout_request_id=checkout_id,
                result_code=result_code,
                result_desc=result_desc,
                amount=amount,              
                transaction_id=mpesa_receipt,        
                initiator= initiator,             
                balance=balance,             
                date=transaction_date                
            )

            logger.info("✅ Transaction created for CheckoutRequestID: %s", checkout_id)

        except IntegrityError as e:
            logger.error("🚨 Integrity error while creating transaction: %s", str(e))
        except DatabaseError as e:
            logger.error("🛑 Database error while creating transaction: %s", str(e))
        except Exception as e:
            logger.exception("🔥 Unexpected error during transaction creation: %s", str(e))

class NotificationHelper:
    """Handles all notification operations"""
    
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
            logger.error("Room %s does not exist", room_name)
            return False

    @staticmethod
    def send_voucher_notification(recipient, voucher_code, package):
        """Send voucher notification to recipient"""
        success = NotificationHelper.send_websocket_message(
            recipient, 
            'system', 
            '🎉 Congratulations! Your purchase was successful. 🎉'
        )
        
        if success:
            NotificationHelper.send_websocket_message(
                recipient,
                'system',
                f'🎉 Your voucher for {package} is: {voucher_code}'
            )
        return success


class PaymentAPIView(APIView):
    """Handles payment initiation"""
    
    def post(self, request):
        load = request.data
        t_account = re.findall(r'\d+', load.get('account'))
        target_account = ''.join(t_account)
        items = load.get('Items', [])
        item = items[0] if items else {}
        amount = load.get('Amount')
        phone = load.get('PhoneNumber')
        package = item.get('package')
        package_code = item.get('package_code')
        used_credit = load.get('UsedBalance')

        # Initiate payment
        response = MpesaHelper.initiate_payment(
            target_account, amount, phone, package, package_code
        )

        print(response)
        queue_record = QueueHelper.create_queue_record(
            package_code=package_code,
            initiator=phone,
            checkout_id=response.get('CheckoutRequestID'),
            recipient=target_account,
            package=package,
            price=amount,
            used_credit=used_credit
        )

        try:
            user_id = int(load.get('ping'))
            user = User.objects.get(id=user_id)
        except (TypeError, ValueError, User.DoesNotExist):
            user = None

        if user:
            if response.get('ResponseCode') == '0':
               create_and_notify(user, " 🎉 Payment initiated successfully","success")
            else:
               create_and_notify(user, " ❌ Payment initiation failed. Please try again.","error")
        else:
            print("No valid user found for notification.")


        return Response({ "checkout_id": response.get('CheckoutRequestID')}, status=status.HTTP_200_OK   )


class ProcessCallback(APIView):
    """Handles M-Pesa callback processing"""
    permission_classes = [AllowAny]

    def post(self, request):
        stk_callback_response = request.data
        logger.info("Callback Response: %s", stk_callback_response)
        
        stk_callback = stk_callback_response.get('Body', {}).get('stkCallback', {})
        if not stk_callback:
            return Response({'error': 'stkCallback not found'}, status=status.HTTP_400_BAD_REQUEST)

        merchant_id = stk_callback.get('MerchantRequestID', 'unknown')
        checkout_id = stk_callback.get('CheckoutRequestID', 'unknown')
        result_code = stk_callback.get('ResultCode', -1)
        result_desc = stk_callback.get('ResultDesc', 'unknown')
        callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])

        if len(callback_metadata) < 5:
            return Response({'error': 'Insufficient metadata items'}, status=status.HTTP_400_BAD_REQUEST)

        amount = callback_metadata[0].get('Value', 0)
        mpesa_receipt = callback_metadata[1].get('Value', 'unknown')
        balance = callback_metadata[2].get('Value', 0)
        transaction_date = callback_metadata[3].get('Value', 'unknown')
        initiator = callback_metadata[4].get('Value', 'unknown')

        if result_code == 0:
            return self.handle_success(
                merchant_id, checkout_id, result_code, result_desc,
                amount, mpesa_receipt, initiator, balance, transaction_date
            )
        elif result_code in [1, 1032, 1037, 2001]:
            return self.handle_failure(checkout_id, result_code)
        else:
            return Response({'message': 'Unknown result code'}, status=status.HTTP_400_BAD_REQUEST)

    def handle_success(self, merchant_id, checkout_id, result_code, result_desc,
                      amount, mpesa_receipt, initiator, balance, transaction_date):
        """Handle successful transaction"""
        try:
            TransactionHelper.create_or_update_transaction_from_result(
                merchant_id, checkout_id, result_code, result_desc,
                amount, mpesa_receipt, initiator, balance, transaction_date
            )
            
            queue_record = QueueHelper.get_pending_record(checkout_id)
            if not queue_record:
                return Response({'message': 'Transaction logged successfully'}, status=status.HTTP_200_OK )

            #self.process_queue_record(queue_record, mpesa_receipt, initiator, amount)
          
            
            return Response({'message': 'Transaction logged successfully'},status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Error processing successful transaction: %s", e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def process_queue_record(self, queue_record, mpesa_receipt, initiator, amount):
        """Process a single queue record"""
        package_code = queue_record.package_code.strip()
        recipient = queue_record.recipient.strip()
        used_credit = queue_record.used_credit
        devices = 1

        # Try to activate voucher
        activated_voucher = VoucherHelper.activate_voucher(package_code, mpesa_receipt)
        
        if activated_voucher.get("status") == "activated":
            self.handle_activated_voucher(activated_voucher, package_code, recipient, queue_record)
        else:
            self.handle_available_voucher(package_code, recipient, queue_record)

        # Update client balance and perform auto-login
        self.update_client_balance(recipient, used_credit,amount)
        self.perform_auto_login(recipient, package_code)
        
        # Clean up
        QueueHelper.mark_as_processed(queue_record)
        QueueHelper.delete_pending_records(initiator, amount)
        update_active_users()

    def handle_activated_voucher(self, activated_voucher, package_code, recipient, queue_record):
        """Handle successfully activated voucher"""
        voucher_code = activated_voucher["voucher_code"]
        package = Package.objects.get(package_code=package_code)
        
        VoucherHelper.create_dispatch_record(
            account=recipient,
            voucher_code=voucher_code,
            package=package.package,
            package_code=package_code,
            duration=package.package_duration,
            price=package.price,
            devices=package.devices
        )

        NotificationHelper.send_voucher_notification(recipient, voucher_code, queue_record.package)

    def handle_available_voucher(self, package_code, recipient, queue_record):
        """Handle available voucher"""
        available_voucher = VoucherHelper.get_available_voucher(package_code)
        if not available_voucher:
            raise Exception('No available voucher found')

        package = Package.objects.get(package_code=available_voucher.package_code)
        
        VoucherHelper.create_dispatch_record(
            account=recipient,
            voucher_code=available_voucher.voucher_code,
            package=available_voucher.package,
            package_code=available_voucher.package_code,
            duration=available_voucher.duration,
            price=available_voucher.price,
            devices=package.devices
        )

        NotificationHelper.send_voucher_notification(
            recipient, 
            available_voucher.voucher_code, 
            queue_record.package
        )
        available_voucher.delete()

    def update_client_balance(self, recipient, used_credit,amount):
        """Update client balance after successful purchase"""
        if used_credit:
            try:
                client = ClientH.objects.get(account=recipient, status__in=['bound', 'active'])
                client.balance -= used_credit
                client.save()
            except ClientH.DoesNotExist:
                logger.error("Client %s is not bound or does not exist", recipient)
                raise Exception('Client is not bound or does not exist')
        else:
            try:
                client = ClientH.objects.get(account=recipient, status__in=['bound', 'active'])
                client.balance += amount
                client.save()
            except ClientH.DoesNotExist:
                logger.error("Client %s is not bound or does not exist", recipient)
                raise Exception('Client is not bound or does not exist')



    def perform_auto_login(self, recipient, package_code):
        """Perform automatic login for the client"""
        from .authentications import validate_voucher, who, TeralinkxWaves, how
        from .models import DHCPLease
        
        try:
            client = ClientH.objects.get(account=recipient)
            current_ip = client.current_ip_address
            
            # Get the latest voucher for this account
            voucher = DispatchVoucher.objects.filter(
                dispatch_account=recipient,
                dispatch_package_code=package_code
            ).latest('dispatch_time')
            
            is_valid, _ = validate_voucher(recipient, voucher.dispatch_voucher_code)
            if not is_valid:
                raise Exception('Voucher validation failed')
            
            router = Api(TeralinkxWaves, user=who, password=how, port=8728, verbose=True)
            router.talk(f'/ip/hotspot/active/login =user={voucher.dispatch_voucher_code} =ip={current_ip}')
            logger.info("Auto-login successful for %s", recipient)
        except Exception as e:
            logger.error("Auto-login failed for %s: %s", recipient, e)
            raise

    def handle_failure(self, checkout_id, result_code):
        """Handle failed transaction"""
        last_9_digits = checkout_id[-9:]
        phone = '254' + last_9_digits
        latest_record = Queue.objects.filter(initiator=phone, status='Pending...').order_by('-queue_time').first()
        
        if not latest_record:
            return Response({'message': 'No matching records found'}, status=status.HTTP_404_NOT_FOUND)

        message = 'Payment failed! You have insufficient funds' if result_code == 1 else 'Payment failed! Please try again.'
        NotificationHelper.send_websocket_message(latest_record.recipient, 'system', message)
        
        return Response({'message': 'Failure handled'})