import re
import logging
from datetime import timedelta
import uuid
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from core.services.notification_service import create_and_notify
from .models import *
from .daraja import QueueHelper 
from core.router.ros_api.api import Api
from packages.generate import activate_voucher
from analytics.moitoring import get_user_by_name
from .chekout_confirmation import perform_auto_login

logger = logging.getLogger(__name__)


class DurationParser:
    """Utility class for parsing duration strings into timedelta objects."""
    
    @staticmethod
    def parse(duration_str):
        """Parse a duration string into a timedelta object.
        
        Args:
            duration_str (str): Duration string (e.g., "3 days", "24:00:00")
            
        Returns:
            timedelta: Parsed duration or None if parsing fails
        """
        duration_str = duration_str.lower().strip()

        # Try to match day patterns first
        day_match = re.match(r'(\d+)\s*days?', duration_str)
        if day_match:
            return timedelta(days=int(day_match.group(1)))

        # Try to match HH:MM:SS format
        try:
            h, m, s = map(int, duration_str.split(':'))
            return timedelta(hours=h, minutes=m, seconds=s)
        except ValueError:
            return None





class VoucherManager:
    """Manages voucher-related operations."""
    
    @staticmethod
    def check_existing_active_vouchers(recipient):
        """Check if recipient has any active vouchers.
        
        Args:
            recipient (str): Account identifier
            
        Returns:
            bool: True if active vouchers exist
        """
        return DispatchVoucher.objects.filter(
            dispatch_account=recipient, 
            dispatch_status='active'
        ).exists()
    
    @staticmethod
    def create_dispatch_voucher(recipient, voucher_data, device):
        """Create a dispatch voucher record.
        
        Args:
            recipient (str): Account receiving the voucher
            voucher_data (dict): Voucher details
            device: Package or DailyPass object
            
        Returns:
            DispatchVoucher: Created voucher object
        """
        return DispatchVoucher.objects.create(
            dispatch_account = recipient,
            dispatch_voucher_code = voucher_data["voucher_code"],
            dispatch_package = device.package,
            dispatch_package_desc = voucher_data["package_desc"],
            dispatch_package_duration = device.package_duration,
            dispatch_status = 'active',
            dispatch_price = str(device.price),
            dispatch_devices = str(device.devices),
            usermanid = get_user_by_name(voucher_data["voucher_code"])
        )


class AutoLoginService:
    """Handles automatic login functionality."""
    
    @staticmethod
    def perform(client, voucher_code):
        """Perform automatic login for a client.
        
        Args:
            client: ClientH object
            voucher_code (str): Voucher code to use
            
        Returns:
            tuple: (success bool, response data)
        """
        from .authentications import validate_voucher, who, TeralinkxWaves, how
        
        current_ip = client.current_ip_address
        account = client.account
        
        is_valid, response = validate_voucher(account, voucher_code)
        if not is_valid:
            return False, response
        
        try:
            router = Api(TeralinkxWaves, user=who, password=how, port=8728, verbose=True)
            hotspot_login = router.talk(
                f'/ip/hotspot/active/login =user={voucher_code} =ip={current_ip}'
            )
            
            return True, {'answer': 'Auto-login successful.'}
        except Exception as e:
            logger.error("Failed to perform auto-login: %s", e)
            return False, {'error': 'Auto-login failed', 'details': str(e)}


class PackagePurchaseService(APIView):
    """Handles package purchase operations."""
    
    def post(self, request):
        """Process a package purchase request.
        
        Args:
            request: HTTP request object
            
        Returns:
            Response: API response with purchase status
        """
        data = request.data
        client_id = data.get('client_id')
        package_id = data.get('package_id') 
        pass_id = data.get('pass_id')
        ping = data.get('ping')
        hotspot_ip = data.get('hotspot_ip')
        
        client = get_object_or_404(ClientH, account=client_id)
        product, prefix = self._get_product(package_id, pass_id)
        
        if not product:
            return Response(
                {"detail": "Either 'package_id' or 'pass_id' must be provided."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not client.can_afford(product.price):
            return self._handle_insufficient_balance(client, product)

        user = self._get_user_by_id(ping)

        if user:
            create_and_notify(user, "Processing started...", "info")
        else:
            logger.warning(f"No valid user found for notification with ID: {ping}")

        
        return self._process_purchase(client, product, prefix,ping,hotspot_ip)
    
    def _get_product(self, package_id, pass_id):
        """Get the product (Package or DailyPass) based on provided IDs.
        
        Args:
            package_id: Package ID or None
            pass_id: DailyPass ID or None
            
        Returns:
            tuple: (product object, voucher prefix)
        """
        if package_id:
            return get_object_or_404(Package, id=package_id), 'BAL'
        if pass_id:
            return get_object_or_404(DailyPass, id=pass_id), 'DPASS'
        return None, None
    
    def _handle_insufficient_balance(self, client, product):
        """Handle case where client has insufficient balance.
        
        Args:
            client: ClientH object
            product: Package or DailyPass object
            
        Returns:
            JsonResponse: Response with balance details
        """
        new_price = product.price - client.balance
        return JsonResponse({
            'status': 'insufficient_balance',
            'message': 'Insufficient balance to buy the package.',
            'new_price': new_price,
            'used_balance': client.balance
        }, status=status.HTTP_201_CREATED)
    
    def _process_purchase(self, client, product, prefix,ping,hotspot_ip):
        """Process a valid purchase request.
        
        Args:
            client: ClientH object
            product: Package or DailyPass object
            prefix: Voucher prefix string
            
        Returns:
            Response: API response with purchase result
        """
        checkout_request_id = self.generate_checkout_id(client.account, product.id)
        queue_record = self._create_queue_record(client, product,checkout_request_id)
        
        queue_rd = QueueHelper.get_pending_record(checkout_id=checkout_request_id)

        if not queue_rd:
            return Response(
                {'message': 'No matching records found in the queue'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return self._process_voucher_activation(client, product, prefix, queue_record,ping,hotspot_ip)
  

    def generate_checkout_id(self,client_account, product_id):
        unique_suffix = uuid.uuid4().hex[:8]  # Short unique string
        return f"bal_co_{client_account}_{product_id}_{unique_suffix}"
    
    def _create_queue_record(self, client, product,request_id):
        """Create a queue record for the purchase.
        
        Args:
            client: ClientH object
            product: Package or DailyPass object
            
        Returns:
            Queue: Created queue record
        """
        
        return Queue.objects.create(
            checkout_request_id=request_id,
            package_desc=product.package_desc,
            initiator=client.account,
            recipient=client.account,
            package=product.package,
            price=product.price,
            status='Pending...',
            method='balance',
            used_balance=product.price
        )
    
    def _process_voucher_activation(self, client, product, prefix, queue_record,ping,hotspot_ip):
        """Process voucher activation and dispatch.
        
        Args:
            client: ClientH object
            product: Package or DailyPass object
            prefix: Voucher prefix string
            queue_record: Queue record
            
        Returns:
            Response: API response with activation result
        """
        activation_result = activate_voucher(prefix=prefix, profile=product.package_desc,devices=product.devices)
        
        if activation_result.get("status") == "activated":
            return self._handle_activated_voucher(client, product, activation_result, queue_record,ping,hotspot_ip)
        else:
            return self._handle_available_vouchers(client, product, queue_record,ping,hotspot_ip)
    
    def _handle_activated_voucher(self, client, product, activation_result, queue_record,ping,hotspot_ip):
        """Handle successfully activated voucher.
        
        Args:
            client: ClientH object
            product: Package or DailyPass object
            activation_result: Activation result dict
            queue_record: Queue record
            
        Returns:
            Response: API response
        """
        voucher_code = activation_result["voucher_code"]
        
        VoucherManager.create_dispatch_voucher(
            client.account,
            {
                "voucher_code": voucher_code,
                "package_desc": product.package_desc
            },
            product
        )
        
        self._send_notifications(ping, f'🎉 Your voucher for {queue_record.package} is: {voucher_code}','success')
        self._send_notifications(ping, 'Processing complete','info' )
        client.deduct_balance(product.price)
        self._update_queue(queue_record, 'processed')

        perform_auto_login(client, voucher_code, hotspot_ip) 
        return Response({'Voucher activated and dispatched successfully'})
    
    def _handle_available_vouchers(self, client, product, queue_record,ping,hotspot_ip):
        """Handle case where we check for available vouchers.
        
        Args:
            client: ClientH object
            product: Package or DailyPass object
            queue_record: Queue record
            
        Returns:
            Response: API response
        """
        available_voucher = AvailableVoucher.objects.filter(
            package_desc=product.package_desc
        ).first()
        
        if not available_voucher:
            self._send_notifications(ping, 'Processing complete','info' )
            self._send_maintenance_notification(product,ping)
            return Response(
                {'message': 'No available voucher found for the given package description'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        self._process_available_voucher(client, product, available_voucher, queue_record,ping,hotspot_ip)
        return Response({'Voucher retrieved and dispatched successfully'})
    
    def _process_available_voucher(self, client, product, available_voucher, queue_record,ping,hotspot_ip):
        """Process an available voucher from the database.
        
        Args:
            client: ClientH object
            product: Package or DailyPass object
            available_voucher: AvailableVoucher object
            queue_record: Queue record
        """
        voucher_status = 'active' if not VoucherManager.check_existing_active_vouchers(
            client.account
        ) else 'inactive'
        
        DispatchVoucher.objects.create(
            dispatch_account=client.account,
            dispatch_voucher_code=available_voucher.voucher_code,
            dispatch_package=available_voucher.package,
            dispatch_package_desc=available_voucher.package_desc,
            dispatch_package_duration=available_voucher.duration,
            dispatch_status=voucher_status,
            dispatch_price=str(available_voucher.price),
            dispatch_devices=str(product.devices)
        )
        
        available_voucher.delete()
        client.deduct_balance(product.price)
        self._send_notifications(ping, 'Processing complete','info' )
        self._update_queue(queue_record, 'processed')

        perform_auto_login(client.account, available_voucher.voucher_code, hotspot_ip) 
        
       
    
    def _send_notifications(self, ping, message, message_type):
        """Send notifications to the user based on their ID.

        Args:
            ping: Account identifier (user ID)
            message: Message content for the notification
            message_type: Type of notification (e.g., 'info', 'error')
        """
        user = self._get_user_by_id(ping)
        if user:
            create_and_notify(user, message, message_type)
        else:
            logger.warning(f"No valid user found for notification with ID: {ping}")

    def _send_maintenance_notification(self, product, ping):
        """Send maintenance notification to the recipient.

        Args:
            product: Package or DailyPass object
            ping: Account identifier (user ID)
        """
        message = (
            f'Your purchase of {product.package} @KES {product.price} was unsuccessful. '
            'The system is undergoing maintenance. Please try again later.'
        )
        message_type = 'error'

        self._send_notifications(ping, message, message_type)

    def _get_user_by_id(self, ping):
        """Retrieve User object by user ID.

        Args:
            ping: Account identifier (user ID)

        Returns:
            User: Corresponding User object or None if not found.
        """
        try:
            user_id = int(ping)
            return User.objects.get(id=user_id)
        except (TypeError, ValueError, User.DoesNotExist):
            return None

    
    def _update_queue(self, queue_record, status):
        """Update queue record status.
        
        Args:
            queue_record: Queue object
            status: New status string
        """
        queue_record.status = status
        queue_record.save()
        
    
    def _perform_auto_login(self, client, voucher_code):
        """Perform automatic login for client.
        
        Args:
            client: ClientH object
            voucher_code: Voucher code string
            
        Returns:
            bool: True if login succeeded
        """

        try:
            if client.status not in ['bound', 'active']:
                return False
                
            success, _ = AutoLoginService.perform(client, voucher_code)
            return success
        except ClientH.DoesNotExist:
            return False
        
class VoucherRenewService(APIView):
    """Handles voucher renewals using existing purchase flow."""

    def post(self, request):
        data = request.data
        voucher_code = data.get("voucher_code")
        ping = data.get("ping")

        # Find expired voucher
        expired = get_object_or_404(DispatchVoucher, dispatch_voucher_code=voucher_code)

        # Map description to package
        try:
            product = Package.objects.get(package_desc=expired.dispatch_package_desc)
        except Package.DoesNotExist:
            return Response(
                {"error": "No matching package found for this voucher."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Reuse purchase flow
        purchase_service = PackagePurchaseService()
        request.data.update({
            "client_id": expired.dispatch_account,
            "package_id": product.id,
            "ping": ping,
        })
        return purchase_service.post(request)
