# core/services/client_service.py
import logging
import traceback  
import uuid
import hashlib
from datetime import timedelta
from typing import Optional, Tuple, Dict, Any, List 
from decimal import Decimal

from django.apps import apps 
from django.contrib.auth.models import User
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

from users.models import ClientH, UserDevice, UserSession
from locations.models import Location
from security.models import SecurityLog
from packages.models import DispatchVoucher
from core.exceptions import (
    BusinessLogicError,
    AuthenticationError,
    DeviceConflictError
)
 

# Configure logger
logger = logging.getLogger(__name__)


class ClientService:
    """
    Production-grade service for client authentication, registration,
    and device management with JWT support.
    
    Features:
    - JWT token generation with custom claims
    - Comprehensive error handling
    - Detailed logging
    - Security audit trails using your enhanced SecurityLog
    - Device conflict resolution
    - Session management
    - Location-aware operations
    """

    # Configuration
    MAX_FAILED_LOGIN_ATTEMPTS = 5
    ACCOUNT_TIER_DEVICE_LIMITS = {
        'basic': 100,
        'premium': 100,
        'business': 100,
        'enterprise': 100
    }
    
    # JWT Configuration
    ACCESS_TOKEN_LIFETIME = timedelta(minutes=30)  # Short-lived for security
    REFRESH_TOKEN_LIFETIME = timedelta(days=7)
    
    # Session Configuration
    DEFAULT_SESSION_TIMEOUT_MINUTES = 1440  # 24 hours
    SESSION_CLEANUP_AGE_HOURS = 24  # Clean up sessions older than 24 hours

    @staticmethod
    def _create_security_log(
        user: Optional[ClientH] = None,
        action_type: str = '',
        action_category: str = 'authentication',
        description: str = '',
        severity: str = 'info',
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        location: Optional[Location] = None,
        session_id: Optional[str] = None,
        details: Dict = None,
        auto_calculate_threat: bool = True
    ) -> SecurityLog:
        """
        Create a security log entry using your enhanced model.
        """
        try:
            log = SecurityLog.objects.create(
                user=user,
                action_type=action_type,
                action_category=action_category,
                description=description,
                severity=severity,
                ip_address=ip_address,
                user_agent=user_agent or '',
                location=location,
                session_id=session_id or '',
                details=details or {}
            )
            
            # Auto-calculate threat score if enabled
            if auto_calculate_threat:
                log.calculate_threat_score()
            
            return log
            
        except Exception as e:
            logger.error(f"Failed to create security log: {str(e)}")
            # Don't fail the main operation due to logging error
            return None

    @staticmethod
    def _generate_jwt_tokens(
        user: User,
        client: ClientH,
        device: Optional[UserDevice] = None,
        session: Optional[UserSession] = None,
        ip_address: Optional[str] = None,
        location: Optional[Location] = None,
        user_agent: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate JWT tokens with ALL custom claims required 
        """
        # Clean up old tokens if needed
        # OutstandingToken.objects.filter(user=user).delete()
        
        refresh = RefreshToken.for_user(user)
        
        # ============ CORE IDENTITY (REQUIRED) ============
        refresh['client_id'] = str(client.id)
        refresh['client_account'] = client.account  # ✅ Payment system REQUIRES this
        refresh['account_tier'] = client.account_tier  # ✅ Payment system REQUIRES this
        refresh['phone_number'] = client.phone_number or ''  # ✅ Payment system REQUIRES this
        refresh['display_name'] = client.display_name or user.username
        
        # ============ FINANCIAL INFORMATION (REQUIRED for payment) ============
        refresh['balance'] = float(client.balance)  # ✅ CRITICAL for payment confirmation
        refresh['credit_limit'] = float(client.credit_limit)
        refresh['total_spent'] = float(client.total_spent)
        
        # ============ LOCATION INFORMATION (REQUIRED for payment) ============
        # Home location (from client profile)
        refresh['home_location_id'] = client.home_location_id if client.home_location else None
        refresh['home_location_code'] = client.home_location.code if client.home_location else None
        
        # Current location (from session or detected location)
        current_loc = location or (session.location if session else None) or client.current_location
        refresh['current_location_id'] = current_loc.id if current_loc else None
        refresh['current_location_code'] = current_loc.code if current_loc else None
        refresh['location_id'] = current_loc.id if current_loc else None  # Alias for compatibility
        
        # ============ STATUS & SETTINGS (REQUIRED for payment) ============
        refresh['is_active'] = client.status == 'active'  # ✅ Payment system checks this
        refresh['auto_renew'] = client.auto_renew  # ✅ Payment system expects this
        refresh['two_factor_enabled'] = client.two_factor_enabled  # ✅ Payment system expects this
        
        # ============ ACTIVE VOUCHER INFO (if any) ============
        if client.active_voucher:
            try:
                voucher = DispatchVoucher.objects.filter(
                    voucher_code=client.active_voucher,
                    status='active'
                ).first()
                if voucher:
                    refresh['active_voucher'] = voucher.voucher_code
                    refresh['voucher_expires_at'] = voucher.expires_at.isoformat() if voucher.expires_at else None
                    refresh['voucher_package'] = voucher.package.name if voucher.package else None
                    refresh['voucher_package_id'] = voucher.package.id if voucher.package else None
            except Exception as e:
                logger.warning(f"Failed to get active voucher info for JWT: {e}")
        
        # ============ DEVICE INFORMATION ============
        if device:
            refresh['device_id'] = str(device.id)
            refresh['device_mac'] = device.mac_address
            refresh['device_name'] = device.device_name
            refresh['is_owner'] = device.user == client
            refresh['was_transferred'] = bool(device.previous_owners and len(device.previous_owners) > 0)
            refresh['is_trusted'] = device.is_trusted
        
        # ============ SESSION INFORMATION ============
        if session:
            refresh['session_id'] = session.session_id
            refresh['login_time'] = session.login_time.isoformat()
            refresh['session_location_id'] = str(session.location.id) if session.location else None
        
        # ============ SECURITY CONTEXT ============
        if ip_address:
            refresh['ip_hash'] = hashlib.sha256(ip_address.encode()).hexdigest()[:16]
            refresh['last_login_ip'] = ip_address
        
        if user_agent:
            refresh['ua_hash'] = hashlib.sha256(user_agent.encode()).hexdigest()[:16]
        
        # ============ TIMESTAMPS ============
        refresh['last_login'] = client.last_login.isoformat() if client.last_login else timezone.now().isoformat()
        refresh['last_balance_update'] = client.last_balance_update.isoformat() if client.last_balance_update else None
        refresh['token_issued_at'] = timezone.now().isoformat()
        
        # ============ PERMISSIONS/ROLES ============
        refresh['permissions'] = {
            'max_devices': client.get_max_allowed_devices(),
            'can_transfer_devices': True,
            'auto_renew': client.auto_renew,
            'two_factor_enabled': client.two_factor_enabled,
            'status': client.status,
            'account_tier': client.account_tier,
            'can_purchase': client.status == 'active' and client.balance >= 0,
            'can_use_credit': client.is_eligible_for_credit,
            'available_credit': float(client.available_credit)
        }
        
        # ============ USER METADATA ============
        refresh['user_id'] = user.id
        refresh['username'] = user.username
        refresh['email'] = user.email or ''
        refresh['correlation_id'] = correlation_id or str(uuid.uuid4())
        
        # ============ AUTHENTICATION CONTEXT ============
        refresh['auth_method'] = 'password'
        refresh['auth_timestamp'] = timezone.now().isoformat()
        refresh['auth_provider'] = 'teralinkx_waves'
        
        # ============ ADDITIONAL CLIENT METADATA ============
        refresh['client_metadata'] = {
            'created_at': client.created_at.isoformat() if hasattr(client, 'created_at') else None,
            'lifetime_data_used': client.lifetime_data_used,
            'failed_login_attempts': client.failed_login_attempts,
            'profile_image': bool(client.profile_image),
            'is_roaming': client.current_location != client.home_location if client.current_location and client.home_location else False
        }
        
        # Set expiration times
        access_token = refresh.access_token
        access_token.set_exp(lifetime=ClientService.ACCESS_TOKEN_LIFETIME)
        
        # Log the token generation with claim details
        logger.info(
            f"Generated JWT with {len(refresh.payload)} claims for client: {client.account} "
            f"(Balance: {client.balance}, Location: {current_loc.code if current_loc else 'None'})"
        )
        
        return {
            'refresh': str(refresh),
            'access': str(access_token),
            'token_type': 'Bearer',
            'expires_in': int(ClientService.ACCESS_TOKEN_LIFETIME.total_seconds()),
            'refresh_expires_in': int(ClientService.REFRESH_TOKEN_LIFETIME.total_seconds()),
            'correlation_id': refresh['correlation_id'],
            'claims_summary': {
                'client_account': refresh['client_account'],
                'balance': refresh['balance'],
                'location_id': refresh['location_id'],
                'has_active_voucher': 'active_voucher' in refresh
            }
        }

    @staticmethod
    def detect_location(
        ip_address: Optional[str] = None,
        mac_address: Optional[str] = None,
        ap_identifier: Optional[str] = None
    ) -> Optional[Location]:
        """
        Detect location based on available data.
        """
        try:
            # Check if Location app is installed
            if not apps.is_installed('locations'):
                logger.warning("Locations app is not installed")
                return None
            
            # Check if Location model exists
            try:
                from locations.models import Location
            except ImportError:
                logger.warning("Location model not found")
                return None
            
            # Try AP/SSID based location first
            if ap_identifier:
                try:
                    location = Location.objects.filter(
                        access_points__identifier=ap_identifier,
                        is_active=True
                    ).first()
                    if location:
                        logger.info(f"Location detected via AP: {ap_identifier} -> {location.code}")
                        return location
                except Exception as e:
                    logger.warning(f"AP-based location detection failed: {str(e)}")
            
            # Try default active location
            try:
                location = Location.objects.filter(is_active=True).first()
                if location:
                    logger.info(f"Using default location: {location.code}")
                    return location
            except Exception as e:
                logger.warning(f"Default location detection failed: {str(e)}")
            
            # Create a fallback location if none exists
            try:
                location, created = Location.objects.get_or_create(
                    code='FALLBACK',
                    defaults={
                        'name': 'Fallback Location',
                        'is_active': True,
                        'description': 'Auto-created fallback location'
                    }
                )
                if created:
                    logger.warning(f"Created fallback location: {location.code}")
                else:
                    logger.info(f"Using existing fallback location: {location.code}")
                return location
            except Exception as e:
                logger.error(f"Failed to create/get fallback location: {str(e)}")
                return None

        except Exception as e:
            logger.error(f"Location detection completely failed: {str(e)}", exc_info=True)
            return None

    @staticmethod
    def _validate_phone_number(phone: str) -> bool:
        """Validate phone number format - accepts +254XXXXXXXXX format"""
        if not phone:
            return False
        
        # Remove non-digits for validation
        cleaned = ''.join(filter(str.isdigit, phone))
        
        # Must be 12 digits (254 + 9 digits) for Kenyan numbers
        if len(cleaned) != 12:
            return False
            
        # Must start with 254 (Kenya country code)
        if not cleaned.startswith('254'):
            return False
            
        # Validate Kenyan mobile prefixes (7xx, 1xx, 0xx after 254)
        mobile_part = cleaned[3:]  # Remove 254
        if len(mobile_part) != 9:
            return False
            
        # Valid Kenyan mobile prefixes
        valid_prefixes = ['7', '1', '0']
        if mobile_part[0] not in valid_prefixes:
            return False
            
        return True

    @staticmethod
    def _check_account_limits(client: ClientH) -> bool:
        """Check if client can add more devices"""
        active_devices = client.devices.filter(status='active').count()
        max_allowed = ClientService.ACCOUNT_TIER_DEVICE_LIMITS.get(
            client.account_tier, 3
        )
        
        if active_devices >= max_allowed:
            logger.warning(
                f"Device limit reached for {client.account}: "
                f"{active_devices}/{max_allowed}"
            )
            
            # Log as security event
            ClientService._create_security_log(
                user=client,
                action_type='access_denied',
                action_category='authorization',
                description=f"Device limit reached ({active_devices}/{max_allowed})",
                severity='medium',
                details={
                    'active_devices': active_devices,
                    'max_allowed': max_allowed,
                    'account_tier': client.account_tier
                }
            )
            
            return False
        return True

    @staticmethod
    def _handle_failed_login(client: ClientH, ip_address: str, user_agent: str = '') -> None:
        """Track failed login attempts with security logging"""
        client.failed_login_attempts += 1
        client.save()

        # Create security log
        log = ClientService._create_security_log(
            user=client,
            action_type='login_failed',
            action_category='authentication',
            description=f"Failed login attempt #{client.failed_login_attempts} from {ip_address}",
            severity='medium' if client.failed_login_attempts < 3 else 'high',
            ip_address=ip_address,
            user_agent=user_agent,
            details={
                'attempt_number': client.failed_login_attempts,
                'ip_address': ip_address,
                'timestamp': timezone.now().isoformat(),
                'max_attempts': ClientService.MAX_FAILED_LOGIN_ATTEMPTS
            }
        )

        # Suspend account if too many failures
        if client.failed_login_attempts >= ClientService.MAX_FAILED_LOGIN_ATTEMPTS:
            old_status = client.status
            client.status = 'suspended'
            client.save()
            
            logger.warning(f"Account suspended: {client.account} due to {client.failed_login_attempts} failed logins")
            
            ClientService._create_security_log(
                user=client,
                action_type='device_blocked',  # Using device_blocked for account suspension
                action_category='device_management',
                description=f"Account suspended after {client.failed_login_attempts} failed login attempts",
                severity='critical',
                ip_address=ip_address,
                details={
                    'reason': 'excessive_failed_logins',
                    'failed_attempts': client.failed_login_attempts,
                    'previous_status': old_status,
                    'new_status': client.status
                }
            )

    @staticmethod
    def _reset_failed_logins(client: ClientH) -> None:
        """Reset failed login counter on successful login"""
        if client.failed_login_attempts > 0:
            old_count = client.failed_login_attempts
            client.failed_login_attempts = 0
            client.save()
            
            logger.info(f"Reset failed login attempts for {client.account}: {old_count} -> 0")
            
            ClientService._create_security_log(
                user=client,
                action_type='login_success',
                action_category='authentication',
                description=f"Successful login after {old_count} previous failures",
                severity='info',
                details={
                    'previous_failures': old_count
                }
            )

    @staticmethod
    def _create_user(
        phone: str,
        password: str,
        email: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> User:
        """Create new user with validation and security logging"""
        if not ClientService._validate_phone_number(phone):
            raise ValidationError("Invalid phone number format")

        if User.objects.filter(username=phone).exists():
            raise BusinessLogicError("User already exists")

        user = User.objects.create_user(
            username=phone,  # Store with + format
            password=password,
            email=email or f"{phone.replace('+', '')}@teralinkx.net"  # Remove + for email
        )
        
        logger.info(f"Created new user: {phone}")
        
        return user

    @staticmethod
    def _authenticate_user(
        phone: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> User:
        """Authenticate existing user with security logging"""
        try:
            user = User.objects.get(username=phone)
            
            # Check if account is locked/suspended via ClientH
            if hasattr(user, 'client_profile'):
                client = user.client_profile
                if client.status in ['suspended', 'banned']:
                    # Log failed login due to suspended account
                    ClientService._create_security_log(
                        user=client,
                        action_type='login_failed',
                        action_category='authentication',
                        description=f"Login attempt to {client.status} account",
                        severity='high',
                        ip_address=ip_address,
                        user_agent=user_agent,
                        details={
                            'reason': f'account_{client.status}',
                            'account_status': client.status
                        }
                    )
                    raise AuthenticationError(f"Account is {client.status}")
            
            if not user.check_password(password):
                raise AuthenticationError("Invalid password")
                
            return user
            
        except User.DoesNotExist:
            # Log failed login for non-existent user
            ClientService._create_security_log(
                user=None,
                action_type='login_failed',
                action_category='authentication',
                description=f"Login attempt for non-existent user: {phone}",
                severity='medium',
                ip_address=ip_address,
                user_agent=user_agent,
                details={
                    'reason': 'user_not_found',
                    'attempted_username': phone
                }
            )
            raise AuthenticationError("User not found")

    @staticmethod
    def _get_or_create_client(
        user: User,
        phone: str,
        display_name: Optional[str],
        location: Optional[Location],
        ip_address: Optional[str] = None
    ) -> Tuple[ClientH, bool]:
        """Get or create ClientH with security logging"""
        try:
            client = user.client_profile
            client_created = False
            
            # Update last login
            client.last_login = timezone.now()
            
            # Update location if provided
            if location and location != client.current_location:
                client.current_location = location
                client.last_location_update = timezone.now()
            
            client.save()
            
            # Log successful login for existing user
            ClientService._create_security_log(
                user=client,
                action_type='login_success',
                action_category='authentication',
                description=f"Successful login from {ip_address or 'unknown IP'}",
                severity='info',
                ip_address=ip_address,
                location=location,
                details={
                    'location_changed': location != client.home_location if location else False,
                    'new_location': str(location) if location else None
                }
            )
            
        except ClientH.DoesNotExist:
            # Create new client
            client = ClientH.objects.create(
                user=user,
                account=f"CLI{user.id:06d}",
                phone_number=phone,
                display_name=display_name or f"User_{phone[-4:]}",
                home_location=location,
                current_location=location,
                last_location_update=timezone.now() if location else None,
                status='active',
                account_tier='basic'
            )
            client_created = True
            
            logger.info(f"Created new client: {client.account}")
            
            # Log new client creation
            ClientService._create_security_log(
                user=client,
                action_type='device_registered',  # Closest match for new account
                action_category='device_management',
                description="New client account created",
                severity='info',
                ip_address=ip_address,
                location=location,
                details={
                    'account_number': client.account,
                    'display_name': client.display_name,
                    'initial_location': str(location) if location else None
                }
            )
        
        return client, client_created

    @staticmethod
    def _map_device_type(parsed_type):
        """Map parsed device type to model choices"""
        type_mapping = {
            'mobile': 'phone',
            'tablet': 'tablet',
            'desktop': 'desktop',
            'smart_tv': 'tv',
            'gaming_console': 'gaming',
            'unknown': 'other'
        }
        return type_mapping.get(parsed_type, 'other')
    
    @staticmethod
    def _map_platform(parsed_platform):
        """Map parsed platform to model choices"""
        platform_lower = parsed_platform.lower()
        
        if 'windows' in platform_lower:
            return 'windows'
        elif 'mac' in platform_lower or 'ios' in platform_lower:
            return 'macos' if 'mac' in platform_lower else 'ios'
        elif 'android' in platform_lower:
            return 'android'
        elif 'linux' in platform_lower:
            return 'linux'
        else:
            return 'other'

    @staticmethod
    def detect_device_type_and_info(device_info: Dict) -> Dict[str, Any]:
        """
        Enhanced device detection using comprehensive device information.
        
        Args:
            device_info: Dictionary containing device fingerprinting data
            
        Returns:
            Dictionary with detected device type, platform, model, etc.
        """
        try:
            logger.info(f"Device detection input: {device_info}")
            
            user_agent = device_info.get('userAgent', '').lower()
            platform = device_info.get('platform', '').lower()
            screen_width = device_info.get('screenWidth', 0)
            screen_height = device_info.get('screenHeight', 0)
            touch_points = device_info.get('touchPoints', 0)
            is_touch = device_info.get('isTouch', False)
            is_mobile = device_info.get('isMobile', False)
            is_tablet = device_info.get('isTablet', False)
            
            logger.info(f"Device detection - UA: {user_agent[:50]}..., Mobile: {is_mobile}, Tablet: {is_tablet}, Touch: {is_touch}")
            
            # Device type detection
            device_type = 'other'
            device_platform = 'other'
            device_model = 'Unknown'
            device_manufacturer = 'Unknown'
            
            # Platform detection
            if 'android' in user_agent:
                device_platform = 'android'
                device_manufacturer = 'Android'
                
                # Android device type detection
                if is_tablet or (screen_width >= 768 and not is_mobile):
                    device_type = 'tablet'
                else:
                    device_type = 'phone'
                    
            elif any(ios_indicator in user_agent for ios_indicator in ['iphone', 'ipod', 'ipad']):
                device_platform = 'ios'
                device_manufacturer = 'Apple'
                
                if 'ipad' in user_agent:
                    device_type = 'tablet'
                    device_model = 'iPad'
                elif 'iphone' in user_agent:
                    device_type = 'phone'
                    device_model = 'iPhone'
                elif 'ipod' in user_agent:
                    device_type = 'phone'
                    device_model = 'iPod'
                    
            elif 'smart-tv' in user_agent or 'smarttv' in user_agent or 'tizen' in user_agent:
                device_type = 'tv'
                device_platform = 'tv'
                device_manufacturer = 'Smart TV'
                
            elif 'macintosh' in user_agent or 'mac os' in user_agent:
                device_platform = 'macos'
                device_manufacturer = 'Apple'
                device_type = 'laptop'
                device_model = 'Mac'
                
            elif 'windows' in user_agent:
                device_platform = 'windows'
                device_manufacturer = 'PC'
                
                # Windows device type detection
                if is_touch and screen_width < 1200:
                    device_type = 'tablet'
                elif 'mobile' in user_agent or is_mobile:
                    device_type = 'phone'
                else:
                    device_type = 'desktop' if screen_width > 1400 else 'laptop'
                    
            elif 'linux' in user_agent:
                device_platform = 'linux'
                device_type = 'desktop'
                
            # Store additional device info
            additional_info = {
                'screen_resolution': f"{screen_width}x{screen_height}",
                'touch_capable': is_touch,
                'touch_points': touch_points,
                'pixel_ratio': device_info.get('pixelRatio', 1),
                'orientation': device_info.get('orientation', 'unknown'),
                'timezone': device_info.get('timezone', 'unknown'),
                'language': device_info.get('language', 'unknown'),
                'connection_type': device_info.get('connectionType', 'unknown')
            }
            
            result = {
                'device_type': device_type,
                'device_platform': device_platform,
                'device_model': device_model,
                'device_manufacturer': device_manufacturer,
                'device_identification': additional_info
            }
            
            logger.info(f"Device detection result: {result}")
            return result
            
        except Exception as e:
            logger.warning(f"Device detection failed: {str(e)}")
            return {
                'device_type': 'other',
                'device_platform': 'other', 
                'device_model': 'Unknown',
                'device_manufacturer': 'Unknown',
                'device_identification': {}
            }

    @staticmethod
    def _handle_device_with_conflict_resolution(
        mac_address: str,
        client: ClientH,
        ip_address: Optional[str],
        location: Optional[Location],
        conflict_resolution: str = 'transfer',
        user_agent: Optional[str] = None,
        device_info: Optional[Dict] = None
    ) -> Tuple[Optional[UserDevice], bool, bool]:
        """
        Handle device with configurable conflict resolution.
        
        Returns: (device, is_owner, was_transferred)
        """
        if not mac_address:
            return None, False, False

        # Check if device exists
        existing_device = UserDevice.objects.filter(mac_address=mac_address).first()
        
        if not existing_device:
            # New device - check account limits
            if not ClientService._check_account_limits(client):
                raise BusinessLogicError(
                    f"Device limit reached for account tier {client.account_tier}"
                )
            
            # Detect device info from user agent if not provided
            if not device_info and user_agent:
                device_info = ClientService.detect_device_type_and_info({
                    'userAgent': user_agent,
                    'isMobile': 'mobile' in user_agent.lower(),
                    'isTouch': 'touch' in user_agent.lower()
                })
            elif device_info:
                device_info = ClientService.detect_device_type_and_info(device_info)
            
            device = UserDevice.objects.create(
                user=client,
                mac_address=mac_address,
                device_name=f"{client.display_name}'s {device_info.get('device_type', 'Device').title()}" if device_info else f"{client.display_name}'s Device",
                device_type=device_info.get('device_type', 'other') if device_info else 'other',
                device_platform=device_info.get('device_platform', 'other') if device_info else 'other',
                device_model=device_info.get('device_model', 'Unknown') if device_info else 'Unknown',
                device_manufacturer=device_info.get('device_manufacturer', 'Unknown') if device_info else 'Unknown',
                device_identification=device_info.get('device_identification', {}) if device_info else {},
                is_trusted=True,
                status='active'
            )
            
            logger.info(f"Created new device: {mac_address} for {client.account}")
            
            # Log device registration
            ClientService._create_security_log(
                user=client,
                action_type='device_registered',
                action_category='device_management',
                description=f"New device registered: {mac_address}",
                severity='info',
                ip_address=ip_address,
                location=location,
                user_agent=user_agent,
                details={
                    'mac_address': mac_address,
                    'device_name': device.device_name,
                    'device_type': device.device_type
                }
            )
            
            return device, True, False
        
        # Device exists - check ownership
        if existing_device.user == client:
            # Same user - update and return
            existing_device.last_seen = timezone.now()
            existing_device.total_connections += 1
            if location:
                existing_device.last_seen_location = location
            existing_device.save()
            
            # Log device reconnection
            ClientService._create_security_log(
                user=client,
                action_type='device_connected',
                action_category='device_management',
                description=f"Device reconnected: {mac_address}",
                severity='info',
                ip_address=ip_address,
                location=location,
                user_agent=user_agent,
                details={
                    'mac_address': mac_address,
                    'total_connections': existing_device.total_connections
                }
            )
            
            return existing_device, True, False
        
        # Device belongs to different user - handle conflict
        old_client = existing_device.user
        
        if conflict_resolution == 'reject':
            # Log the rejection
            ClientService._create_security_log(
                user=client,
                action_type='access_denied',
                action_category='authorization',
                description=f"Device {mac_address} already registered to {old_client.account}",
                severity='medium',
                ip_address=ip_address,
                location=location,
                user_agent=user_agent,
                details={
                    'mac_address': mac_address,
                    'current_owner': old_client.account,
                    'conflict_resolution': 'rejected'
                }
            )
            
            raise DeviceConflictError(
                f"Device {mac_address} already registered to {old_client.account}"
            )
        
        elif conflict_resolution == 'create_new':
            # Create new device with modified MAC (not recommended)
            modified_mac = f"{mac_address}_{uuid.uuid4().hex[:4]}"
            device = UserDevice.objects.create(
                user=client,
                mac_address=modified_mac,
                device_name=f"{client.display_name}'s Device (Conflict)",
                device_type='other',
                device_platform='other',
                is_trusted=False,
                status='active'
            )
            
            logger.warning(
                f"Device conflict - created new with modified MAC: "
                f"{mac_address} -> {modified_mac}"
            )
            
            # Log conflict resolution
            ClientService._create_security_log(
                user=client,
                action_type='device_registered',
                action_category='device_management',
                description=f"Device conflict resolved by creating new record",
                severity='medium',
                ip_address=ip_address,
                location=location,
                user_agent=user_agent,
                details={
                    'original_mac': mac_address,
                    'new_mac': modified_mac,
                    'previous_owner': old_client.account,
                    'conflict_resolution': 'created_new'
                }
            )
            
            return device, True, False
        
        else:  # 'transfer' - default
            # Check if old client would exceed limits after transfer
            old_client_devices = old_client.devices.exclude(
                mac_address=mac_address
            ).filter(status='active').count()
            
            # Terminate old client's active sessions on this device using terminate() method
            terminated_sessions = UserSession.objects.filter(
                user=old_client,
                device=existing_device,
                is_active=True
            )
            terminated_count = 0
            for session in terminated_sessions:
                session.terminate(reason=f"Device transferred to {client.account}")
                terminated_count += 1

            logger.info(
                f"Device transfer cleanup: "
                f"Terminated {terminated_count} sessions"
            )
            
            # Transfer device
            previous_owner = existing_device.user.account
            existing_device.user = client
            existing_device.device_name = f"{client.display_name}'s Device"
            existing_device.is_trusted = False  # Reset trust on transfer
            
            # Update device detection info if provided
            if device_info:
                existing_device.device_type = device_info.get('device_type', existing_device.device_type)
                existing_device.device_platform = device_info.get('device_platform', existing_device.device_platform)
                existing_device.device_model = device_info.get('device_model', existing_device.device_model)
                existing_device.device_manufacturer = device_info.get('device_manufacturer', existing_device.device_manufacturer)
                existing_device.device_identification = device_info.get('device_identification', existing_device.device_identification)
            
            existing_device.save()
            
            # Log device transfer (OUT) for old owner
            ClientService._create_security_log(
                user=old_client,
                action_type='device_untrusted',  # Using untrusted for transfer out
                action_category='device_management',
                description=f"Device {mac_address} transferred to {client.account}",
                severity='medium',
                ip_address=ip_address,
                location=location,
                details={
                    'new_owner': client.account,
                    'device_mac': mac_address,
                    'terminated_sessions': terminated_count,
                    'previous_owner': previous_owner,
                    'conflict_resolution': 'transferred'
                }
            )
            
            # Log device transfer (IN) for new owner
            ClientService._create_security_log(
                user=client,
                action_type='device_trusted',  # Using trusted for transfer in
                action_category='device_management',
                description=f"Received device {mac_address} from {previous_owner}",
                severity='medium',
                ip_address=ip_address,
                location=location,
                user_agent=user_agent,
                details={
                    'previous_owner': previous_owner,
                    'device_mac': mac_address,
                    'conflict_resolution': 'transferred'
                }
            )
            
            logger.info(
                f"Device transferred: {mac_address} from "
                f"{previous_owner} to {client.account}"
            )
            
            return existing_device, True, True

    @staticmethod
    def _create_or_get_device_session(
        client: ClientH,
        device: UserDevice,
        ip_address: Optional[str],
        location: Optional[Location],
        user_agent: Optional[str] = None,
        request_metadata: Optional[Dict] = None
    ) -> UserSession:
        """
        Create a new session or get existing active session for the device.
        Returns existing active session if found and not expired.
        Uses the terminate() method for proper session cleanup.
        """
        # First, check for existing active sessions for this device and user
        existing_sessions = UserSession.objects.filter(
            user=client,
            device=device,
            is_active=True
        ).order_by('-login_time')  # Get the most recent session
        
        # If there are existing active sessions
        for session in existing_sessions:
            # Check if session is expired using the model's is_expired property
            if session.is_expired:
                # Use terminate() method for proper cleanup
                session.terminate(reason="Session expired on new connection")
                
                logger.info(f"Terminated expired session: {session.session_id}")
                
                # Log the termination
                ClientService._create_security_log(
                    user=client,
                    action_type='session_terminated',
                    action_category='authentication',
                    description=f"Expired session terminated for new connection",
                    severity='info',
                    ip_address=ip_address,
                    location=location,
                    user_agent=user_agent,
                    session_id=session.session_id,
                    details={
                        'device_mac': device.mac_address,
                        'device_name': device.device_name,
                        'session_id': session.session_id,
                        'session_age_seconds': session.duration.total_seconds(),
                        'reason': 'expired_for_new_connection'
                    }
                )
                
                # Continue to next session or create new one
            else:
                # Session is still valid, update it and return
                session.refresh_activity()
                
                # Update location if changed
                if location and location != session.location:
                    session.location = location
                
                # Update IP address if changed
                if ip_address and ip_address != session.ip_address:
                    session.ip_address = ip_address
                
                # Update user agent if changed
                if user_agent and user_agent != session.user_agent:
                    session.user_agent = user_agent
                
                # Update metadata if needed
                if request_metadata:
                    # Merge with existing metadata
                    current_metadata = session.request_metadata or {}
                    current_metadata.update(request_metadata)
                    session.request_metadata = current_metadata
                
                session.save()
                
                logger.info(f"Using existing active session: {session.session_id} for device {device.mac_address}")
                
                # Log session reuse
                ClientService._create_security_log(
                    user=client,
                    action_type='device_reconnected',
                    action_category='device_management',
                    description=f"Existing session reused for device {device.mac_address}",
                    severity='info',
                    ip_address=ip_address,
                    location=location,
                    user_agent=user_agent,
                    session_id=session.session_id,
                    details={
                        'device_mac': device.mac_address,
                        'device_name': device.device_name,
                        'session_id': session.session_id,
                        'session_age_seconds': session.duration.total_seconds(),
                        'session_type': session.session_type,
                        'has_active_voucher': session.has_active_voucher
                    }
                )
                
                return session
        
        # If we get here, either no active sessions exist or all were expired
        # Create a new session
        session_id = f"sess_{uuid.uuid4().hex[:16]}"
        
        session = UserSession.objects.create(
            user=client,
            device=device,
            session_id=session_id,
            ip_address=ip_address or "",
            location=location,
            login_time=timezone.now(),
            last_activity=timezone.now(),
            is_active=True,
            session_type='network_login',
            user_agent=user_agent or "",
            request_metadata=request_metadata or {},
            auto_logout_minutes=ClientService.DEFAULT_SESSION_TIMEOUT_MINUTES
        )
        
        logger.info(f"Created new session: {session_id} for device {device.mac_address}")
        
        # Log session creation
        ClientService._create_security_log(
            user=client,
            action_type='device_connected',
            action_category='device_management',
            description=f"New session created for device {device.mac_address}",
            severity='info',
            ip_address=ip_address,
            location=location,
            user_agent=user_agent,
            session_id=session_id,
            details={
                'device_mac': device.mac_address,
                'device_name': device.device_name,
                'session_id': session_id,
                'reason': 'new_session'
            }
        )
        
        return session

    @staticmethod
    def _update_device_presence(
        device: UserDevice,
        ip_address: Optional[str],
        location: Optional[Location]
    ) -> None:
        """Update device presence information"""
        try:
            if hasattr(device, 'update_presence'):
                device.update_presence(
                    ip_address=ip_address,
                    location=location
                )
            else:
                # Fallback update
                device.last_seen = timezone.now()
                device.total_connections += 1
                if location:
                    device.last_seen_location = location
                device.save()
        except Exception as e:
            logger.error(f"Failed to update device presence: {str(e)}")

    @staticmethod
    @transaction.atomic
    def authenticate_or_register(
        phone: str,
        password: Optional[str] = None,
        current_mac: Optional[str] = None,
        current_ip: Optional[str] = None,
        ap_identifier: Optional[str] = None,
        display_name: Optional[str] = None,
        conflict_resolution: str = 'transfer',
        user_agent: Optional[str] = None,
        device_info: Optional[Dict] = None,
        request_metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Main entry point for client authentication/registration with JWT.
        """
        start_time = timezone.now()
        correlation_id = str(uuid.uuid4())
        
        logger.info(
            f"Authentication request - "
            f"Correlation: {correlation_id}, "
            f"Phone: {phone}, "
            f"MAC: {current_mac}, "
            f"IP: {current_ip}"
        )
        
        try:
            # STEP 1: Validate inputs with detailed logging
            logger.info(f"[Step 1] Validating inputs")
            if not phone:
                error_msg = "Phone is required"
                logger.error(f"{error_msg}")
                raise ValidationError(error_msg)
            logger.info(f"[Step 1] Input validation passed")
            
            # STEP 2: Detect location
            logger.info(f"[Step 2] Detecting location")
            location = None
            try:
                location = ClientService.detect_location(
                    ip_address=current_ip,
                    mac_address=current_mac,
                    ap_identifier=ap_identifier
                )
                logger.info(f"[Step 2] Location detected: {location.id if location else 'None'}")
            except Exception as e:
                logger.warning(f"[Step 2] Location detection failed, continuing without location: {str(e)}")
                location = None
            
            # STEP 3: User authentication/creation
            logger.info(f"[Step 3] Checking user existence for: {phone}")
            user_exists = False
            try:
                user_exists = User.objects.filter(username=phone).exists()
                logger.info(f"[Step 3] User exists check result: {user_exists}")
            except Exception as e:
                logger.error(f"[Step 3] Database error checking user existence: {str(e)}")
                raise BusinessLogicError("Database error checking user")
            
            is_new_user = False
            user = None
            
            if user_exists:
                # STEP 3a: Authenticate existing user
                logger.info(f"[Step 3a] Authenticating existing user: {phone}")
                try:
                    if password:
                        # Password provided - authenticate with password
                        user = ClientService._authenticate_user(
                            phone=phone,
                            password=password,
                            ip_address=current_ip,
                            user_agent=user_agent
                        )
                    else:
                        # No password - check if account is passwordless
                        user = User.objects.get(username=phone)
                        if user.has_usable_password():
                            raise AuthenticationError("This account requires a password")
                        # Passwordless account - allow signin
                    
                    is_new_user = False
                    logger.info(f"[Step 3a] User authenticated successfully: {user.id}")
                except AuthenticationError as e:
                    logger.warning(f"[Step 3a] Authentication failed: {str(e)}")
                    
                    # Handle failed login attempts for existing users
                    try:
                        temp_user = User.objects.get(username=phone)
                        if hasattr(temp_user, 'client_profile'):
                            ClientService._handle_failed_login(
                                client=temp_user.client_profile,
                                ip_address=current_ip or 'unknown',
                                user_agent=user_agent or ''
                            )
                    except Exception as failed_login_error:
                        logger.warning(f"Failed to track failed login: {str(failed_login_error)}")
                    
                    raise
                except Exception as e:
                    logger.error(f"[Step 3a] System error during authentication: {str(e)}")
                    raise BusinessLogicError("Authentication system error")
            else:
                # STEP 3b: Create new user
                logger.info(f"[Step 3b] Creating new user: {phone}")
                try:
                    if password:
                        # Create user with password
                        user = ClientService._create_user(
                            phone=phone,
                            password=password,
                            email=request_metadata.get('email') if request_metadata else None,
                            ip_address=current_ip
                        )
                    else:
                        # Create passwordless user
                        user = User.objects.create_user(
                            username=phone,
                            email=f"{phone}@teralinkx.net"
                        )
                        user.set_unusable_password()
                        user.save()
                        
                    is_new_user = True
                    logger.info(f"[Step 3b] New user created: {user.id}")
                except ValidationError as e:
                    logger.warning(f"[Step 3b] Validation error creating user: {str(e)}")
                    raise
                except BusinessLogicError as e:
                    logger.warning(f"[Step 3b] Business logic error creating user: {str(e)}")
                    raise
                except Exception as e:
                    logger.error(f"[Step 3b] System error creating user: {str(e)}")
                    raise BusinessLogicError("User creation failed")
            
            # STEP 4: ClientH handling
            logger.info(f"[Step 4] Getting or creating ClientH for user: {user.id}")
            client = None
            client_created = False
            try:
                client, client_created = ClientService._get_or_create_client(
                    user=user,
                    phone=phone,
                    display_name=display_name,
                    location=location,
                    ip_address=current_ip
                )
                logger.info(f"[Step 4] Client handling completed - Account: {client.account}, Created: {client_created}")
            except Exception as e:
                logger.error(f"[Step 4] Failed to get/create client: {str(e)}", exc_info=True)
                raise BusinessLogicError("Client profile management failed")
            
            # STEP 5: Reset failed logins
            try:
                ClientService._reset_failed_logins(client)
                logger.info(f"[Step 5] Failed logins reset for account: {client.account}")
            except Exception as e:
                logger.warning(f"[Step 5] Failed to reset login attempts: {str(e)}")
                # Non-critical error, continue
            
            # STEP 6-8: Device handling (if MAC provided)
            device = None
            session = None
            is_device_owner = False
            was_device_transferred = False
            
            if current_mac:
                logger.info(f"[Step 6] Handling device with MAC: {current_mac}")
                try:
                    # Process enhanced device info if provided
                    processed_device_info = {}
                    if device_info:
                        processed_device_info = ClientService.detect_device_type_and_info(device_info)
                        logger.info(f"[Step 6] Enhanced device detection: {processed_device_info.get('device_type')} {processed_device_info.get('device_manufacturer')} {processed_device_info.get('device_model')}")
                    elif user_agent:
                        # Use our new DeviceParser for rich User-Agent parsing
                        from core.utils.device_parser import DeviceParser
                        device_info_from_ua = DeviceParser.parse_user_agent(user_agent)
                        processed_device_info = {
                            'device_type': ClientService._map_device_type(device_info_from_ua['device_type']),
                            'device_platform': ClientService._map_platform(device_info_from_ua['platform']),
                            'device_model': device_info_from_ua['model'],
                            'device_manufacturer': device_info_from_ua['manufacturer'],
                            'device_identification': {
                                'user_agent': device_info_from_ua['user_agent'],
                                'browser': device_info_from_ua['browser_info'],
                                'os': device_info_from_ua['os_info'],
                                'device_details': device_info_from_ua['device_details'],
                                'last_updated': timezone.now().isoformat()
                            }
                        }
                        logger.info(f"[Step 6] User-Agent device detection: {processed_device_info.get('device_type')} {processed_device_info.get('device_manufacturer')} {processed_device_info.get('device_model')}")
                    
                    device, is_device_owner, was_device_transferred = (
                        ClientService._handle_device_with_conflict_resolution(
                            mac_address=current_mac,
                            client=client,
                            ip_address=current_ip,
                            location=location,
                            conflict_resolution=conflict_resolution,
                            user_agent=user_agent,
                            device_info=processed_device_info
                        )
                    )
                    
                    if device:
                        logger.info(f"[Step 6] Device handled - ID: {device.id}, Owner: {is_device_owner}, Transferred: {was_device_transferred}")
                        
                        # Update device presence
                        try:
                            ClientService._update_device_presence(
                                device=device,
                                ip_address=current_ip,
                                location=location
                            )
                            logger.info(f"[Step 6a] Device presence updated")
                        except Exception as e:
                            logger.warning(f"[Step 6a] Failed to update device presence: {str(e)}")
                        
                        # Create or get existing session
                        try:
                            session = ClientService._create_or_get_device_session(
                                client=client,
                                device=device,
                                ip_address=current_ip,
                                location=location,
                                user_agent=user_agent,
                                request_metadata=request_metadata
                            )
                            
                            # Update session metadata
                            session.is_owner = is_device_owner
                            session.was_transferred = was_device_transferred
                            session.save()
                            
                            logger.info(f"[Step 6b] Session handled: {session.session_id}")
                        except Exception as e:
                            logger.warning(f"[Step 6b] Failed to handle session: {str(e)}")
                            session = None
                    else:
                        logger.warning(f"[Step 6] No device created/retrieved for MAC: {current_mac}")
                        
                except (BusinessLogicError, DeviceConflictError) as e:
                    logger.warning(f"[Step 6] Device handling error: {str(e)}")
                    raise
                except Exception as e:
                    logger.error(f"[Step 6] System error during device handling: {str(e)}", exc_info=True)
                    # Device handling is not critical for authentication, continue without device
                    device = None
                    session = None
            
            # STEP 9: Generate JWT tokens
            logger.info(f"[Step 9] Generating JWT tokens")
            token_data = None
            try:
                token_data = ClientService._generate_jwt_tokens(
                    user=user,
                    client=client,
                    device=device,
                    session=session,
                    ip_address=current_ip,
                    location=location,
                    user_agent=user_agent,
                    correlation_id=correlation_id
                )
                logger.info(f"[Step 9] JWT tokens generated successfully")
            except Exception as e:
                logger.error(f"[Step 9] Failed to generate JWT tokens: {str(e)}", exc_info=True)
                raise BusinessLogicError("Token generation failed")
            
            # STEP 10: Prepare response
            processing_time = (timezone.now() - start_time).total_seconds() * 1000
            logger.info(f"[Step 10] Preparing response - Processing time: {processing_time:.2f}ms")
            
            try:
                response_data = {
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email
                    },
                    'client': {
                        'id': client.id,
                        'account': client.account,
                        'display_name': client.display_name,
                        'phone_number': client.phone_number,
                        'balance': float(client.balance),
                        'account_tier': client.account_tier,
                        'status': client.status,
                        'home_location': {
                            'id': client.home_location.id,
                            'name': client.home_location.name,
                            'code': client.home_location.code
                        } if client.home_location else None,
                        'current_location': {
                            'id': client.current_location.id,
                            'name': client.current_location.name,
                            'code': client.current_location.code
                        } if client.current_location else None,
                        # Add additional client info for debugging
                        'additional_info': {
                            'auto_renew': client.auto_renew,
                            'two_factor_enabled': client.two_factor_enabled,
                            'credit_limit': float(client.credit_limit),
                            'total_spent': float(client.total_spent)
                        }
                    },
                    'auth': token_data,
                    'device': {
                        'id': device.id if device else None,
                        'mac_address': device.mac_address if device else None,
                        'device_name': device.device_name if device else None,
                        'is_owner': is_device_owner,
                        'was_transferred': was_device_transferred,
                        'is_trusted': device.is_trusted if device else None
                    } if device else None,
                    'session': {
                        'id': session.id if session else None,
                        'session_id': session.session_id if session else None,
                        'login_time': session.login_time.isoformat() if session else None,
                        'is_owner': is_device_owner,
                        'was_transferred': was_device_transferred,
                        'session_type': session.session_type if session else None,
                        'has_active_voucher': session.has_active_voucher if session else False,
                        'auto_logout_minutes': session.auto_logout_minutes if session else ClientService.DEFAULT_SESSION_TIMEOUT_MINUTES
                    } if session else None,
                    'metadata': {
                        'is_new_user': is_new_user,
                        'client_created': client_created,
                        'processing_time_ms': round(processing_time, 2),
                        'timestamp': timezone.now().isoformat(),
                        'location_detected': location is not None,
                        'correlation_id': correlation_id,
                        'token_expiry': (timezone.now() + ClientService.ACCESS_TOKEN_LIFETIME).isoformat(),
                        'session_timeout_minutes': ClientService.DEFAULT_SESSION_TIMEOUT_MINUTES
                    }
                }
            except Exception as e:
                logger.error(f"[Step 10] Error preparing response: {str(e)}", exc_info=True)
                raise BusinessLogicError("Response preparation failed")
            
            # STEP 11: Log successful authentication
            try:
                ClientService._create_security_log(
                    user=client,
                    action_type='login_success',
                    action_category='authentication',
                    description=f"Authentication successful - New user: {is_new_user}",
                    severity='info',
                    ip_address=current_ip,
                    user_agent=user_agent,
                    location=location,
                    session_id=session.session_id if session else None,
                    details={
                        'is_new_user': is_new_user,
                        'client_created': client_created,
                        'device_registered': device is not None,
                        'device_owner': is_device_owner,
                        'device_transferred': was_device_transferred,
                        'processing_time_ms': processing_time,
                        'correlation_id': correlation_id,
                        'token_type': 'jwt',
                        'session_reused': session and session.login_time < (timezone.now() - timedelta(minutes=5)) if session else False
                    }
                )
            except Exception as e:
                logger.warning(f"[Step 11] Failed to create security log: {str(e)}")
                # Non-critical, continue
            
            logger.info(
                f"Authentication completed successfully - "
                f"Correlation: {correlation_id}, "
                f"Account: {client.account}, "
                f"New User: {is_new_user}, "
                f"Device: {current_mac or 'None'}, "
                f"Session: {session.session_id if session else 'None'}, "
                f"Time: {processing_time:.2f}ms"
            )
            
            return response_data
            
        except (ValidationError, AuthenticationError, BusinessLogicError, DeviceConflictError) as e:
            # Client errors - log with correlation ID
            error_type = type(e).__name__
            error_details = {
                'error_type': error_type,
                'error_message': str(e),
                'correlation_id': correlation_id,
                'phone': phone,
                'mac_address': current_mac,
                'ip_address': current_ip,
                'timestamp': timezone.now().isoformat()
            }
            
            # Find client for logging (if exists)
            client_for_log = None
            try:
                user_temp = User.objects.get(username=phone)
                client_for_log = getattr(user_temp, 'client_profile', None)
            except Exception:
                pass
            
            # Log with detailed traceback for debugging
            logger.warning(
                f"Client authentication error - "
                f"Correlation: {correlation_id}, "
                f"Error: {error_type}, "
                f"Message: {str(e)}, "
                f"Traceback: {traceback.format_exc()}"
            )
            
            try:
                ClientService._create_security_log(
                    user=client_for_log,
                    action_type='login_failed' if 'Authentication' in error_type else 'access_denied',
                    action_category='authentication',
                    description=f"{error_type}: {str(e)}",
                    severity='medium',
                    ip_address=current_ip,
                    user_agent=user_agent,
                    details=error_details
                )
            except Exception as log_error:
                logger.error(f"Failed to create error security log: {str(log_error)}")
            
            # Re-raise the original error
            raise
            
        except Exception as e:
            # System errors
            error_type = type(e).__name__
            full_traceback = traceback.format_exc()
            
            logger.error(
                f"System error in authenticate_or_register - "
                f"Correlation: {correlation_id}, "
                f"Error: {error_type}, "
                f"Message: {str(e)}, "
                f"Traceback: {full_traceback}"
            )
            
            try:
                # Log system error with full details
                ClientService._create_security_log(
                    user=None,
                    action_type='system',
                    action_category='system',
                    description=f"System error during authentication: {error_type}",
                    severity='critical',
                    ip_address=current_ip,
                    user_agent=user_agent,
                    details={
                        'error_type': error_type,
                        'error_message': str(e),
                        'correlation_id': correlation_id,
                        'phone': phone,
                        'timestamp': timezone.now().isoformat(),
                        'traceback': full_traceback[:1000]  # First 1000 chars of traceback
                    }
                )
            except Exception as log_error:
                logger.error(f"Failed to create system error security log: {str(log_error)}")
            
            # Return user-friendly error
            raise BusinessLogicError("Authentication service unavailable. Please try again.")

    @staticmethod
    def logout_user(
        user: User,
        refresh_token: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Logout user and blacklist JWT refresh token.
        Uses the terminate() method for proper session cleanup.
        """
        try:
            client = user.client_profile
            
            # Blacklist the refresh token if provided
            if refresh_token:
                try:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                    logger.info(f"JWT refresh token blacklisted for user: {user.username}")
                except Exception as e:
                    logger.warning(f"Failed to blacklist token: {str(e)}")
            
            # Terminate all active sessions using terminate() method
            sessions = UserSession.objects.filter(
                user=client,
                is_active=True
            )
            terminated = 0
            for session in sessions:
                session.terminate(reason="User logout")
                terminated += 1
            
            # Log the logout
            ClientService._create_security_log(
                user=client,
                action_type='logout',
                action_category='authentication',
                description=f"User logged out - {terminated} sessions terminated",
                severity='info',
                ip_address=ip_address,
                user_agent=user_agent,
                details={
                    'sessions_terminated': terminated,
                    'token_blacklisted': refresh_token is not None,
                    'user_id': user.id,
                    'logout_type': 'jwt_blacklist'
                }
            )
            
            logger.info(f"Logout successful - User: {user.username}, Sessions: {terminated}")
            
            return {
                'success': True,
                'sessions_terminated': terminated,
                'tokens_blacklisted': 1 if refresh_token else 0,
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Logout failed for user {user.username}: {str(e)}")
            
            ClientService._create_security_log(
                user=getattr(user, 'client_profile', None),
                action_type='system',
                action_category='system',
                description=f"Logout failed: {str(e)}",
                severity='high',
                ip_address=ip_address,
                user_agent=user_agent,
                details={
                    'error': str(e),
                    'user_id': user.id
                }
            )
            
            raise BusinessLogicError("Logout failed")

    @staticmethod
    def refresh_token(
        refresh_token: str,
        device_mac: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Refresh JWT token with device validation.
        """
        try:
            # Validate the refresh token
            token = RefreshToken(refresh_token)
            
            # Get user from token
            user_id = token.get('user_id')
            if not user_id:
                raise AuthenticationError("Invalid token: no user_id claim")
            
            user = User.objects.get(id=user_id)
            client = user.client_profile
            
            # Optional: Validate device if MAC provided
            if device_mac:
                try:
                    device = client.devices.get(mac_address=device_mac, status='active')
                    
                    # Log token refresh for specific device
                    ClientService._create_security_log(
                        user=client,
                        action_type='token_refresh',
                        action_category='authentication',
                        description=f"Token refreshed for device {device_mac}",
                        severity='info',
                        ip_address=ip_address,
                        user_agent=user_agent,
                        details={
                            'device_mac': device_mac,
                            'device_name': device.device_name,
                            'refresh_type': 'device_aware'
                        }
                    )
                except client.devices.model.DoesNotExist:
                    raise AuthenticationError("Device not found or not active")
            
            # Blacklist the old refresh token
            token.blacklist()
            
            # Generate new tokens
            new_token_data = ClientService._generate_jwt_tokens(
                user=user,
                client=client,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Log successful token refresh
            ClientService._create_security_log(
                user=client,
                action_type='token_refresh',
                action_category='authentication',
                description="JWT tokens refreshed successfully",
                severity='info',
                ip_address=ip_address,
                user_agent=user_agent,
                details={
                    'refresh_type': 'standard',
                    'new_correlation_id': new_token_data.get('correlation_id')
                }
            )
            
            logger.info(f"Token refreshed successfully for user: {user.username}")
            
            return {
                'success': True,
                'tokens': new_token_data,
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            
            ClientService._create_security_log(
                user=getattr(user, 'client_profile', None) if 'user' in locals() else None,
                action_type='token_refresh_failed',
                action_category='authentication',
                description=f"Token refresh failed: {str(e)}",
                severity='medium',
                ip_address=ip_address,
                user_agent=user_agent,
                details={
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            )
            
            if isinstance(e, AuthenticationError):
                raise
            else:
                raise BusinessLogicError("Token refresh failed")

    @staticmethod
    def validate_session(
        session_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate if a session is still active and valid.
        Uses the terminate() method for expired sessions.
        """
        try:
            session = UserSession.objects.get(
                session_id=session_id,
                is_active=True
            )
            
            # Check if session expired
            if session.is_expired:
                # Use terminate() method for proper cleanup
                session.terminate(reason="Session expired during validation")
                
                # Log expired session
                ClientService._create_security_log(
                    user=session.user,
                    action_type='session_terminated',
                    action_category='device_management',
                    description=f"Session expired during validation after {session.duration}",
                    severity='info',
                    ip_address=ip_address,
                    user_agent=user_agent,
                    session_id=session_id,
                    details={
                        'session_duration': str(session.duration),
                        'login_time': session.login_time.isoformat(),
                        'expired_at': session.last_activity.isoformat(),
                        'reason': 'expired_during_validation'
                    }
                )
                
                return {
                    'valid': False,
                    'reason': 'expired',
                    'expired_at': session.last_activity.isoformat(),
                    'session_duration': str(session.duration)
                }
            
            # Update last activity
            session.refresh_activity()
            
            return {
                'valid': True,
                'user_id': session.user.user.id,
                'client_account': session.user.account,
                'device_mac': session.device.mac_address if session.device else None,
                'last_activity': session.last_activity.isoformat(),
                'session_duration': str(session.duration),
                'is_owner': getattr(session, 'is_owner', False),
                'was_transferred': getattr(session, 'was_transferred', False),
                'session_type': session.session_type,
                'has_active_voucher': session.has_active_voucher
            }
            
        except UserSession.DoesNotExist:
            # Log invalid session attempt
            ClientService._create_security_log(
                user=None,
                action_type='suspicious_activity',
                action_category='network_access',
                description=f"Invalid session validation attempt: {session_id}",
                severity='medium',
                ip_address=ip_address,
                user_agent=user_agent,
                details={
                    'session_id': session_id,
                    'reason': 'not_found'
                }
            )
            
            return {
                'valid': False,
                'reason': 'not_found'
            }
        except Exception as e:
            logger.error(f"Session validation failed: {str(e)}")
            
            return {
                'valid': False,
                'reason': 'validation_error'
            }

    @staticmethod
    def decode_and_validate_jwt(
        token: str,
        require_device_match: bool = False,
        expected_device_mac: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Decode and validate JWT token with optional device matching.
        """
        try:
            from rest_framework_simplejwt.authentication import JWTAuthentication
            from rest_framework_simplejwt.exceptions import InvalidToken
            
            jwt_auth = JWTAuthentication()
            
            # Validate token
            validated_token = jwt_auth.get_validated_token(token)
            user = jwt_auth.get_user(validated_token)
            
            # Get claims
            claims = validated_token.payload
            
            # Optional: Check if token is blacklisted
            if BlacklistedToken.objects.filter(token__jti=claims.get('jti')).exists():
                raise AuthenticationError("Token has been blacklisted")
            
            # Optional: Validate device match
            if require_device_match and expected_device_mac:
                token_device_mac = claims.get('device_mac')
                if token_device_mac != expected_device_mac:
                    raise AuthenticationError(f"Device mismatch. Token device: {token_device_mac}, Expected: {expected_device_mac}")
            
            return {
                'valid': True,
                'user': user,
                'client_account': claims.get('client_account'),
                'device_mac': claims.get('device_mac'),
                'session_id': claims.get('session_id'),
                'claims': claims
            }
            
        except InvalidToken as e:
            logger.warning(f"Invalid JWT token: {str(e)}")
            raise AuthenticationError(f"Invalid token: {str(e)}")
        except Exception as e:
            logger.error(f"JWT validation error: {str(e)}")
            raise AuthenticationError("Token validation failed")

    @staticmethod
    def cleanup_expired_sessions():
        """
        Clean up expired sessions using the terminate() method.
        Run this as a periodic task (e.g., via Celery or cron).
        """
        try:
            expired_sessions = UserSession.objects.filter(
                is_active=True,
                login_time__lt=timezone.now() - timedelta(hours=ClientService.SESSION_CLEANUP_AGE_HOURS)
            )
            
            count = 0
            for session in expired_sessions:
                # Use the terminate method for proper cleanup
                session.terminate(reason="Auto-cleanup of expired session")
                count += 1
            
            if count > 0:
                logger.info(f"Cleaned up {count} expired sessions")
                
                # Log the cleanup operation
                ClientService._create_security_log(
                    user=None,
                    action_type='system_maintenance',
                    action_category='system',
                    description=f"Session cleanup: terminated {count} expired sessions",
                    severity='info',
                    details={
                        'sessions_cleaned': count,
                        'cleanup_age_hours': ClientService.SESSION_CLEANUP_AGE_HOURS,
                        'timestamp': timezone.now().isoformat()
                    }
                )
            
            return count
            
        except Exception as e:
            logger.error(f"Session cleanup failed: {str(e)}")
            
            ClientService._create_security_log(
                user=None,
                action_type='system_error',
                action_category='system',
                description=f"Session cleanup failed: {str(e)}",
                severity='high',
                details={
                    'error': str(e),
                    'operation': 'session_cleanup'
                }
            )
            
            return 0

    @staticmethod
    def get_active_sessions_for_user(user: User) -> Dict[str, Any]:
        """
        Get all active sessions for a user.
        """
        try:
            client = user.client_profile
            active_sessions = UserSession.objects.filter(
                user=client,
                is_active=True
            ).select_related('device', 'location').order_by('-last_activity')
            
            sessions_data = []
            for session in active_sessions:
                sessions_data.append({
                    'session_id': session.session_id,
                    'device': {
                        'mac_address': session.device.mac_address,
                        'device_name': session.device.device_name,
                        'device_type': session.device.device_type
                    },
                    'location': {
                        'name': session.location.name if session.location else None,
                        'code': session.location.code if session.location else None
                    },
                    'login_time': session.login_time.isoformat(),
                    'last_activity': session.last_activity.isoformat(),
                    'duration_seconds': session.duration.total_seconds(),
                    'session_type': session.session_type,
                    'is_owner': session.is_owner,
                    'was_transferred': session.was_transferred,
                    'has_active_voucher': session.has_active_voucher,
                    'active_voucher': session.active_voucher,
                    'ip_address': session.ip_address
                })
            
            return {
                'success': True,
                'user_id': user.id,
                'client_account': client.account,
                'active_sessions_count': len(sessions_data),
                'sessions': sessions_data,
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get active sessions for user {user.id}: {str(e)}")
            raise BusinessLogicError("Failed to retrieve active sessions")

    # Add this new method for JWT claims verification
    @staticmethod
    def verify_jwt_claims_for_payment(token_data: Dict) -> Tuple[bool, List[str]]:
        """
        Verify JWT contains all claims required by payment confirmation system.
        
        Returns: (is_valid, missing_claims)
        """
        required_claims = [
            'client_account',
            'account_tier',
            'balance',
            'phone_number',
            'current_location_id'  # or location_id
        ]
        
        optional_claims = [
            'home_location_id',
            'is_active',
            'auto_renew',
            'two_factor_enabled',
            'active_voucher',
            'voucher_expires_at'
        ]
        
        # Extract claims from token
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            access_token = AccessToken(token_data['access'])
            claims = access_token.payload
            
            missing_required = []
            missing_optional = []
            
            for claim in required_claims:
                if claim not in claims or claims[claim] is None:
                    missing_required.append(claim)
            
            for claim in optional_claims:
                if claim not in claims:
                    missing_optional.append(claim)
            
            is_valid = len(missing_required) == 0
            
            logger.info(
                f"JWT claims verification - "
                f"Valid: {is_valid}, "
                f"Missing required: {missing_required}, "
                f"Missing optional: {missing_optional}, "
                f"Total claims: {len(claims)}"
            )
            
            return is_valid, missing_required + missing_optional
            
        except Exception as e:
            logger.error(f"Failed to verify JWT claims: {e}")
            return False, ['token_validation_failed']