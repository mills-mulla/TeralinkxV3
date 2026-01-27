import random
import string
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from twilio.rest import Client as TwilioClient
from .models import PhoneOTP, VerificationSession

class OTPService:
    
    @staticmethod
    def generate_otp(length=6):
        """Generate a random numeric OTP"""
        return ''.join(random.choice(string.digits) for _ in range(length))
    
    @staticmethod
    def create_otp(phone_number, purpose='login'):
        """Create a new OTP for a phone number"""
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
        """Send OTP via SMS using Twilio (or any other provider)"""
        try:
            # Configure your SMS provider here
            # For Twilio:
            if hasattr(settings, 'TWILIO_ACCOUNT_SID') and settings.TWILIO_ACCOUNT_SID:
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
                # For development, just print the OTP
                print(f"OTP for {phone_number}: {otp}")
                return True, "DEV_MODE"
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
                return False, "Too many attempts. Please request a new OTP."
            
            phone_otp.mark_used()
            return True, "OTP verified successfully"
            
        except PhoneOTP.DoesNotExist:
            return False, "Invalid or expired OTP"
    
    @staticmethod
    def create_verification_session(phone_number):
        """Create a new verification session"""
        # Invalidate previous sessions
        VerificationSession.objects.filter(
            phone_number=phone_number,
            is_completed=False
        ).update(is_completed=True)
        
        # Create new session
        session = VerificationSession.objects.create(
            phone_number=phone_number,
            session_token=OTPService.generate_session_token(),
            expires_at=timezone.now() + timedelta(minutes=15),
            next_step='otp_sent'
        )
        
        return session
    
    @staticmethod
    def generate_session_token(length=32):
        """Generate a random session token"""
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


class AuthService:
    
    @staticmethod
    def get_auth_methods(phone_number):
        """Get available authentication methods for a phone number"""
        from django.contrib.auth.models import User
        
        methods = []
        
        # Check if user exists
        try:
            user = User.objects.get(username=phone_number)
            methods.append('password')
            methods.append('otp')
        except User.DoesNotExist:
            # New user - only OTP
            methods.append('otp')
        
        return methods
    
    @staticmethod
    def verify_password(phone_number, password):
        """Verify password for a user"""
        from django.contrib.auth.models import User
        from django.contrib.auth.hashers import check_password
        
        try:
            user = User.objects.get(username=phone_number)
            if check_password(password, user.password):
                return True, user
            return False, "Invalid password"
        except User.DoesNotExist:
            return False, "User not found"