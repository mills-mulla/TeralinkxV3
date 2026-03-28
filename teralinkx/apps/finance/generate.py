# apps/finance/generate.py
import random
import string
import logging
import time
from typing import Dict, Optional, List
from datetime import datetime

from django.core.cache import cache
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import librouteros

logger = logging.getLogger(__name__)


class RouterOSAPIError(Exception):
    """Custom exception for RouterOS API failures"""
    pass


class RouterOSManager:
    """Manages RouterOS connections using librouteros"""
    
    def __init__(self, host: str = '192.168.88.1', username: str = 'admin', 
                 password: str = 'q', port: int = 8728, ssl: bool = False):
        """
        Initialize RouterOS connection manager
        
        Args:
            host: Router IP address
            username: RouterOS username
            password: RouterOS password
            port: API port (8728 for plain, 8729 for SSL)
            ssl: Use SSL/TLS connection
        """
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.ssl = ssl
        self.connection = None
        self.api = None
        
    def connect(self) -> bool:
        """
        Connect to RouterOS API with explicit timeout to prevent hanging workers.
        """
        import socket
        socket.setdefaulttimeout(5)  # 5s max — router is either up or it isn't
        try:
            if self.ssl:
                self.connection = librouteros.connect(
                    host=self.host,
                    username=self.username,
                    password=self.password,
                    port=self.port,
                    use_ssl=True
                )
            else:
                self.connection = librouteros.connect(
                    host=self.host,
                    username=self.username,
                    password=self.password,
                    port=self.port
                )
            self.api = self.connection
            logger.info(f"Connected to RouterOS at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Connection failed to {self.host}:{self.port}: {e}")
            raise ConnectionError(f"RouterOS connection failed: {str(e)}")
    
    def disconnect(self):
        """Disconnect from RouterOS API"""
        if self.connection:
            try:
                self.connection.close()
                logger.debug("Disconnected from RouterOS")
            except Exception as e:
                logger.warning(f"Error disconnecting from RouterOS: {e}")
            finally:
                self.connection = None
                self.api = None
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
    
    def execute_command(self, path: str, command: str = None, **kwargs) -> List[Dict]:
        """
        Execute RouterOS API command
        
        Args:
            path: API path (e.g., '/user-manager/user')
            command: Command to execute (add, set, remove, print, etc.)
            **kwargs: Additional parameters
        
        Returns:
            List of response dictionaries
        """
        if not self.api:
            self.connect()
        
        try:
            # Prepare the command
            api_path = self.api.path(path)
            
            if command:
                # Execute with command
                result = list(getattr(api_path, command)(**kwargs))
            else:
                # Simple path call
                result = list(api_path(**kwargs))
            
            logger.debug(f"RouterOS command executed: {path} {command} {kwargs}")
            return result
            
        except librouteros.exceptions.TrapError as e:
            logger.error(f"RouterOS trap error for {path} {command}: {e}")
            raise RouterOSAPIError(f"RouterOS error: {str(e)}")
        except Exception as e:  # Catch all other exceptions
            logger.error(f"Error executing {path} {command}: {e}")
            raise RouterOSAPIError(f"Command execution failed: {str(e)}")

def generate_voucher(prefix: str, length: int = 16) -> str:
    """
    Generate a unique voucher code with prefix.
    
    Args:
        prefix: Voucher prefix (e.g., 'QRDSTk')
        length: Total length including prefix and hyphen
    
    Returns:
        Unique voucher code
    """
    if length <= len(prefix) + 1:  # +1 for hyphen
        raise ValueError(f"Total length ({length}) must be greater than prefix length ({len(prefix)}) + 1")
    
    allowed_chars = string.ascii_uppercase + string.digits
    random_part_length = length - len(prefix) - 1  # -1 for hyphen
    
    # Try to generate unique code (max 5 attempts)
    for attempt in range(5):
        random_part = ''.join(random.choices(allowed_chars, k=random_part_length))
        voucher_code = f"{prefix}-{random_part}"
        
        # Check cache for uniqueness (simple deduplication)
        cache_key = f"voucher_generated:{voucher_code}"
        if not cache.get(cache_key):
            cache.set(cache_key, True, timeout=300)  # 5 minutes
            logger.debug(f"Generated unique voucher: {voucher_code}")
            return voucher_code
    
    # If we couldn't generate unique after 5 attempts, use timestamp
    timestamp = str(int(time.time()))[-6:]
    random_part = ''.join(random.choices(allowed_chars, k=random_part_length-6))
    voucher_code = f"{prefix}-{random_part}{timestamp}"
    
    logger.warning(f"Used fallback generation for voucher: {voucher_code}")
    return voucher_code


def parse_devices(devices_input) -> int:
    """
    Convert various device inputs into integer.
    
    Supports:
    - Integer: 1, 2, 3
    - String: '1', '2', '3'
    - String with units: '1 device', '2 devices'
    - PackageType object with device_limit attribute
    
    Defaults to 1 if parsing fails.
    """
    try:
        # If it's already an integer
        if isinstance(devices_input, int):
            return max(1, devices_input)  # Ensure at least 1 device
        
        # If it's a PackageType object
        if hasattr(devices_input, 'device_limit'):
            return max(1, devices_input.device_limit)
        
        # If it's a string
        if isinstance(devices_input, str):
            # Remove non-digit characters and convert
            import re
            digits = re.sub(r'\D', '', devices_input)
            if digits:
                return max(1, int(digits))
        
        # Default fallback
        return 1
        
    except (ValueError, AttributeError, TypeError):
        logger.warning(f"Failed to parse devices from input: {devices_input}, defaulting to 1")
        return 1


def activate_voucher(prefix: str, profile: str, devices, 
                    location: Optional[str] = None,
                    router_config: Optional[Dict] = None) -> Dict[str, str]:
    """
    Activate voucher in RouterOS User Manager using librouteros.
    
    Args:
        prefix: Voucher prefix (e.g., 'QRDSTk')
        profile: RouterOS profile name
        devices: Can be integer, string, or PackageType object
        location: Optional location code for profile selection
        router_config: Optional router configuration override
    
    Returns:
        Dictionary with voucher code and status
    """
    start_time = time.time()
    activation_id = f"ACT_{int(time.time())}_{random.randint(1000, 9999)}"
    
    try:
        # Generate unique voucher code
        voucher = generate_voucher(prefix, length=16)
        
        # Parse device count
        device_count = parse_devices(devices)
        
        logger.info(f"[{activation_id}] Activating voucher: {voucher}, "
                   f"Profile: {profile}, Devices: {device_count}")
        
        # Get router configuration
        config = router_config or {}
        router_host = config.get('host', '192.168.88.1')
        router_user = config.get('user', 'admin')
        router_pass = config.get('password', 'q')
        router_port = config.get('port', 8728)
        router_ssl = config.get('ssl', False)
        
        # Use context manager for automatic connection management
        with RouterOSManager(
            host=router_host,
            username=router_user,
            password=router_pass,
            port=router_port,
            ssl=router_ssl
        ) as router:
            
            # # Step 1: Check if profile exists (optional, but good for debugging)
            # logger.debug(f"[{activation_id}] Checking profile existence: {profile}")
            # try:
            #     profiles = router.execute_command(
            #         path='/user-manager/profile/print',
                    
            #     )
                
            #     # Filter profiles by name
            #     profile_exists = any(p.get('name') == profile for p in profiles)
                
            #     if not profile_exists:
            #         logger.warning(f"[{activation_id}] Profile '{profile}' not found on router")
            #         # You might want to create the profile here or handle this error
            #     else:
            #         logger.info(f"[{activation_id}] Profile '{profile}' exists")
            # except Exception as e:
            #     logger.warning(f"[{activation_id}] Profile check failed: {e}")
            #     # Continue anyway, the router will error if profile doesn't exist
            
            # Step 2: Create voucher user with CORRECT parameter name: shared-users (with hyphen)
            logger.info(f"[{activation_id}] Creating voucher user: {voucher}")
            
            # Prepare user parameters
            user_params = {
                'name': voucher,
                'shared-users': str(device_count),  # CORRECT: with hyphen, as string
                'comment': f"Voucher: {profile}, Devices: {device_count}, Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
            
            # Execute the command
            user_response = router.execute_command(
                path='/user-manager/user',
                command='add',
                **user_params
            )
            
            logger.info(f"[{activation_id}] User created successfully")
            
            # Step 3: Apply profile to the user
            logger.info(f"[{activation_id}] Applying profile '{profile}' to voucher")
            try:
                profile_response = router.execute_command(
                    path='/user-manager/user-profile',
                    command='add',
                    user=voucher,
                    profile=profile
                )
                logger.info(f"[{activation_id}] Profile applied successfully")
            except Exception as e:
                logger.warning(f"[{activation_id}] Failed to apply profile: {e}")
                # This might not be necessary if profile is set during user creation
                # Continue anyway
        
        processing_time = time.time() - start_time
        logger.info(
            f"[{activation_id}] Voucher {voucher} activated successfully. "
            f"Profile: {profile}, Devices: {device_count}, "
            f"Processing time: {processing_time:.2f}s"
        )
        
        # Cache the activation for idempotency and monitoring
        activation_data = {
            'voucher_code': voucher,
            'profile': profile,
            'devices': device_count,
            'activated_at': time.time(),
            'processing_time': processing_time,
            'activation_id': activation_id,
            'router_host': router_host
        }
        cache.set(f"voucher_activated:{voucher}", activation_data, timeout=3600)
        
        # Record success metrics
        cache_key = "voucher_activation_metrics"
        metrics = cache.get(cache_key, {'success': 0, 'failure': 0, 'total_time': 0.0})
        metrics['success'] = metrics.get('success', 0) + 1
        metrics['total_time'] = metrics.get('total_time', 0.0) + processing_time
        cache.set(cache_key, metrics, timeout=86400)  # 24 hours
        
        return {
            "voucher_code": voucher,
            "status": "activated",
            "devices": device_count,
            "profile": profile,
            "processing_time": processing_time,
            "activation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "activation_id": activation_id,
            "router_host": router_host
        }

    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"[{activation_id}] Voucher activation failed: {e}", exc_info=True)
        
        # Record failure metrics
        cache_key = "voucher_activation_metrics"
        metrics = cache.get(cache_key, {'success': 0, 'failure': 0, 'total_time': 0.0})
        metrics['failure'] = metrics.get('failure', 0) + 1
        cache.set(cache_key, metrics, timeout=86400)
        
        return {
            "voucher_code": voucher if 'voucher' in locals() else "FAILED",
            "status": "failed",
            "error": str(e),
            "processing_time": processing_time,
            "activation_id": activation_id
        }

def get_voucher_info(voucher_code: str, router_config: Optional[Dict] = None) -> Optional[Dict]:
    """
    Get information about an existing voucher from RouterOS.
    
    Args:
        voucher_code: Voucher code to query
        router_config: Optional router configuration
    
    Returns:
        Dictionary with voucher info or None if not found
    """
    try:
        config = router_config or {}
        
        with RouterOSManager(
            host=config.get('host', '192.168.88.1'),
            username=config.get('user', 'admin'),
            password=config.get('password', 'q'),
            port=config.get('port', 8728),
            ssl=config.get('ssl', False)
        ) as router:
            
            # Get user info
            users = router.execute_command(
                path='/user-manager/user',
                command='print',
                where={'name': voucher_code}
            )
            
            if not users:
                logger.debug(f"Voucher {voucher_code} not found on router")
                return None
            
            user_info = users[0]
            
            # Get profile info
            profiles = router.execute_command(
                path='/user-manager/user/profile',
                command='print',
                where={'user': voucher_code}
            )
            
            profile_names = [p.get('profile', '') for p in profiles] if profiles else []
            
            # Get session info
            sessions = router.execute_command(
                path='/user-manager/user/active',
                command='print',
                where={'user': voucher_code}
            )
            
            return {
                'voucher_code': voucher_code,
                'shared_users': user_info.get('shared-users', '1'),
                'disabled': user_info.get('disabled', 'false') == 'true',
                'comment': user_info.get('comment', ''),
                'profiles': profile_names,
                'active_sessions': len(sessions),
                'last_logged_in': user_info.get('last-logged-in', ''),
                'uptime': user_info.get('uptime', '')
            }
            
    except Exception as e:
        logger.error(f"Failed to get info for voucher {voucher_code}: {e}")
        return None


def disable_voucher(voucher_code: str, router_config: Optional[Dict] = None) -> bool:
    """
    Disable a voucher on RouterOS.
    
    Args:
        voucher_code: Voucher code to disable
        router_config: Optional router configuration
    
    Returns:
        bool: True if disabled successfully
    """
    try:
        config = router_config or {}
        
        with RouterOSManager(
            host=config.get('host', '192.168.88.1'),
            username=config.get('user', 'admin'),
            password=config.get('password', 'q'),
            port=config.get('port', 8728),
            ssl=config.get('ssl', False)
        ) as router:
            
            router.execute_command(
                path='/user-manager/user',
                command='set',
                numbers=voucher_code,
                disabled='yes'
            )
            
            logger.info(f"Voucher {voucher_code} disabled successfully")
            return True
            
    except Exception as e:
        logger.error(f"Failed to disable voucher {voucher_code}: {e}")
        return False


def validate_voucher_format(voucher_code: str) -> bool:
    """
    Validate voucher code format.
    
    Expected format: PREFIX-RANDOMPART (e.g., QRDSTk-ABC123DEF456)
    """
    if not voucher_code or '-' not in voucher_code:
        return False
    
    try:
        prefix, random_part = voucher_code.split('-', 1)
        
        # Check prefix is alphanumeric and not too long
        if not prefix.isalnum() or len(prefix) < 3 or len(prefix) > 10:
            return False
        
        # Check random part is alphanumeric uppercase
        if not random_part.isalnum() or not random_part.isupper():
            return False
        
        # Check total length
        if len(voucher_code) < 10 or len(voucher_code) > 25:
            return False
        
        return True
        
    except Exception:
        return False


def get_activation_metrics() -> Dict:
    """
    Get voucher activation metrics.
    
    Returns:
        Dictionary with activation statistics
    """
    cache_key = "voucher_activation_metrics"
    metrics = cache.get(cache_key, {'success': 0, 'failure': 0, 'total_time': 0.0})
    
    success = metrics.get('success', 0)
    failure = metrics.get('failure', 0)
    total = success + failure
    
    if total > 0:
        success_rate = (success / total) * 100
        avg_time = metrics.get('total_time', 0.0) / total if success > 0 else 0.0
    else:
        success_rate = 0.0
        avg_time = 0.0
    
    return {
        'total_attempts': total,
        'successful': success,
        'failed': failure,
        'success_rate_percent': round(success_rate, 2),
        'average_processing_time_seconds': round(avg_time, 2),
        'last_updated': datetime.now().isoformat()
    }


# Legacy function for backward compatibility
def simple_activate_voucher(prefix, profile, devices):
    """
    Simple wrapper for backward compatibility.
    Converts old-style parameters to new format.
    """
    return activate_voucher(
        prefix=prefix,
        profile=profile,
        devices=devices,
        location=None,
        router_config=None
    )