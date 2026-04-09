from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from packages.models import DispatchVoucher
from analytics.models import ActiveSession
from librouteros import connect
from librouteros.exceptions import ConnectionError, TrapError
import time
import logging

logger = logging.getLogger(__name__)

# Router configuration
ROUTER_CONFIG = {
    'host': '192.168.88.12',
    'username': 'admin',
    'password': 'q',
    'port': 8728
}

class RouterManager:
    """router connection manager"""
    
    @staticmethod
    def get_connection():
        """Get RouterOS connection"""
        try:
            return connect(**ROUTER_CONFIG)
        except (ConnectionError, TrapError) as e:
            logger.error(f"Router connection failed: {e}")
            raise Exception(f"Router connection failed: {str(e)}")

class VoucherManager:
    """Handle voucher validation"""
    
    @staticmethod
    def validate_voucher(account, voucher_code):
        """Validate voucher and return status"""
        try:
            voucher = DispatchVoucher.objects.get(
                dispatch_account=account, 
                dispatch_voucher_code=voucher_code, 
                dispatch_status__in=['active', 'inactive']
            )
            
            # Activate voucher if inactive
            if voucher.dispatch_status == 'inactive':
                voucher.dispatch_status = 'active'
                voucher.save()
            
            return True, "Voucher is valid"
        except DispatchVoucher.DoesNotExist:
            return False, "Voucher does not exist"

class NetworkAuthView(APIView):
    """
    Unified network authentication view
    Supports: connect, reconnect, disconnect
    """
    
    def execute_router_command(self, command, params=None, max_retries=3):
        """Execute router command with retry logic"""
        last_error = None
        params = params or {}
        
        for attempt in range(1, max_retries + 1):
            try:
                api = RouterManager.get_connection()
                result = api(cmd=command, **params)
                api.close()
                return result, None
                
            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt} failed: {e}")
                if attempt < max_retries:
                    time.sleep(1)
        
        return None, last_error
    
    def post(self, request):
        action = request.data.get('action')  # connect, reconnect, disconnect
        
        if not action:
            return Response(
                {'error': 'Missing action parameter'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Route to appropriate handler
        action_handlers = {
            'connect': self.handle_connect,
            'reconnect': self.handle_reconnect, 
            'disconnect': self.handle_disconnect
        }
        
        handler = action_handlers.get(action)
        if not handler:
            return Response(
                {'error': f'Invalid action: {action}. Use connect, reconnect, or disconnect'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return handler(request.data)
    
    def handle_connect(self, data):
        """Handle connection request - router handles IP via DHCP"""
        account = data.get('account')
        voucher_code = data.get('voucher_code')
        bound_mac = data.get('bound_mac')

        # Validate input
        if not all([account, voucher_code, bound_mac]):
            return Response(
                {'error': 'Missing required fields for connect: account, voucher_code, bound_mac'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Validate voucher only - router handles IP assignment
            is_valid, message = VoucherManager.validate_voucher(account, voucher_code)
            if not is_valid:
                return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
            
            # Perform hotspot login - router will assign IP via DHCP
            # Using MAC address to identify the device
            result, error = self.execute_router_command(
                '/ip/hotspot/active/login',
                params={'user': voucher_code, 'mac-address': bound_mac}
            )
            
            if error:
                return Response(
                    {'error': 'Failed to connect to network', 'details': str(error)}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response({
                'success': True, 
                'message': 'Connected successfully - IP will be assigned by router DHCP',
                'action': 'connect',
                'voucher': voucher_code,
                'mac_address': bound_mac
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Connect error: {e}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def handle_reconnect(self, data):
        """Handle reconnection request"""
        account = data.get('account')
        voucher_code = data.get('voucher_code')
        bound_mac = data.get('bound_mac')  # Use MAC instead of IP

        if not all([account, voucher_code, bound_mac]):
            return Response(
                {'error': 'Missing required fields for reconnect: account, voucher_code, bound_mac'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate voucher
        is_valid, message = VoucherManager.validate_voucher(account, voucher_code)
        if not is_valid:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

        # Perform reconnect using MAC address
        result, error = self.execute_router_command(
            '/ip/hotspot/active/login',
            params={'user': voucher_code, 'mac-address': bound_mac}
        )
        
        if error:
            return Response(
                {'error': 'Failed to reconnect to network', 'details': str(error)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({
            'success': True, 
            'message': 'Reconnected successfully',
            'action': 'reconnect'
        }, status=status.HTTP_200_OK)
    
    def handle_disconnect(self, data):
        """Handle disconnection request"""
        bound_mac = data.get('bound_mac')

        if not bound_mac:
            return Response(
                {'error': 'Missing required field for disconnect: bound_mac'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Find active session by MAC address
            active_entry = ActiveSession.objects.get(mac_address=bound_mac)
            active_id = active_entry.idA
            
            # Perform logout using session ID
            result, error = self.execute_router_command(
                '/ip/hotspot/active/remove',
                params={'numbers': active_id}
            )
            
            if error:
                return Response(
                    {'error': 'Failed to disconnect from network', 'details': str(error)}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Remove session from our database
            active_entry.delete()
            
            return Response({
                'success': True, 
                'message': 'Disconnected successfully',
                'action': 'disconnect'
            }, status=status.HTTP_200_OK)
            
        except ActiveSession.DoesNotExist:
            return Response(
                {'error': 'MAC address not found in active sessions'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Disconnect error: {e}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )