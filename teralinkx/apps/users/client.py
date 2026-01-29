# users/client_view.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
import logging

from core.serializers.client_serializer import ClientSerializer
from core.services.client_service import ClientService
from core.exceptions import (
    BusinessLogicError,
    AuthenticationError,
    DeviceConflictError
)

logger = logging.getLogger(__name__)


class ClientView(APIView):
    """
    Client authentication and registration endpoint with JWT support.
    
    Handles both login and signup.
    Creates User, ClientH, UserDevice, and UserSession records.
    Returns JWT tokens for authentication.
    """
    permission_classes = [AllowAny]
    authentication_classes = []  # Explicitly disable authentication for this endpoint

    def post(self, request):
        """
        Authenticate or register a client with JWT tokens.
        
        Expected data:
        - phone: User phone number (required)
        - password: User password (required)
        - current_mac: Device MAC address (optional)
        - current_ip: Device IP address (optional)
        - display_name: User display name (optional, for new users)
        """
        # Log incoming request
        logger.info(
            f"ClientView request - "
            f"IP: {self._get_client_ip(request)}, "
            f"Method: {request.method}, "
            f"Path: {request.path}"
        )
        
        # Validate serializer
        serializer = ClientSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            logger.warning(f"Validation failed: {serializer.errors}")
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Extract RouterOS parameters from query string (for future integration)
            ap_identifier = request.GET.get('ap') or request.GET.get('ssid')
            original_url = request.GET.get('url', '')
            
            # Get user agent for security logging
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            client_ip = self._get_client_ip(request)
            print(client_ip)
            # Extract validated data
            validated_data = serializer.validated_data
            
            # Use production-grade service with JWT support
            result = ClientService.authenticate_or_register(
                phone=validated_data['phone'],
                password=validated_data['password'],
                current_mac=validated_data.get('current_mac'),
                current_ip=validated_data.get('current_ip') or client_ip,
                ap_identifier=ap_identifier,
                display_name=validated_data.get('display_name'),
                conflict_resolution='transfer',  # business rule
                user_agent=user_agent,
                request_metadata={
                    'user_agent': user_agent,
                    'client_ip': client_ip,
                    'referer': request.META.get('HTTP_REFERER', ''),
                    'content_type': request.content_type,
                    'method': request.method,
                    'ap_identifier': ap_identifier,
                    'original_url': original_url,
                    'query_params': dict(request.GET),
                    'is_routeros': bool(ap_identifier)  # Flag for RouterOS requests
                }
            )
            
            # Prepare response with JWT tokens
            response_data = self._prepare_response_data(result)
            
            # Add RouterOS-specific response if needed (for future integration)
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
                f"Authentication successful - "
                f"Account: {result['client']['account']}, "
                f"New User: {result['metadata']['is_new_user']}, "
                f"Token Type: {result['auth']['token_type']}, "
                f"Time: {result['metadata']['processing_time_ms']}ms"
            )
            
            return Response(
                response_data, 
                status=status.HTTP_200_OK
            )

        except AuthenticationError as e:
            # Invalid credentials
            logger.warning(f"Authentication failed: {str(e)}")
            return Response(
                {
                    'error': str(e),
                    'code': 'AUTH_FAILED',
                    'suggested_action': 'check_credentials'
                }, 
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        except DeviceConflictError as e:
            # Device already registered to another user
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
            # Business rule violation (device limits, etc.)
            logger.warning(f"Business logic error: {str(e)}")
            return Response(
                {
                    'error': str(e),
                    'code': 'BUSINESS_RULE_VIOLATION',
                    'suggested_action': 'upgrade_account_or_contact_support'
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            # System error
            logger.error(
                f"System error in ClientView: {str(e)}",
                exc_info=True
            )
            return Response(
                {
                    'error': 'Internal server error',
                    'code': 'INTERNAL_ERROR',
                    'request_id': request.META.get('HTTP_X_REQUEST_ID', 'unknown'),
                    'suggested_action': 'try_again_later'
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _prepare_response_data(self, service_result: dict) -> dict:
        """Prepare standardized response data from service result with JWT"""
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
                "access": service_result['auth']['access'],  # JWT access token
                "refresh": service_result['auth']['refresh'],  # JWT refresh token
                "token_type": service_result['auth']['token_type'],  # Should be 'Bearer'
                "expires_in": service_result['auth']['expires_in'],  # Seconds until expiration
                "refresh_expires_in": service_result['auth']['refresh_expires_in'],  # Refresh token expiration
                "correlation_id": service_result['auth'].get('correlation_id')
            },
            "metadata": {
                "is_new_user": service_result['metadata']['is_new_user'],
                "client_created": service_result['metadata']['client_created'],
                "processing_time_ms": service_result['metadata']['processing_time_ms'],
                "timestamp": service_result['metadata']['timestamp'],
                "location_detected": service_result['metadata']['location_detected'],
                "correlation_id": service_result['metadata']['correlation_id'],
                "token_expiry": service_result['metadata'].get('token_expiry')
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
        """
        Generate redirect URL for RouterOS after successful authentication.
        
        RouterOS expects specific parameters to allow network access.
        """
        # Base URL for RouterOS callback
        base_url = "https://your-hotspot-domain.com/routeros/callback"
        
        # Extract necessary parameters
        session_id = service_result.get('session', {}).get('session_id', '')
        mac_address = service_result.get('device', {}).get('mac_address', '')
        client_account = service_result['client']['account']
        
        # Build RouterOS parameters
        params = {
            'username': client_account,
            'password': 'authenticated',  # Flag for RouterOS
            'mac': mac_address,
            'session': session_id,
            'ip': service_result.get('device', {}).get('ip', ''),
            'ap': service_result['metadata'].get('ap_identifier', ''),
            'original_url': original_url,
            'timestamp': service_result['metadata']['timestamp']
        }
        
        # Convert to query string
        query_string = '&'.join([f"{k}={v}" for k, v in params.items() if v])
        
        return f"{base_url}?{query_string}"

    def get(self, request):
        """
        Health check and service information endpoint.
        """
        return Response({
            "service": "Client Authentication API",
            "version": "2.0.0",
            "status": "operational",
            "authentication": "JWT (JSON Web Tokens)",
            "capabilities": [
                "user_authentication",
                "user_registration", 
                "device_management",
                "session_creation",
                "jwt_token_generation",
                "token_refresh",
                "routeros_integration"
            ],
            "endpoints": {
                "POST /api/client/": "Authenticate or register client (returns JWT)",
                "POST /api/token/refresh/": "Refresh JWT tokens",
                "POST /api/logout/": "Logout and blacklist tokens",
                "GET /api/client/": "Service information (this endpoint)"
            },
            "jwt_configuration": {
                "access_token_lifetime": "30 minutes",
                "refresh_token_lifetime": "7 days",
                "token_type": "Bearer",
                "requires_csrf": False
            },
            "timestamp": timezone.now().isoformat()
        })


class TokenRefreshView(APIView):
    """
    JWT token refresh endpoint.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Refresh JWT tokens.
        
        Expected data:
        - refresh: JWT refresh token (required)
        - device_mac: Device MAC address (optional, for validation)
        """
        refresh_token = request.data.get('refresh')
        device_mac = request.data.get('device_mac')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        client_ip = self._get_client_ip(request)
        
        if not refresh_token:
            return Response(
                {
                    'error': 'Refresh token is required',
                    'code': 'REFRESH_TOKEN_REQUIRED'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            result = ClientService.refresh_token(
                refresh_token=refresh_token,
                device_mac=device_mac,
                ip_address=client_ip,
                user_agent=user_agent
            )
            
            logger.info(
                f"Token refresh successful - "
                f"IP: {client_ip}, "
                f"Device MAC: {device_mac or 'not provided'}"
            )
            
            return Response(result, status=status.HTTP_200_OK)
            
        except AuthenticationError as e:
            logger.warning(f"Token refresh failed: {str(e)}")
            return Response(
                {
                    'error': str(e),
                    'code': 'INVALID_REFRESH_TOKEN',
                    'suggested_action': 'reauthenticate'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        except BusinessLogicError as e:
            logger.warning(f"Token refresh business error: {str(e)}")
            return Response(
                {
                    'error': str(e),
                    'code': 'TOKEN_REFRESH_FAILED',
                    'suggested_action': 'try_again'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Token refresh system error: {str(e)}", exc_info=True)
            return Response(
                {
                    'error': 'Token refresh failed',
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


class LogoutView(APIView):
    """
    Logout endpoint to blacklist JWT tokens.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Logout user and blacklist JWT refresh token.
        
        Expected data:
        - refresh: JWT refresh token (optional, but recommended)
        """
        refresh_token = request.data.get('refresh')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        client_ip = self._get_client_ip(request)
        
        try:
            result = ClientService.logout_user(
                user=request.user,
                refresh_token=refresh_token,
                ip_address=client_ip,
                user_agent=user_agent
            )
            
            logger.info(
                f"Logout successful - "
                f"User: {request.user.username}, "
                f"Sessions terminated: {result.get('sessions_terminated', 0)}"
            )
            
            return Response(result, status=status.HTTP_200_OK)
            
        except BusinessLogicError as e:
            logger.warning(f"Logout failed: {str(e)}")
            return Response(
                {
                    'error': str(e),
                    'code': 'LOGOUT_FAILED'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Logout system error: {str(e)}", exc_info=True)
            return Response(
                {
                    'error': 'Logout failed',
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


class TokenVerifyView(APIView):
    """
    JWT token verification endpoint.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Verify JWT token validity.
        
        Expected data:
        - token: JWT token to verify (required)
        """
        token = request.data.get('token')
        
        if not token:
            return Response(
                {
                    'error': 'Token is required',
                    'code': 'TOKEN_REQUIRED'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Use ClientService to decode and validate
            result = ClientService.decode_and_validate_jwt(
                token=token,
                require_device_match=False
            )
            
            return Response(
                {
                    'valid': True,
                    'client_account': result.get('client_account'),
                    'device_mac': result.get('device_mac'),
                    'session_id': result.get('session_id')
                },
                status=status.HTTP_200_OK
            )
            
        except AuthenticationError as e:
            return Response(
                {
                    'valid': False,
                    'error': str(e),
                    'code': 'INVALID_TOKEN'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            return Response(
                {
                    'valid': False,
                    'error': 'Token verification failed',
                    'code': 'VERIFICATION_ERROR'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SessionValidationView(APIView):
    """
    Session validation endpoint.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Validate if a session is still active.
        
        Expected data:
        - session_id: Session ID to validate (required)
        """
        session_id = request.data.get('session_id')
        
        if not session_id:
            return Response(
                {
                    'error': 'Session ID is required',
                    'code': 'SESSION_ID_REQUIRED'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        client_ip = self._get_client_ip(request)
        
        try:
            result = ClientService.validate_session(
                session_id=session_id,
                ip_address=client_ip,
                user_agent=user_agent
            )
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Session validation error: {str(e)}")
            return Response(
                {
                    'valid': False,
                    'error': 'Session validation failed',
                    'code': 'VALIDATION_ERROR'
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