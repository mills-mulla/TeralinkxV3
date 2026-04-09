# apps/security/auth_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from users.models import ClientH

from .serializers import (
    PhoneAuthSerializer,
    RequestOTPSerializer,
    VerifyOTPSerializer,
    PasswordLoginSerializer,
    CompleteSignupSerializer
)
from .services import OTPService, AuthManager
from .models import SecurityLog

# Your existing MeView (moved/updated)
@method_decorator(csrf_exempt, name='dispatch')
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        client = getattr(user, 'clienth', None)

        return Response({
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "client": {
                "account": client.account if client else None,
                "ip": client.current_ip_address if client else None,
                "balance": float(client.balance) if client else None,
                "status": client.status if client else None,
                "voucher_expiry": client.voucher_expiry if client else None,
                "display_name": client.display_name if client else None,
                "phone_number": client.phone_number if client else None,
            }
        })


# New Authentication Views
@method_decorator(csrf_exempt, name='dispatch')
class AuthOptionsView(APIView):
    """
    Get authentication options for a phone number
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PhoneAuthSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        phone = serializer.validated_data['phone']
        method = serializer.validated_data.get('method')
        
        # Get available authentication methods
        options = AuthManager.get_auth_options(phone)
        
        # If specific method requested
        if method:
            method_info = next((m for m in options['methods'] if m['method'] == method), None)
            if not method_info:
                return Response({
                    'error': f'Method {method} not available for this phone number'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not method_info.get('available', True):
                return Response({
                    'error': f'Method {method} is not available. Please use another method.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                'phone': phone,
                'selected_method': method_info
            })
        
        return Response(options)


@method_decorator(csrf_exempt, name='dispatch')
class RequestOTPView(APIView):
    """
    Request OTP for phone verification
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        phone = serializer.validated_data['phone']
        purpose = serializer.validated_data['purpose']
        
        # Check if user exists for signup purpose
        if purpose == 'signup' and User.objects.filter(username=phone).exists():
            return Response({
                'error': 'User already exists. Please use login instead.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create OTP
        otp_record = OTPService.create_otp(phone, purpose)
        
        # Send OTP via SMS
        success, message = OTPService.send_otp_sms(phone, otp_record.otp)
        
        if not success:
            return Response({
                'error': f'Failed to send OTP: {message}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Create auth session
        session = OTPService.create_auth_session(phone, auth_method='otp', request=request)
        
        # Log OTP request
        SecurityLog.objects.create(
            action_type='login_success' if purpose == 'login' else 'system',
            action_category='authentication',
            description=f"OTP requested for {phone}",
            severity='info',
            ip_address=request.META.get('REMOTE_ADDR'),
            details={
                'phone': phone,
                'purpose': purpose,
                'session_id': str(session.id)
            }
        )
        
        return Response({
            'message': 'OTP sent successfully',
            'session_token': session.session_token,
            'phone': phone,
            'purpose': purpose,
            'expires_in': 600  # 10 minutes
        })


@method_decorator(csrf_exempt, name='dispatch')
class VerifyOTPView(APIView):
    """
    Verify OTP and proceed with authentication/signup
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        phone = serializer.validated_data['phone']
        otp = serializer.validated_data['otp']
        session_token = serializer.validated_data['session_token']
        purpose = serializer.validated_data['purpose']
        
        # Validate session
        valid_session, session = OTPService.validate_session(session_token)
        if not valid_session:
            return Response({
                'error': session
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify OTP
        success, message = OTPService.verify_otp(phone, otp, purpose)
        
        if not success:
            # Update session status
            session.mark_failed(message)
            return Response({
                'error': message
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update session status
        session.status = 'otp_verified'
        session.save()
        
        # Handle based on purpose
        if purpose == 'login':
            # Check if user exists
            user_exists = User.objects.filter(username=phone).exists()
            
            if user_exists:
                # Complete authentication for existing user
                success, result = AuthManager.complete_otp_authentication(phone, session, request)
                
                if not success:
                    return Response({
                        'error': result
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                user = result['user']
                client = getattr(user, 'clienth', None)
                
                return Response({
                    'success': True,
                    'message': 'Login successful',
                    'token': result['token'],
                    'session_token': session_token,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name
                    },
                    'client': {
                        'account': client.account if client else None,
                        'display_name': client.display_name if client else None,
                        'phone_number': client.phone_number if client else None,
                        'balance': float(client.balance) if client else None,
                        'status': client.status if client else None
                    } if client else None
                })
            else:
                # User doesn't exist - requires signup
                return Response({
                    'success': True,
                    'message': 'OTP verified. User does not exist.',
                    'requires_signup': True,
                    'session_token': session_token,
                    'phone': phone
                })
        
        elif purpose == 'signup':
            # OTP verified for signup
            return Response({
                'success': True,
                'message': 'OTP verified for signup',
                'requires_signup': True,
                'session_token': session_token,
                'phone': phone
            })
        
        return Response({
            'error': 'Invalid purpose'
        }, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class PasswordLoginView(APIView):
    """
    Authenticate using password
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PasswordLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        phone = serializer.validated_data['phone']
        password = serializer.validated_data['password']
        
        # Authenticate with password
        success, result = AuthManager.authenticate_with_password(phone, password, request)
        
        if not success:
            return Response({
                'error': result
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = result['user']
        client = getattr(user, 'clienth', None)
        
        return Response({
            'success': True,
            'message': 'Authentication successful',
            'token': result['token'],
            'session_token': result['session'].session_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            },
            'client': {
                'account': client.account if client else None,
                'display_name': client.display_name if client else None,
                'phone_number': client.phone_number if client else None,
                'balance': float(client.balance) if client else None,
                'status': client.status if client else None
            } if client else None
        })


@method_decorator(csrf_exempt, name='dispatch')
class CompleteSignupView(APIView):
    """
    Complete signup after OTP verification
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = CompleteSignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        session_token = serializer.validated_data['session_token']
        
        # Validate session
        valid_session, session = OTPService.validate_session(session_token)
        if not valid_session or session.status != 'otp_verified':
            return Response({
                'error': 'Invalid or expired session'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        phone = session.phone_number
        
        # Check if user already exists
        if User.objects.filter(username=phone).exists():
            return Response({
                'error': 'User already exists. Please login instead.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                # Prepare client data
                client_data = {
                    'email': serializer.validated_data.get('email'),
                    'display_name': serializer.validated_data.get('display_name'),
                    'password': serializer.validated_data.get('password'),
                    'current_ip': serializer.validated_data.get('current_ip'),
                    'current_mac': serializer.validated_data.get('current_mac')
                }
                
                # Remove None values
                client_data = {k: v for k, v in client_data.items() if v is not None}
                
                # Create user and client
                user, client, token, session = AuthManager.create_user_from_otp(
                    phone, 
                    client_data, 
                    request
                )
                
                return Response({
                    'success': True,
                    'message': 'Signup successful',
                    'token': token.key,
                    'session_token': session.session_token,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name
                    },
                    'client': {
                        'account': client.account,
                        'display_name': client.display_name,
                        'phone_number': client.phone_number,
                        'balance': float(client.balance),
                        'status': client.status
                    }
                })
                
        except Exception as e:
            return Response({
                'error': f'Signup failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    """
    Logout and invalidate token
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Delete the token
            Token.objects.filter(user=request.user).delete()
            
            # Log the logout
            SecurityLog.objects.create(
                user=getattr(request.user, 'clienth', None),
                action_type='logout',
                action_category='authentication',
                description=f"User logged out: {request.user.username}",
                severity='info',
                ip_address=request.META.get('REMOTE_ADDR'),
                details={
                    'username': request.user.username
                }
            )
            
            return Response({
                'message': 'Successfully logged out'
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)