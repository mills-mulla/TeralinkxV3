# apps/security/services.py
import random
import string
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction
from rest_framework.authtoken.models import Token
from .models import PhoneOTP, AuthSession, SecurityLog
from users.models import ClientH
from core.services.client_service import ClientService
from twilio.rest import Client as TwilioClient

class OTPService:
    
    @staticmethod
    def generate_otp(length=6):
        """Generate a random numeric OTP"""
        return ''.join(random.choice(string.digits) for _ in range(length))
    
    @staticmethod
    def generate_session_token(length=32):
        """Generate a random session token"""
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
    
    @staticmethod
    def create_otp(phone_number, purpose='login'):
        """Create a new OTP for a phone number"""
        # Clean up expired OTPs
        PhoneOTP.cleanup_expired()
        
        # Invalidate previous unused OTPs for this phone
        PhoneOTP.objects.filter(
            phone_number=phone_number,
            is_used=False,
            expires_at__gt=timezone.now()
        ).update(is_used=True)
        
        # Generate new OTP
        otp = OTPService.generate_otp()
        
        # Create OTP record
        phone_otp = PhoneOTP.objects.create(
            phone_number=phone_number,
            otp=otp,
            expires_at=timezone.now() + timedelta(minutes=10),
            purpose=purpose
        )
        
        return phone_otp
    
    @staticmethod
    def send_otp_sms(phone_number, otp):
        """Send OTP via SMS"""
        try:
            # For development, print OTP to console
            print(f"[OTP] {phone_number}: {otp}")
            
            # For production, integrate with your SMS provider
            if getattr(settings, 'TWILIO_ACCOUNT_SID', None):
                client = TwilioClient(
                    settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN
                )
                
                message = client.messages.create(
                    body=f"Your verification code is: {otp}. Valid for 10 minutes.",
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to=phone_number
                )
                return True, message.sid
            else:
                return True, "OTP generated (check console)"
                
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def verify_otp(phone_number, otp, purpose='login'):
        """Verify an OTP for a phone number"""
        try:
            phone_otp = PhoneOTP.objects.get(
                phone_number=phone_number,
                otp=otp,
                is_used=False,
                expires_at__gt=timezone.now(),
                purpose=purpose
            )
            
            # Check attempt limit
            if phone_otp.attempt_count >= 5:
                phone_otp.mark_used()
                return False, "Too many attempts. Please request a new OTP."
            
            phone_otp.increment_attempt()
            
            # Mark OTP as used
            phone_otp.mark_used()
            return True, "OTP verified successfully"
            
        except PhoneOTP.DoesNotExist:
            return False, "Invalid or expired OTP"
    
    @staticmethod
    def create_auth_session(phone_number, auth_method='otp', request=None):
        """Create a new authentication session"""
        # Clean up expired sessions
        AuthSession.objects.filter(
            expires_at__lt=timezone.now(),
            status__in=['pending', 'otp_sent', 'otp_verified', 'password_verified']
        ).update(status='expired')
        
        # Create new session
        session = AuthSession.objects.create(
            phone_number=phone_number,
            session_token=OTPService.generate_session_token(),
            expires_at=timezone.now() + timedelta(minutes=15),
            auth_method=auth_method,
            status='otp_sent' if auth_method == 'otp' else 'pending'
        )
        
        # Add request info if available
        if request:
            session.ip_address = request.META.get('REMOTE_ADDR')
            session.user_agent = request.META.get('HTTP_USER_AGENT', '')
            session.save()
        
        return session
    
    @staticmethod
    def validate_session(session_token):
        """Validate an authentication session"""
        try:
            session = AuthSession.objects.get(
                session_token=session_token,
                expires_at__gt=timezone.now(),
                status__in=['otp_sent', 'otp_verified', 'password_verified', 'pending']
            )
            return True, session
        except AuthSession.DoesNotExist:
            return False, "Invalid or expired session"


class AuthManager:
    
    @staticmethod
    def get_auth_options(phone_number):
        """Get available authentication options for phone number"""
        user_exists = User.objects.filter(username=phone_number).exists()
        
        options = {
            'phone': phone_number,
            'user_exists': user_exists,
            'methods': []
        }
        
        # Always allow OTP
        options['methods'].append({
            'method': 'otp',
            'name': 'OTP Verification',
            'description': 'Receive a code via SMS',
            'available': True
        })
        
        # Only allow password if user exists AND has password set
        if user_exists:
            user = User.objects.get(username=phone_number)
            has_password = bool(user.password)  # Check if password is set
            options['methods'].append({
                'method': 'password',
                'name': 'Password',
                'description': 'Use your password',
                'available': has_password
            })
        
        return options
    
    @staticmethod
    def authenticate_with_password(phone_number, password, request=None):
        """Authenticate user with password"""
        try:
            user = User.objects.get(username=phone_number)
            
            # Check if user has password set
            if not user.password:
                return False, "Password not set. Please use OTP authentication."
            
            # Verify password
            if check_password(password, user.password):
                # Create auth session
                session = AuthSession.objects.create(
                    phone_number=phone_number,
                    session_token=OTPService.generate_session_token(),
                    expires_at=timezone.now() + timedelta(hours=24),
                    auth_method='password',
                    status='password_verified',
                    user=user,
                    ip_address=request.META.get('REMOTE_ADDR') if request else None,
                    user_agent=request.META.get('HTTP_USER_AGENT', '') if request else ''
                )
                
                # Generate or get token
                token, _ = Token.objects.get_or_create(user=user)
                session.auth_token = token.key
                session.save()
                
                # Log successful authentication
                SecurityLog.objects.create(
                    user=getattr(user, 'clienth', None),
                    action_type='login_success',
                    action_category='authentication',
                    description=f"Password authentication successful for {phone_number}",
                    severity='info',
                    ip_address=request.META.get('REMOTE_ADDR') if request else None,
                    details={
                        'auth_method': 'password',
                        'session_id': str(session.id)
                    }
                )
                
                return True, {
                    'user': user,
                    'token': token.key,
                    'session': session
                }
            
            return False, "Invalid password"
            
        except User.DoesNotExist:
            return False, "User not found"
    
    @staticmethod
    @transaction.atomic
    def create_user_from_otp(phone_number, client_data=None, request=None):
        """Create user after OTP verification"""
        # Create user
        user = User.objects.create_user(
            username=phone_number,
            email=client_data.get('email', f'{phone_number}@teralinkx.net') if client_data else f'{phone_number}@teralinkx.net',
            password=client_data.get('password') if client_data else None,
            first_name=client_data.get('display_name', '').split(' ')[0] if client_data else ''
        )
        
        # Generate auth token
        token = Token.objects.create(user=user)
        
        # Create client profile using existing service
        client_service_data = {
            'phone': phone_number,
            'current_ip': request.META.get('REMOTE_ADDR') if request else None,
            'current_mac': client_data.get('current_mac') if client_data else None,
            'display_name': client_data.get('display_name', f'User_{phone_number[-4:]}') if client_data else f'User_{phone_number[-4:]}'
        }
        
        if client_data and 'email' in client_data:
            client_service_data['email'] = client_data['email']
        
        _, client, _, _ = ClientService.create_user_and_client(client_service_data)
        
        # Create authenticated session
        session = AuthSession.objects.create(
            phone_number=phone_number,
            session_token=OTPService.generate_session_token(),
            expires_at=timezone.now() + timedelta(hours=24),
            auth_method='otp',
            status='authenticated',
            user=user,
            auth_token=token.key,
            ip_address=request.META.get('REMOTE_ADDR') if request else None,
            user_agent=request.META.get('HTTP_USER_AGENT', '') if request else ''
        )
        
        # Log user creation
        SecurityLog.objects.create(
            user=client,
            action_type='login_success',
            action_category='authentication',
            description=f"New user created via OTP: {phone_number}",
            severity='info',
            ip_address=request.META.get('REMOTE_ADDR') if request else None,
            details={
                'auth_method': 'otp',
                'is_new_user': True,
                'session_id': str(session.id)
            }
        )
        
        return user, client, token, session
    
    @staticmethod
    def complete_otp_authentication(phone_number, session, request=None):
        """Complete OTP authentication for existing user"""
        try:
            user = User.objects.get(username=phone_number)
            
            # Generate or get token
            token, _ = Token.objects.get_or_create(user=user)
            
            # Update session
            session.mark_authenticated(user=user, auth_token=token.key)
            session.ip_address = request.META.get('REMOTE_ADDR') if request else None
            session.user_agent = request.META.get('HTTP_USER_AGENT', '') if request else ''
            session.save()
            
            # Log successful authentication
            SecurityLog.objects.create(
                user=getattr(user, 'clienth', None),
                action_type='login_success',
                action_category='authentication',
                description=f"OTP authentication successful for {phone_number}",
                severity='info',
                ip_address=request.META.get('REMOTE_ADDR') if request else None,
                details={
                    'auth_method': 'otp',
                    'is_new_user': False,
                    'session_id': str(session.id)
                }
            )
            
            return True, {
                'user': user,
                'token': token.key,
                'session': session,
                'is_new_user': False
            }
            
        except User.DoesNotExist:
            return False, "User not found"