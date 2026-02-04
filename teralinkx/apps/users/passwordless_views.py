# users/passwordless_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
import logging

from core.serializers.passwordless_serializer import (
    AccountCheckSerializer,
    PasswordlessAuthSerializer,
    SetupPasswordSerializer,
    VerifyOTPSerializer
)
from core.services.client_service import ClientService
from core.services.passwordless_service import PasswordlessService
from core.exceptions import (
    BusinessLogicError,
    AuthenticationError,
    DeviceConflictError
)

logger = logging.getLogger(__name__)


class AccountCheckView(APIView):
    """
    Check account status for passwordless authentication.
    
    This endpoint helps frontend decide what authentication flow to show.
    """
    permission_classes = [AllowAny]
    authentication_classes = []  # No authentication needed for checking

    def post(self, request):
        """
        Check if account exists and what authentication methods are required.
        
        Expected data:
        - phone: User phone number (required)
        - current_ip: Device IP address (optional)
        - current_mac: Device MAC address (optional)
        
        Response:
        {
            "exists": true/false,
            "requires_password": true/false,
            "requires_otp": true/false,
            "message": "Account status message"
        }
        """
        logger.info(
            f"AccountCheck request - "
            f"IP: {self._get_client_ip(request)}, "
            f"Phone: {request.data.get('phone', 'not provided')}"
        )
        
        # Validate serializer
        serializer = AccountCheckSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"AccountCheck validation failed: {serializer.errors}")
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validated_data = serializer.validated_data
            phone = validated_data['phone']
            current_ip = validated_data.get('current_ip') or self._get_client_ip(request)
            current_mac = validated_data.get('current_mac')
            
            # Check account status using PasswordlessService
            result = PasswordlessService.check_account_status(
                phone=phone,
                current_ip=current_ip,
                current_mac=current_mac
            )
            
            logger.info(
                f"AccountCheck result - "
                f"Phone: {phone}, "
                f"Exists: {result['exists']}, "
                f"Requires Password: {result['requires_password']}, "
                f"Requires OTP: {result['requires_otp']}"
            )
            
            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(
                f"AccountCheck system error: {str(e)}",
                exc_info=True
            )
            return Response(
                {
                    'error': 'Unable to check account status',
                    'code': 'SYSTEM_ERROR',
                    'suggested_action': 'try_again_later'
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_client_ip(self, request):
        """Extract client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class PasswordlessAuthView(APIView):
    """
    Passwordless authentication endpoint.
    
    Handles authentication without requiring password initially.
    Password is optional - only required if account has password protection.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        """
        Authenticate with passwordless flow.
        
        Expected data:
        - phone: User phone number (required)
        - password: User password (optional, only if account requires it)
        - current_ip: Device IP address (optional)
        - current_mac: Device MAC address (optional)
        
        Response:
        {
            "auth": { tokens... },
            "user": { user_data },
            "requires_otp": true/false,
            "is_new_account": true/false,
            "session": { session_data }
        }
        """
        logger.info(
            f"PasswordlessAuth request - "
            f"IP: {self._get_client_ip(request)}, "
            f"Phone: {request.data.get('phone', 'not provided')}"
        )
        
        # Validate serializer
        serializer = PasswordlessAuthSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"PasswordlessAuth validation failed: {serializer.errors}")
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Extract RouterOS parameters (for future integration)
            ap_identifier = request.GET.get('ap') or request.GET.get('ssid')
            original_url = request.GET.get('url', '')
            
            # Get user agent
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            client_ip = self._get_client_ip(request)
            
            # Extract validated data
            validated_data = serializer.validated_data
            phone = validated_data['phone']
            password = validated_data.get('password')
            current_mac = validated_data.get('current_mac')
            current_ip = validated_data.get('current_ip') or client_ip
            device_info = validated_data.get('device_info')
            
            logger.info(f"PasswordlessAuth - Device info received: {device_info}")
            logger.info(f"PasswordlessAuth - User agent: {user_agent[:100]}...")
            
            # Use PasswordlessService for authentication
            result = PasswordlessService.passwordless_authenticate(
                phone=phone,
                password=password,
                current_mac=current_mac,
                current_ip=current_ip,
                ap_identifier=ap_identifier,
                user_agent=user_agent,
                device_info=device_info,
                request_metadata={
                    'user_agent': user_agent,
                    'client_ip': client_ip,
                    'referer': request.META.get('HTTP_REFERER', ''),
                    'content_type': request.content_type,
                    'method': request.method,
                    'ap_identifier': ap_identifier,
                    'original_url': original_url,
                    'query_params': dict(request.GET),
                    'is_routeros': bool(ap_identifier),
                    'auth_flow': 'passwordless'
                }
            )
            
            # Prepare response
            response_data = self._prepare_response_data(result)
            
            # Add RouterOS-specific response if needed
            if ap_identifier:
                response_data['routeros'] = {
                    'redirect_url': self._get_routeros_redirect_url(
                        result, 
                        original_url
                    ),
                    'session_id': result.get('session', {}).get('session_id'),
                    'mac_address': result.get('device', {}).get('mac_address')
                }
            
            logger.info(
                f"PasswordlessAuth successful - "
                f"Account: {result['client']['account']}, "
                f"New Account: {result['metadata']['is_new_user']}, "
                f"Requires OTP: {result['metadata'].get('requires_otp', False)}"
            )
            
            return Response(
                response_data, 
                status=status.HTTP_200_OK
            )

        except AuthenticationError as e:
            logger.warning(f"PasswordlessAuth failed: {str(e)}")
            return Response(
                {
                    'error': str(e),
                    'code': 'AUTH_FAILED',
                    'suggested_action': 'check_credentials_or_contact_support'
                }, 
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        except DeviceConflictError as e:
            logger.warning(f"Device conflict: {str(e)}")
            return Response(
                {
                    'error': str(e),
                    'code': 'DEVICE_CONFLICT',
                    'suggested_action': 'use_different_device_or_contact_support'
                }, 
                status=status.HTTP_409_CONFLICT
            )
            
        except BusinessLogicError as e:
            logger.warning(f"Business logic error: {str(e)}")
            return Response(
                {
                    'error': str(e),
                    'code': 'BUSINESS_RULE_VIOLATION',
                    'suggested_action': 'contact_support'
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            logger.error(
                f"PasswordlessAuth system error: {str(e)}",
                exc_info=True
            )
            return Response(
                {
                    'error': 'Authentication service unavailable',
                    'code': 'INTERNAL_ERROR',
                    'request_id': request.META.get('HTTP_X_REQUEST_ID', 'unknown'),
                    'suggested_action': 'try_again_later'
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _prepare_response_data(self, service_result: dict) -> dict:
        """Prepare response data from service result"""
        response = {
            "user": {
                "id": service_result['user']['id'],
                "username": service_result['user']['username'],
                "email": service_result['user']['email']
            },
            "client": {
                "id": service_result['client']['id'],
                "account": service_result['client']['account'],
                "display_name": service_result['client']['display_name'],
                "phone_number": service_result['client']['phone_number'],
                "balance": float(service_result['client']['balance']),
                "account_tier": service_result['client']['account_tier'],
                "status": service_result['client']['status'],
                "home_location": service_result['client']['home_location'],
                "current_location": service_result['client']['current_location']
            },
            "auth": {
                "access": service_result['auth']['access'],
                "refresh": service_result['auth']['refresh'],
                "token_type": service_result['auth']['token_type'],
                "expires_in": service_result['auth']['expires_in'],
                "refresh_expires_in": service_result['auth']['refresh_expires_in'],
                "correlation_id": service_result['auth'].get('correlation_id')
            },
            "metadata": {
                "is_new_user": service_result['metadata']['is_new_user'],
                "client_created": service_result['metadata']['client_created'],
                "processing_time_ms": service_result['metadata']['processing_time_ms'],
                "timestamp": service_result['metadata']['timestamp'],
                "location_detected": service_result['metadata']['location_detected'],
                "correlation_id": service_result['metadata']['correlation_id'],
                "token_expiry": service_result['metadata'].get('token_expiry'),
                "requires_otp": service_result['metadata'].get('requires_otp', False),
                "requires_password": service_result['metadata'].get('requires_password', False)
            }
        }
        
        # Add device info if available
        if service_result.get('device'):
            response["device"] = {
                "id": service_result['device']['id'],
                "mac_address": service_result['device']['mac_address'],
                "device_name": service_result['device']['device_name'],
                "is_owner": service_result['device']['is_owner'],
                "was_transferred": service_result['device']['was_transferred'],
                "is_trusted": service_result['device']['is_trusted']
            }
        
        # Add session info if available
        if service_result.get('session'):
            response["session"] = {
                "id": service_result['session']['id'],
                "session_id": service_result['session']['session_id'],
                "login_time": service_result['session']['login_time'],
                "is_owner": service_result['session']['is_owner'],
                "was_transferred": service_result['session']['was_transferred']
            }
        
        return response

    def _get_client_ip(self, request):
        """Extract client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def _get_routeros_redirect_url(self, service_result: dict, original_url: str) -> str:
        """Generate RouterOS redirect URL"""
        base_url = "https://your-hotspot-domain.com/routeros/callback"
        
        session_id = service_result.get('session', {}).get('session_id', '')
        mac_address = service_result.get('device', {}).get('mac_address', '')
        client_account = service_result['client']['account']
        
        params = {
            'username': client_account,
            'password': 'authenticated',
            'mac': mac_address,
            'session': session_id,
            'ip': service_result.get('device', {}).get('ip', ''),
            'ap': service_result['metadata'].get('ap_identifier', ''),
            'original_url': original_url,
            'timestamp': service_result['metadata']['timestamp']
        }
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items() if v])
        return f"{base_url}?{query_string}"


class SetupPasswordView(APIView):
    """
    Setup password for account (optional).
    """
    permission_classes = [IsAuthenticated]  # User must be authenticated

    def post(self, request):
        """
        Setup password for authenticated user.
        
        Expected data:
        - phone: User phone number (required)
        - password: New password (required, min 6 chars)
        
        Response:
        {
            "success": true,
            "message": "Password set up successfully"
        }
        """
        logger.info(
            f"SetupPassword request - "
            f"User: {request.user.username}"
        )
        
        # Validate serializer
        serializer = SetupPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"SetupPassword validation failed: {serializer.errors}")
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validated_data = serializer.validated_data
            phone = validated_data['phone']
            password = validated_data['password']
            
            # Verify phone matches authenticated user
            if request.user.username != phone:
                return Response(
                    {
                        'error': 'Phone does not match authenticated user',
                        'code': 'PHONE_MISMATCH'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Setup password using PasswordlessService
            result = PasswordlessService.setup_password(
                user=request.user,
                password=password
            )
            
            logger.info(f"Password setup successful for user: {request.user.username}")
            
            return Response(result, status=status.HTTP_200_OK)

        except BusinessLogicError as e:
            logger.warning(f"Password setup failed: {str(e)}")
            return Response(
                {
                    'error': str(e),
                    'code': 'SETUP_FAILED'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Password setup system error: {str(e)}", exc_info=True)
            return Response(
                {
                    'error': 'Password setup failed',
                    'code': 'SYSTEM_ERROR'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VerifyOTPView(APIView):
    """
    Verify OTP for additional security.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Verify OTP for authenticated session.
        
        Expected data:
        - phone: User phone number (required)
        - otp_code: 6-digit OTP (required)
        - session_id: Session ID from initial auth (required)
        
        Response:
        {
            "auth": { tokens... },
            "success": true
        }
        """
        logger.info(
            f"VerifyOTP request - "
            f"IP: {self._get_client_ip(request)}, "
            f"Phone: {request.data.get('phone', 'not provided')}"
        )
        
        # Validate serializer
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"VerifyOTP validation failed: {serializer.errors}")
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validated_data = serializer.validated_data
            phone = validated_data['phone']
            otp_code = validated_data['otp_code']
            session_id = validated_data['session_id']
            client_ip = self._get_client_ip(request)
            
            # Verify OTP using PasswordlessService
            result = PasswordlessService.verify_otp(
                phone=phone,
                otp_code=otp_code,
                session_id=session_id,
                ip_address=client_ip
            )
            
            logger.info(f"OTP verification successful for phone: {phone}")
            
            return Response(result, status=status.HTTP_200_OK)

        except AuthenticationError as e:
            logger.warning(f"OTP verification failed: {str(e)}")
            return Response(
                {
                    'error': str(e),
                    'code': 'INVALID_OTP',
                    'suggested_action': 'try_again_or_resend'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            logger.error(f"OTP verification system error: {str(e)}", exc_info=True)
            return Response(
                {
                    'error': 'OTP verification failed',
                    'code': 'SYSTEM_ERROR'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_client_ip(self, request):
        """Extract client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip