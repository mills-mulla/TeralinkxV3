# core/services/passwordless_service.py
import logging
import uuid
from datetime import timedelta
from typing import Optional, Dict, Any
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from users.models import ClientH
from core.services.client_service import ClientService
from core.exceptions import (
    BusinessLogicError,
    AuthenticationError
)

logger = logging.getLogger(__name__)


class PasswordlessService:
    """
    Service for passwordless authentication flows.
    """
    
    @staticmethod
    def check_account_status(
        phone: str,
        current_ip: Optional[str] = None,
        current_mac: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check if account exists and what authentication methods are required.
        
        Returns:
        {
            "exists": true/false,
            "requires_password": true/false,
            "requires_otp": true/false,
            "failed_attempts": number,
            "account_locked": true/false,
            "message": "Account status message"
        }
        """
        try:
            # Check if user exists
            user_exists = User.objects.filter(username=phone).exists()
            
            if not user_exists:
                return {
                    "exists": False,
                    "requires_password": False,
                    "requires_otp": False,
                    "failed_attempts": 0,
                    "account_locked": False,
                    "message": "New account will be created"
                }
            
            # User exists, check if has password set
            user = User.objects.get(username=phone)
            
            # ✅ FIX: Use Django's has_usable_password() method
            has_password = user.has_usable_password()
            
            # Check if client exists and get failed login attempts
            requires_otp = False
            failed_attempts = 0
            account_locked = False
            
            try:
                client = user.client_profile
                failed_attempts = client.failed_login_attempts
                account_locked = client.status in ['suspended', 'banned']
                # You can add OTP requirement logic here
                # Example: requires_otp = client.two_factor_enabled
            except ClientH.DoesNotExist:
                client = None
            
            message = "Account exists"
            if account_locked:
                message = "Account is temporarily locked due to failed login attempts"
            elif has_password:
                message += " - password required"
                if failed_attempts > 0:
                    message += f" ({failed_attempts} failed attempts)"
            else:
                message += " - passwordless signin"
            if requires_otp:
                message += " - OTP verification required"
            
            logger.info(
                f"Account check - Phone ending in ***{phone[-4:]}, "
                f"Exists: True, Has Password: {has_password}, "
                f"Requires OTP: {requires_otp}, Failed Attempts: {failed_attempts}, "
                f"Account Locked: {account_locked}"
            )
            
            return {
                "exists": True,
                "requires_password": has_password,
                "requires_otp": requires_otp,
                "failed_attempts": failed_attempts,
                "account_locked": account_locked,
                "message": message
            }
            
        except Exception as e:
            logger.error(f"Error checking account status: {str(e)}", exc_info=True)
            return {
                "exists": False,
                "requires_password": False,
                "requires_otp": False,
                "failed_attempts": 0,
                "account_locked": False,
                "message": "Unable to check account status"
            }

    @staticmethod
    @transaction.atomic
    def passwordless_authenticate(
        phone: str,
        password: Optional[str] = None,
        current_mac: Optional[str] = None,
        current_ip: Optional[str] = None,
        ap_identifier: Optional[str] = None,
        user_agent: Optional[str] = None,
        device_info: Optional[Dict] = None,
        request_metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Passwordless authentication main entry point.
        
        Flow:
        1. New user → Create without password → Auto-signin
        2. Existing user (no password) → Auto-signin
        3. Existing user (with password) → Require password
        """
        start_time = timezone.now()
        correlation_id = str(uuid.uuid4())
        
        logger.info(
            f"Passwordless authentication - "
            f"Correlation: {correlation_id}, "
            f"Phone ending in ***{phone[-4:]}, "
            f"Has password provided: {bool(password)}"
        )
        
        try:
            # Check if user exists (single query optimization)
            try:
                user = User.objects.get(username=phone)
                user_exists = True
            except User.DoesNotExist:
                user = None
                user_exists = False
            
            if user_exists:
                
                # ✅ FIX: Use has_usable_password() to check if account has password
                account_has_password = user.has_usable_password()
                
                if account_has_password:
                    # Account has password - require it
                    if not password:
                        logger.warning(
                            f"Password required for phone ending in ***{phone[-4:]} but not provided"
                        )
                        raise AuthenticationError(
                            "This account requires a password. Please enter your password."
                        )
                    
                    # Authenticate with password using ClientService
                    logger.info(f"Authenticating phone ending in ***{phone[-4:]} with password")
                    result = ClientService.authenticate_or_register(
                        phone=phone,
                        password=password,
                        current_mac=current_mac,
                        current_ip=current_ip,
                        ap_identifier=ap_identifier,
                        user_agent=user_agent,
                        device_info=device_info,
                        request_metadata=request_metadata
                    )
                    
                    # Add metadata for passwordless flow
                    result['metadata']['requires_password'] = True
                    result['metadata']['requires_otp'] = False
                    result['metadata']['authentication_type'] = 'password'
                    
                    return result
                    
                else:
                    # Account has no password - passwordless signin
                    logger.info(f"Passwordless signin for phone ending in ***{phone[-4:]}")
                    
                    # Get or update client
                    try:
                        client = user.client_profile
                        client_created = False
                        client.last_login = timezone.now()
                        
                        # Update location if detected
                        location = None
                        if ap_identifier:
                            location = ClientService.detect_location(
                                ip_address=current_ip,
                                mac_address=current_mac,
                                ap_identifier=ap_identifier
                            )
                            if location and client.current_location != location:
                                client.current_location = location
                                client.last_location_update = timezone.now()
                        
                        client.save()
                        
                    except ClientH.DoesNotExist:
                        # Create client profile
                        location = ClientService.detect_location(
                            ip_address=current_ip,
                            mac_address=current_mac,
                            ap_identifier=ap_identifier
                        )
                        
                        client = ClientH.objects.create(
                            user=user,
                            account=f"CLI{user.id:06d}",
                            phone_number=phone,
                            display_name=f"User_{phone[-4:]}",
                            home_location=location,
                            current_location=location,
                            last_location_update=timezone.now() if location else None,
                            status='active',
                            account_tier='basic'
                        )
                        client_created = True
                        
                        logger.info(f"Created client profile for passwordless user: {client.account}")
                    
                    # Handle device if MAC provided
                    device = None
                    session = None
                    is_owner = False
                    was_transferred = False
                    
                    if current_mac:
                        device, is_owner, was_transferred = (
                            ClientService._handle_device_with_conflict_resolution(
                                mac_address=current_mac,
                                client=client,
                                ip_address=current_ip,
                                location=client.current_location,
                                conflict_resolution='transfer',
                                user_agent=user_agent,
                                device_info=device_info  # Pass the rich device_info
                            )
                        )
                        
                        if device:
                            # Update device presence
                            ClientService._update_device_presence(
                                device=device,
                                ip_address=current_ip,
                                location=client.current_location
                            )
                            
                            # Create or get session
                            session = ClientService._create_or_get_device_session(
                                client=client,
                                device=device,
                                ip_address=current_ip,
                                location=client.current_location,
                                user_agent=user_agent,
                                request_metadata=request_metadata
                            )
                    
                    # Generate JWT tokens
                    token_data = ClientService._generate_jwt_tokens(
                        user=user,
                        client=client,
                        device=device,
                        session=session,
                        ip_address=current_ip,
                        location=client.current_location,
                        user_agent=user_agent,
                        correlation_id=correlation_id
                    )
                    
                    processing_time = (timezone.now() - start_time).total_seconds() * 1000
                    
                    logger.info(
                        f"Passwordless signin successful - "
                        f"Account: {client.account}, "
                        f"Time: {processing_time:.2f}ms"
                    )
                    
                    return {
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'email': user.email or ''
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
                            } if client.current_location else None
                        },
                        'auth': token_data,
                        'device': {
                            'id': device.id if device else None,
                            'mac_address': device.mac_address if device else None,
                            'device_name': device.device_name if device else None,
                            'is_owner': is_owner,
                            'was_transferred': was_transferred,
                            'is_trusted': device.is_trusted if device else None
                        } if device else None,
                        'session': {
                            'id': session.id if session else None,
                            'session_id': session.session_id if session else None,
                            'login_time': session.login_time.isoformat() if session else None,
                            'is_owner': is_owner,
                            'was_transferred': was_transferred,
                            'session_type': session.session_type if session else None,
                            'has_active_voucher': session.has_active_voucher if session else False
                        } if session else None,
                        'metadata': {
                            'is_new_user': False,
                            'client_created': client_created,
                            'processing_time_ms': round(processing_time, 2),
                            'timestamp': timezone.now().isoformat(),
                            'location_detected': client.current_location is not None,
                            'correlation_id': correlation_id,
                            'token_expiry': (timezone.now() + ClientService.ACCESS_TOKEN_LIFETIME).isoformat(),
                            'session_timeout_minutes': ClientService.DEFAULT_SESSION_TIMEOUT_MINUTES,
                            'requires_password': False,
                            'requires_otp': False,
                            'authentication_type': 'passwordless'
                        }
                    }
                    
            else:
                # New user - create without password
                logger.info(f"Creating new passwordless account for phone ending in ***{phone[-4:]}")
                
                # Create user with unusable password
                user = User.objects.create_user(
                    username=phone,  # Store with + format
                    email=f"{phone.replace('+', '')}@teralinkx.net"  # Remove + for email
                )
                user.set_unusable_password()  # Mark as passwordless
                user.save()
                
                logger.info(f"Created new passwordless user ending in ***{phone[-4:]}")
                
                # Detect location
                location = ClientService.detect_location(
                    ip_address=current_ip,
                    mac_address=current_mac,
                    ap_identifier=ap_identifier
                )
                
                # Create client profile
                client = ClientH.objects.create(
                    user=user,
                    account=f"CLI{user.id:06d}",
                    phone_number=phone,
                    display_name=f"User_{phone[-4:]}",
                    home_location=location,
                    current_location=location,
                    last_location_update=timezone.now() if location else None,
                    status='active',
                    account_tier='basic'
                )
                
                logger.info(f"Created client profile: {client.account}")
                
                # Handle device if MAC provided
                device = None
                session = None
                is_owner = False
                was_transferred = False
                
                if current_mac:
                    device, is_owner, was_transferred = (
                        ClientService._handle_device_with_conflict_resolution(
                            mac_address=current_mac,
                            client=client,
                            ip_address=current_ip,
                            location=location,
                            conflict_resolution='transfer',
                            user_agent=user_agent,
                            device_info=device_info  # Pass the rich device_info
                        )
                    )
                    
                    if device:
                        ClientService._update_device_presence(
                            device=device,
                            ip_address=current_ip,
                            location=location
                        )
                        
                        session = ClientService._create_or_get_device_session(
                            client=client,
                            device=device,
                            ip_address=current_ip,
                            location=location,
                            user_agent=user_agent,
                            request_metadata=request_metadata
                        )
                
                # Generate JWT tokens
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
                
                processing_time = (timezone.now() - start_time).total_seconds() * 1000
                
                logger.info(
                    f"New passwordless account created - "
                    f"Account: {client.account}, "
                    f"Time: {processing_time:.2f}ms"
                )
                
                return {
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email or ''
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
                            'id': location.id,
                            'name': location.name,
                            'code': location.code
                        } if location else None,
                        'current_location': {
                            'id': location.id,
                            'name': location.name,
                            'code': location.code
                        } if location else None
                    },
                    'auth': token_data,
                    'device': {
                        'id': device.id if device else None,
                        'mac_address': device.mac_address if device else None,
                        'device_name': device.device_name if device else None,
                        'is_owner': is_owner if device else None,
                        'was_transferred': was_transferred,
                        'is_trusted': device.is_trusted if device else None
                    } if device else None,
                    'session': {
                        'id': session.id if session else None,
                        'session_id': session.session_id if session else None,
                        'login_time': session.login_time.isoformat() if session else None,
                        'is_owner': is_owner if session else None,
                        'was_transferred': was_transferred,
                        'session_type': session.session_type if session else None,
                        'has_active_voucher': False
                    } if session else None,
                    'metadata': {
                        'is_new_user': True,
                        'client_created': True,
                        'processing_time_ms': round(processing_time, 2),
                        'timestamp': timezone.now().isoformat(),
                        'location_detected': location is not None,
                        'correlation_id': correlation_id,
                        'token_expiry': (timezone.now() + ClientService.ACCESS_TOKEN_LIFETIME).isoformat(),
                        'session_timeout_minutes': ClientService.DEFAULT_SESSION_TIMEOUT_MINUTES,
                        'requires_password': False,
                        'requires_otp': False,
                        'authentication_type': 'passwordless_new_user'
                    }
                }
                
        except (AuthenticationError, BusinessLogicError) as e:
            logger.warning(f"Passwordless authentication failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Passwordless authentication system error: {str(e)}", exc_info=True)
            raise BusinessLogicError("Authentication service unavailable")

    @staticmethod
    def setup_password(
        user: User,
        password: str
    ) -> Dict[str, Any]:
        """
        Setup password for authenticated user (for account settings).
        """
        try:
            # Set password for user
            user.set_password(password)
            user.save()
            
            logger.info(f"Password setup successful for user ending in ***{user.username[-4:]}")
            
            return {
                "success": True,
                "message": "Password set up successfully. You can now use password authentication."
            }
            
        except Exception as e:
            logger.error(f"Password setup failed: {str(e)}")
            raise BusinessLogicError("Failed to set up password")

    @staticmethod
    def verify_otp(
        phone: str,
        otp_code: str,
        session_id: str,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify OTP code.
        
        Note: You'll need to implement your OTP system.
        This is a placeholder implementation.
        """
        try:
            # Get user
            user = User.objects.get(username=phone)
            
            # TODO: Implement actual OTP verification
            # For now, this is a placeholder
            # In production, you would:
            # 1. Check if OTP exists and is valid
            # 2. Check if OTP matches the session
            # 3. Check if OTP is not expired
            
            # Placeholder: Always accept "123456" for testing
            if otp_code == "123456":
                # Generate new tokens after OTP verification
                client = user.client_profile
                
                token_data = ClientService._generate_jwt_tokens(
                    user=user,
                    client=client,
                    ip_address=ip_address
                )
                
                return {
                    "auth": token_data,
                    "success": True,
                    "message": "OTP verified successfully"
                }
            else:
                raise AuthenticationError("Invalid OTP code")
                
        except User.DoesNotExist:
            raise AuthenticationError("User not found")
        except Exception as e:
            logger.error(f"OTP verification error: {str(e)}")
            raise AuthenticationError("OTP verification failed")