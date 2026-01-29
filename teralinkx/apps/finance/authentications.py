# apps/authentications.py
import logging
import time
from typing import Dict, Optional, Tuple

from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

from packages.models import DispatchVoucher
from users.models import ClientH, UserDevice, UserSession
from locations.models import Location

# Import librouteros
import librouteros
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


# ============================================================================
# ROUTER CONFIGURATION
# ============================================================================

class RouterConfig:
    """Router configuration manager"""
    
    # Default configuration (should be moved to environment variables)
    DEFAULT_CONFIG = {
        'host': '192.168.88.1',
        'username': 'admin',
        'password': 'q',
        'port': 8728,
        'ssl': False,
        'timeout': 10
    }
    
    @classmethod
    def get_config(cls, location: Optional[Location] = None) -> Dict:
        """
        Get router configuration, optionally based on location
        
        Args:
            location: Optional Location object to get location-specific config
        
        Returns:
            Dictionary with router configuration
        """
        config = cls.DEFAULT_CONFIG.copy()
        
        # Override with location-specific configuration if available
        if location and hasattr(location, 'router_config'):
            # Assuming Location model has router_config JSONField
            location_config = location.router_config or {}
            config.update(location_config)
        
        # Override with environment variables
        import os
        config.update({
            'host': os.getenv('ROUTER_HOST', config['host']),
            'username': os.getenv('ROUTER_USER', config['username']),
            'password': os.getenv('ROUTER_PASSWORD', config['password']),
            'port': int(os.getenv('ROUTER_PORT', config['port'])),
            'ssl': os.getenv('ROUTER_SSL', 'False').lower() == 'true',
        })
        
        return config


class RouterManager:
    """Clean and robust RouterOS connection manager"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or RouterConfig.get_config()
        self.connection = None
        # Remove: self._api_version = None
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception)
    )
    def connect(self):
        """Connect to RouterOS API"""
        try:
            if self.config.get('ssl', False):
                self.connection = librouteros.connect(
                    host=self.config['host'],
                    username=self.config['username'],
                    password=self.config['password'],
                    port=self.config['port'],
                    use_ssl=True,
                    timeout=self.config.get('timeout', 10)
                )
            else:
                self.connection = librouteros.connect(
                    host=self.config['host'],
                    username=self.config['username'],
                    password=self.config['password'],
                    port=self.config['port'],
                    timeout=self.config.get('timeout', 10)
                )
            
            logger.info(f"Connected to RouterOS at {self.config['host']}:{self.config['port']}")
            return True
            
        except Exception as e:
            logger.error(f"Connection failed to {self.config['host']}: {e}")
            raise ConnectionError(f"RouterOS connection failed: {str(e)}")
    
    def disconnect(self):
        """Disconnect from RouterOS"""
        if self.connection:
            try:
                self.connection.close()
                logger.debug("Disconnected from RouterOS")
            except Exception as e:
                logger.warning(f"Error disconnecting: {e}")
            finally:
                self.connection = None
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
    
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type(Exception)
    )
    def execute_command(self, path: str, command: str = None, **kwargs) -> list:
        """
        Universal RouterOS command execution
        
        Works with all RouterOS commands:
        - /system/identity
        - /interface print
        - /ip/hotspot/active login user=xxx ip=xxx
        - /ip/hotspot/active/login user=xxx ip=xxx
        """
        if not self.connection:
            self.connect()
        
        try:
            api_path = self.connection.path(path)
            
            if command:
                # Standard command execution
                return list(api_path(command, **kwargs))
            else:
                # No command specified - try calling directly
                # This handles cases like /ip/hotspot/active/login
                try:
                    return list(api_path(**kwargs))
                except TypeError:
                    # Some paths need an empty command string
                    return list(api_path('', **kwargs))
            
        except Exception as e:
            logger.error(f"Command execution error for {path} {command}: {e}")
            raise RuntimeError(f"Command execution failed: {str(e)}")
    
    # ============================================================================
    # CONVENIENCE METHODS FOR COMMON OPERATIONS
    # ============================================================================
    
    def hotspot_login(self, username: str, ip_address: str) -> bool:
        """Convenience method for hotspot login"""
        try:
            # Try the most reliable pattern first
            self.execute_command(
                path='/ip/hotspot/active',
                command='login',
                user=username,
                ip=ip_address
            )
            return True
        except Exception as e:
            logger.error(f"Hotspot login failed: {e}")
            return False
    
    def hotspot_logout(self, session_id: str = None, mac_address: str = None, ip_address: str = None) -> bool:
        """Convenience method for hotspot logout"""
        try:
            if session_id:
                self.execute_command(
                    path='/ip/hotspot/active',
                    command='remove',
                    numbers=session_id
                )
                return True
            elif mac_address or ip_address:
                # Find session first
                sessions = self.execute_command(
                    path='/ip/hotspot/active',
                    command='print'
                )
                
                for session in sessions:
                    sess_mac = session.get('mac-address', '')
                    sess_ip = session.get('address', '')
                    
                    if (mac_address and sess_mac.lower() == mac_address.lower()) or \
                       (ip_address and sess_ip == ip_address):
                        self.execute_command(
                            path='/ip/hotspot/active',
                            command='remove',
                            numbers=session.get('.id')
                        )
                        return True
            return False
        except Exception as e:
            logger.error(f"Hotspot logout failed: {e}")
            return False
    
    def get_active_sessions(self) -> list:
        """Get all active hotspot sessions"""
        try:
            return self.execute_command(
                path='/ip/hotspot/active',
                command='print'
            )
        except Exception as e:
            logger.error(f"Failed to get active sessions: {e}")
            return []
    
    def get_system_info(self) -> dict:
        """Get system information"""
        try:
            identity = self.execute_command('/system/identity')
            resource = self.execute_command('/system/resource')
            
            return {
                'identity': identity[0] if identity else {},
                'resource': resource[0] if resource else {},
                'version': resource[0].get('version') if resource else 'unknown'
            }
        except Exception as e:
            logger.error(f"Failed to get system info: {e}")
            return {}
    
    def create_hotspot_user(self, username: str, password: str, profile: str = 'default') -> bool:
        """Create hotspot user"""
        try:
            self.execute_command(
                path='/ip/hotspot/user',
                command='add',
                name=username,
                password=password,
                profile=profile,
                disabled='no'
            )
            return True
        except Exception as e:
            logger.error(f"Failed to create hotspot user: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test if connection is working"""
        try:
            self.execute_command('/system/identity')
            return True
        except:
            return False

# ============================================================================
# VOUCHER VALIDATION
# ============================================================================

def validate_voucher(account: str, voucher_code: str) -> Tuple[bool, Optional[Response]]:
    """
    Validate voucher against the new DispatchVoucher model
    
    Args:
        account: Client account number
        voucher_code: Voucher code to validate
    
    Returns:
        Tuple of (is_valid, response)
    """
    try:
        # Get client
        client = ClientH.objects.get(account=account)
        
        # Find active voucher for this client
        voucher = DispatchVoucher.objects.filter(
            user=client.user,
            voucher_code=voucher_code,
            status='active'
        ).first()
        
        if not voucher:
            logger.warning(f"Voucher {voucher_code} not found or not active for account {account}")
            return False, Response(
                {'error': 'Voucher not found or not active'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if voucher is still valid
        if not voucher.is_active:
            logger.warning(f"Voucher {voucher_code} is no longer active")
            voucher.status = 'expired' if voucher.expires_at < timezone.now() else 'exhausted'
            voucher.save()
            
            return False, Response(
                {'error': f'Voucher is {voucher.status}'},
                status=status.HTTP_410_GONE
            )
        
        # Check if voucher is associated with the right client
        if voucher.user != client.user:
            logger.warning(f"Voucher {voucher_code} belongs to different user")
            return False, Response(
                {'error': 'Voucher does not belong to this account'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        logger.info(f"Voucher {voucher_code} validated successfully for account {account}")
        
        # Update last used timestamp (could add a field for this)
        voucher.save()  # Just save to update modified_at
        
        return True, None
        
    except ClientH.DoesNotExist:
        logger.error(f"Client account {account} not found")
        return False, Response(
            {'error': 'Account not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Voucher validation error for {account}/{voucher_code}: {e}")
        return False, Response(
            {'error': 'Voucher validation failed'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def validate_device_access(client: ClientH, mac_address: str = None, ip_address: str = None) -> Tuple[bool, Optional[str]]:
    """
    Validate if device can access the network
    
    Args:
        client: ClientH object
        mac_address: Optional device MAC address
        ip_address: Optional IP address
    
    Returns:
        Tuple of (is_allowed, error_message)
    """
    try:
        # Check if device is allowed for this client
        if mac_address:
            # Check if device exists and is active
            device = UserDevice.objects.filter(
                user=client,
                mac_address=mac_address,
                status='active'
            ).first()
            
            if not device:
                return False, "Device not registered or inactive"
            
            # Check if device is trusted
            if not device.is_trusted:
                return False, "Device requires authorization"
        
        # Check client account status
        if client.status != 'active':
            return False, f"Account is {client.status}"
        
        # Check if client has valid voucher
        if not client.active_voucher:
            return False, "No active voucher"
        
        # Validate active voucher
        try:
            voucher = DispatchVoucher.objects.get(
                voucher_code=client.active_voucher,
                status='active',
                user=client.user
            )
            
            if not voucher.is_active:
                return False, "Active voucher has expired or exhausted"
                
        except DispatchVoucher.DoesNotExist:
            return False, "Active voucher not found"
        
        return True, None
        
    except Exception as e:
        logger.error(f"Device access validation error: {e}")
        return False, "Device validation failed"


# ============================================================================
# HOTSPOT AUTHENTICATION VIEWS
# ============================================================================

class ConnectAPIView(APIView):
    """
    Connect device to hotspot with voucher authentication
    
    Expected POST data:
    - account: Client account number
    - voucher_code: Voucher code
    - mac_address: Device MAC address (optional)
    - ip_address: Device IP address (optional)
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        account = request.data.get('account')
        voucher_code = request.data.get('voucher_code')
        mac_address = request.data.get('mac_address')
        ip_address = request.data.get('ip_address')
        
        # Validate required fields
        if not all([account, voucher_code]):
            return Response(
                {'error': 'Account and voucher code are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logger.info(f"Connect request - Account: {account}, Voucher: {voucher_code}")
        
        # Step 1: Validate voucher
        is_valid, error_response = validate_voucher(account, voucher_code)
        if not is_valid:
            return error_response
        
        try:
            # Get client
            client = ClientH.objects.get(account=account)
            
            # Step 2: Validate device access
            if mac_address or ip_address:
                allowed, error_msg = validate_device_access(client, mac_address, ip_address)
                if not allowed:
                    return Response(
                        {'error': error_msg},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            # Step 3: Get actual IP address
            actual_ip = ip_address
            if not actual_ip:
                # Try to get from client's current session
                active_session = UserSession.objects.filter(
                    user=client,
                    is_active=True
                ).order_by('-last_activity').first()
                
                if active_session:
                    actual_ip = active_session.ip_address
                else:
                    # Fallback to client's current IP
                    actual_ip = client.current_ip_address
            
            if not actual_ip:
                return Response(
                    {'error': 'IP address not found'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Step 4: Perform hotspot login
            router_config = RouterConfig.get_config(client.current_location)
            
            with RouterManager(router_config) as router:
                result = router.execute_command(
                    path='/ip/hotspot/active',
                    command='login',
                    user=voucher_code,
                    ip=actual_ip
                )
                
                logger.info(f"Hotspot login successful - Account: {account}, IP: {actual_ip}")
                
                # Step 5: Update client's active voucher if different
                if client.active_voucher != voucher_code:
                    client.active_voucher = voucher_code
                    
                    # Update voucher expiry
                    voucher = DispatchVoucher.objects.get(voucher_code=voucher_code)
                    client.voucher_expiry = voucher.expires_at
                    client.save()
                
                # Step 6: Create or update device session
                if mac_address:
                    device, _ = UserDevice.objects.get_or_create(
                        mac_address=mac_address,
                        defaults={
                            'user': client,
                            'device_name': f"{client.display_name}'s Device",
                            'device_type': 'other'
                        }
                    )
                    
                    # Update device presence
                    device.update_presence(
                        ip_address=actual_ip,
                        location=client.current_location
                    )
                    
                    # Create session
                    UserSession.objects.create(
                        user=client,
                        device=device,
                        session_id=f"hs_{int(time.time())}",
                        ip_address=actual_ip,
                        location=client.current_location,
                        session_type='hotspot_login',
                        active_voucher=voucher_code,
                        voucher_expires=voucher.expires_at if 'voucher' in locals() else None
                    )
                
                return Response({
                    'status': 'connected',
                    'message': 'Device connected successfully',
                    'ip_address': actual_ip,
                    'voucher': voucher_code,
                    'account': account
                }, status=status.HTTP_200_OK)
                
        except ClientH.DoesNotExist:
            return Response(
                {'error': 'Account not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Connection error: {e}", exc_info=True)
            return Response(
                {'error': 'Connection failed', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ReconnectAPIView(APIView):
    """
    Reconnect device to hotspot
    
    Expected POST data:
    - account: Client account number
    - voucher_code: Voucher code (optional, uses active voucher if not provided)
    - ip_address: Device IP address (required)
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        account = request.data.get('account')
        voucher_code = request.data.get('voucher_code')
        ip_address = request.data.get('ip_address')
        
        if not account or not ip_address:
            return Response(
                {'error': 'Account and IP address are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logger.info(f"Reconnect request - Account: {account}, IP: {ip_address}")
        
        try:
            client = ClientH.objects.get(account=account)
            
            # Use provided voucher_code or client's active voucher
            actual_voucher = voucher_code or client.active_voucher
            if not actual_voucher:
                return Response(
                    {'error': 'No voucher available for reconnection'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate voucher
            is_valid, error_response = validate_voucher(account, actual_voucher)
            if not is_valid:
                return error_response
            
            # Get router configuration based on client location
            router_config = RouterConfig.get_config(client.current_location)
            
            # Attempt reconnect with retries
            max_retries = 3
            last_error = None
            
            for attempt in range(1, max_retries + 1):
                try:
                    with RouterManager(router_config) as router:
                        result = router.execute_command(
                            path='/ip/hotspot/active',
                            command='login',
                            user=actual_voucher,
                            ip=ip_address
                        )
                        
                        logger.info(f"Reconnect successful (attempt {attempt}) - Account: {account}")
                        
                        return Response({
                            'status': 'reconnected',
                            'message': 'Device reconnected successfully',
                            'attempt': attempt,
                            'ip_address': ip_address,
                            'voucher': actual_voucher
                        }, status=status.HTTP_200_OK)
                        
                except Exception as e:
                    last_error = e
                    logger.warning(f"Reconnect attempt {attempt} failed: {e}")
                    
                    if attempt < max_retries:
                        time.sleep(1)  # Wait before retry
                    else:
                        logger.error(f"All reconnect attempts failed for account {account}")
                        return Response(
                            {
                                'error': 'Reconnection failed after 3 attempts',
                                'details': str(last_error)
                            },
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                        )
            
        except ClientH.DoesNotExist:
            return Response(
                {'error': 'Account not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Reconnection error: {e}", exc_info=True)
            return Response(
                {'error': 'Reconnection failed', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DisconnectAPIView(APIView):
    """
    Disconnect device from hotspot
    
    Expected POST data:
    - account: Client account number (optional)
    - mac_address: Device MAC address (required)
    - ip_address: Device IP address (optional)
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]  # Changed from IsAuthenticated to AllowAny for hotspot compatibility
    
    def post(self, request):
        account = request.data.get('account')
        mac_address = request.data.get('mac_address')
        ip_address = request.data.get('ip_address')
        
        if not mac_address:
            return Response(
                {'error': 'MAC address is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logger.info(f"Disconnect request - MAC: {mac_address}, Account: {account}")
        
        try:
            # Get client if account provided
            client = None
            if account:
                client = ClientH.objects.get(account=account)
                router_config = RouterConfig.get_config(client.current_location)
            else:
                # Try to find client by device
                device = UserDevice.objects.filter(mac_address=mac_address).first()
                if device:
                    client = device.user
                    router_config = RouterConfig.get_config(client.current_location)
                else:
                    # Use default config
                    router_config = RouterConfig.get_config()
            
            # Get active session for this device
            active_sessions = []
            if client:
                active_sessions = UserSession.objects.filter(
                    user=client,
                    is_active=True
                )
                
                if ip_address:
                    active_sessions = active_sessions.filter(ip_address=ip_address)
            
            # Find active hotspot session on router
            with RouterManager(router_config) as router:
                # Get active hotspot users
                hotspot_users = router.execute_command(
                    path='/ip/hotspot/active',
                    command='print'
                )
                
                # Find session by MAC or IP
                session_to_remove = None
                for user in hotspot_users:
                    user_mac = user.get('mac-address', '')
                    user_ip = user.get('address', '')
                    user_id = user.get('.id', '')
                    
                    if (mac_address and user_mac.lower() == mac_address.lower()) or \
                       (ip_address and user_ip == ip_address):
                        session_to_remove = user_id
                        break
                
                if not session_to_remove:
                    logger.warning(f"No active hotspot session found for MAC: {mac_address}")
                    # Still mark local sessions as terminated
                    for session in active_sessions:
                        session.terminate(reason="Manual disconnect - no active router session")
                    
                    return Response({
                        'status': 'disconnected',
                        'message': 'No active session found on router'
                    }, status=status.HTTP_200_OK)
                
                # Remove from hotspot
                router.execute_command(
                    path='/ip/hotspot/active',
                    command='remove',
                    numbers=session_to_remove
                )
                
                logger.info(f"Hotspot session removed - ID: {session_to_remove}, MAC: {mac_address}")
            
            # Terminate local sessions
            sessions_terminated = 0
            for session in active_sessions:
                session.terminate(reason="Manual disconnect")
                sessions_terminated += 1
            
            return Response({
                'status': 'disconnected',
                'message': 'Device disconnected successfully',
                'sessions_terminated': sessions_terminated,
                'mac_address': mac_address
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Disconnection error: {e}", exc_info=True)
            return Response(
                {'error': 'Disconnection failed', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SessionStatusAPIView(APIView):
    """
    Get current session status for device
    """
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        mac_address = request.GET.get('mac_address')
        ip_address = request.GET.get('ip_address')
        
        if not mac_address and not ip_address:
            return Response(
                {'error': 'MAC address or IP address required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            client = request.user.client_profile
            
            # Get active sessions
            sessions = UserSession.objects.filter(
                user=client,
                is_active=True
            )
            
            if mac_address:
                sessions = sessions.filter(device__mac_address=mac_address)
            if ip_address:
                sessions = sessions.filter(ip_address=ip_address)
            
            session_data = []
            for session in sessions:
                session_data.append({
                    'session_id': session.session_id,
                    'device_mac': session.device.mac_address if session.device else None,
                    'device_name': session.device.device_name if session.device else None,
                    'ip_address': session.ip_address,
                    'login_time': session.login_time.isoformat(),
                    'last_activity': session.last_activity.isoformat(),
                    'session_type': session.session_type,
                    'active_voucher': session.active_voucher,
                    'voucher_expires': session.voucher_expires.isoformat() if session.voucher_expires else None,
                    'is_expired': session.is_expired,
                    'duration_seconds': session.duration.total_seconds()
                })
            
            # Check router status
            router_config = RouterConfig.get_config(client.current_location)
            hotspot_status = []
            
            try:
                with RouterManager(router_config) as router:
                    hotspot_users = router.execute_command(
                        path='/ip/hotspot/active',
                        command='print'
                    )
                    
                    # Filter for this client's sessions
                    for user in hotspot_users:
                        user_mac = user.get('mac-address', '')
                        user_ip = user.get('address', '')
                        
                        if (mac_address and user_mac.lower() == mac_address.lower()) or \
                           (ip_address and user_ip == ip_address):
                            hotspot_status.append({
                                'user': user.get('user', ''),
                                'mac_address': user_mac,
                                'ip_address': user_ip,
                                'uptime': user.get('uptime', ''),
                                'bytes_in': user.get('bytes-in', ''),
                                'bytes_out': user.get('bytes-out', ''),
                                'server': user.get('server', '')
                            })
            except Exception as e:
                logger.warning(f"Could not check router status: {e}")
            
            return Response({
                'local_sessions': session_data,
                'hotspot_sessions': hotspot_status,
                'has_active_sessions': len(session_data) > 0 or len(hotspot_status) > 0,
                'client_account': client.account,
                'current_location': client.current_location.code if client.current_location else None
            }, status=status.HTTP_200_OK)
            
        except ClientH.DoesNotExist:
            return Response(
                {'error': 'Client profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Session status error: {e}")
            return Response(
                {'error': 'Failed to get session status'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============================================================================
# LEGACY COMPATIBILITY FUNCTIONS
# ============================================================================

# For backward compatibility with old code
def validate_voucher_legacy(account, voucher_code):
    """
    Legacy compatibility function
    
    Returns: (is_valid, response) tuple
    """
    return validate_voucher(account, voucher_code)


# Global variables for backward compatibility (deprecated)
TeralinkxWaves = RouterConfig.DEFAULT_CONFIG['host']
who = RouterConfig.DEFAULT_CONFIG['username']
how = RouterConfig.DEFAULT_CONFIG['password']


# Legacy views for backward compatibility
class Connect(ConnectAPIView):
    """Legacy view name for backward compatibility"""
    pass


class Reconnect(ReconnectAPIView):
    """Legacy view name for backward compatibility"""
    pass


class Disconnect(DisconnectAPIView):
    """Legacy view name for backward compatibility"""
    pass