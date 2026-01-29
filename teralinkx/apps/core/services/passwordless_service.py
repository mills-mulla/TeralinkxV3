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
                    "message": "New account will be created"
                }
            
            # User exists, check if has password set
            user = User.objects.get(username=phone)
            has_password = bool(user.password) and user.password != ''
            
            # Check if client exists and has OTP requirement
            requires_otp = False
            try:
                client = user.client_profile
                # You can add OTP requirement logic here
                # Example: requires_otp = client.two_factor_enabled
            except ClientH.DoesNotExist:
                client = None
            
            message = "Account exists"
            if has_password:
                message += " - password required"
            if requires_otp:
                message += " - OTP verification required"
            
            return {
                "exists": True,
                "requires_password": has_password,
                "requires_otp": requires_otp,
                "message": message
            }
            
        except Exception as e:
            logger.error(f"Error checking account status: {str(e)}")
            return {
                "exists": False,
                "requires_password": False,
                "requires_otp": False,
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
        request_metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Passwordless authentication main entry point.
        
        If password is None and account exists with password,
        authentication will fail.
        """
        start_time = timezone.now()
        correlation_id = str(uuid.uuid4())
        
        logger.info(
            f"Passwordless authentication - "
            f"Correlation: {correlation_id}, "
            f"Phone: {phone}, "
            f"Has password: {bool(password)}"
        )
        
        try:
            # Check if user exists
            user_exists = User.objects.filter(username=phone).exists()
            
            if user_exists:
                # Existing user - authenticate with password if provided
                if password:
                    # Use existing ClientService for password authentication
                    result = ClientService.authenticate_or_register(
                        phone=phone,
                        password=password,
                        current_mac=current_mac,
                        current_ip=current_ip,
                        ap_identifier=ap_identifier,
                        user_agent=user_agent,
                        request_metadata=request_metadata
                    )
                    
                    # Add metadata for passwordless flow
                    result['metadata']['requires_password'] = True
                    result['metadata']['requires_otp'] = False
                    
                    return result
                else:
                    # Check if user has password
                    user = User.objects.get(username=phone)
                    has_password = bool(user.password) and user.password != ''
                    
                    if has_password:
                        raise AuthenticationError(
                            "Account requires password. Please enter your password."
                        )
                    
                    # User exists but no password - authenticate without password
                    # This is a simplified version of ClientService.authenticate_or_register
                    # without password validation
                    
                    # Get or create client (similar to ClientService but without password)
                    try:
                        client = user.client_profile
                        client_created = False
                        client.last_login = timezone.now()
                        client.save()
                    except ClientH.DoesNotExist:
                        # Create client without password requirement
                        client = ClientH.objects.create(
                            user=user,
                            account=f"CLI{user.id:06d}",
                            phone_number=phone,
                            display_name=f"User_{phone[-4:]}",
                            status='active',
                            account_tier='basic'
                        )
                        client_created = True
                    
                    # Handle device if MAC provided
                    device = None
                    session = None
                    if current_mac:
                        # Simplified device handling
                        device, is_owner, was_transferred = (
                            ClientService._handle_device_with_conflict_resolution(
                                mac_address=current_mac,
                                client=client,
                                ip_address=current_ip,
                                location=None,  # Location can be detected if needed
                                conflict_resolution='transfer',
                                user_agent=user_agent
                            )
                        )
                        
                        if device:
                            # Create session
                            session = ClientService._create_or_get_device_session(
                                client=client,
                                device=device,
                                ip_address=current_ip,
                                location=None,
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
                        user_agent=user_agent,
                        correlation_id=correlation_id
                    )
                    
                    processing_time = (timezone.now() - start_time).total_seconds() * 1000
                    
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
                            'home_location': None,
                            'current_location': None
                        },
                        'auth': token_data,
                        'device': {
                            'id': device.id if device else None,
                            'mac_address': device.mac_address if device else None,
                            'device_name': device.device_name if device else None,
                            'is_owner': True if device else None,
                            'was_transferred': False if device else None,
                            'is_trusted': device.is_trusted if device else None
                        } if device else None,
                        'session': {
                            'id': session.id if session else None,
                            'session_id': session.session_id if session else None,
                            'login_time': session.login_time.isoformat() if session else None,
                            'is_owner': True if session else None,
                            'was_transferred': False if session else None
                        } if session else None,
                        'metadata': {
                            'is_new_user': False,
                            'client_created': client_created,
                            'processing_time_ms': round(processing_time, 2),
                            'timestamp': timezone.now().isoformat(),
                            'location_detected': False,
                            'correlation_id': correlation_id,
                            'token_expiry': (timezone.now() + ClientService.ACCESS_TOKEN_LIFETIME).isoformat(),
                            'session_timeout_minutes': ClientService.DEFAULT_SESSION_TIMEOUT_MINUTES,
                            'requires_password': False,
                            'requires_otp': False
                        }
                    }
            else:
                # New user - create without password
                # Use ClientService with a default password that will be ignored
                # since we're creating a new user
                result = ClientService.authenticate_or_register(
                    phone=phone,
                    password=str(uuid.uuid4()),  # Random password for new user
                    current_mac=current_mac,
                    current_ip=current_ip,
                    ap_identifier=ap_identifier,
                    user_agent=user_agent,
                    request_metadata=request_metadata
                )
                
                # Update user to have no password (set unusable password)
                user = User.objects.get(username=phone)
                user.set_unusable_password()
                user.save()
                
                # Update metadata
                result['metadata']['requires_password'] = False
                result['metadata']['requires_otp'] = False
                
                return result
                
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
        Setup password for authenticated user.
        """
        try:
            # Set password for user
            user.set_password(password)
            user.save()
            
            logger.info(f"Password setup successful for user: {user.username}")
            
            return {
                "success": True,
                "message": "Password set up successfully"
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