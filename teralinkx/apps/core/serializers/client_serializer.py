# core/serializers/client_serializer.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
import re

User = get_user_model()

class ClientSerializer(serializers.Serializer):
    """
    Serializer for client authentication/registration with JWT support.
    """
    
    phone = serializers.CharField(
        max_length=20,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be 9-15 digits with optional country code."
            )
        ],
        help_text="User phone number (used as username)"
    )
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=6,
        max_length=128,
        help_text="Password for authentication/registration"
    )
    
    current_ip = serializers.IPAddressField(
        required=False,
        allow_blank=True,
        help_text="Current device IP address"
    )
    
    current_mac = serializers.CharField(
        max_length=17,
        required=False,
        allow_blank=True,
        help_text="Device MAC address"
    )
    
    display_name = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text="Display name for new users"
    )
    
    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        help_text="Email address (optional for new users)"
    )
    
    # Optional fields for additional context
    ap_identifier = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        help_text="Access point identifier"
    )
    
    user_agent = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="User agent string for logging"
    )
    
    def validate_phone(self, value):
        """
        Clean and validate phone number.
        """
        # Remove any non-digit characters except leading +
        cleaned = re.sub(r'[^\d\+]', '', value)
        
        # Ensure we have at least 10 digits
        digits = re.sub(r'\D', '', cleaned)
        if len(digits) < 10:
            raise serializers.ValidationError(
                "Phone number must contain at least 10 digits"
            )
        
        # If no country code, assume kenya (+254)
        if not cleaned.startswith('+'):
            if digits.startswith('0'):
                # Convert 0XXXXXXXXX to +254XXXXXXXXX
                cleaned = '+254' + digits[1:]
            else:
                cleaned = '+' + digits
        
        return cleaned
    
    def validate_current_mac(self, value):
        """
        Validate and format MAC address.
        No uniqueness check to allow device transfers.
        """
        if not value or value.strip() == '':
            return ''
        
        # Remove any separators and convert to uppercase
        cleaned = value.replace(':', '').replace('-', '').replace('.', '').upper()
        
        # Validate length
        if len(cleaned) != 12:
            raise serializers.ValidationError(
                "MAC address must be 12 hexadecimal characters"
            )
        
        # Validate hexadecimal
        try:
            int(cleaned, 16)
        except ValueError:
            raise serializers.ValidationError(
                "MAC address must contain only hexadecimal characters (0-9, A-F)"
            )
        
        # Format as standard MAC (AA:BB:CC:DD:EE:FF)
        formatted = ':'.join(cleaned[i:i+2] for i in range(0, 12, 2))
        return formatted
    
    def validate_password(self, value):
        """
        Basic password strength validation.
        """
        if len(value) < 6:
            raise serializers.ValidationError(
                "Password must be at least 6 characters long"
            )
        
        return value
    
    def validate(self, data):
        """
        Additional cross-field validation.
        """
        # Check if user exists (for informational purposes only)
        phone = data.get('phone')
        
        if User.objects.filter(username=phone).exists():
            user = User.objects.get(username=phone)
            data['user_exists'] = True
            data['existing_user'] = user
        else:
            data['user_exists'] = False
            data['existing_user'] = None
        
        # For new users, require display_name
        if not data['user_exists'] and not data.get('display_name'):
            raise serializers.ValidationError({
                "display_name": "Display name is required for new users"
            })
        
        return data
    
    def to_internal_value(self, data):
        """
        Override to handle empty strings as None for optional fields.
        """
        # Convert empty strings to None for optional fields
        optional_fields = ['current_ip', 'current_mac', 'display_name', 
                          'email', 'ap_identifier', 'user_agent']
        
        for field in optional_fields:
            if field in data and data[field] == '':
                data[field] = None
        
        return super().to_internal_value(data)


class TokenRefreshSerializer(serializers.Serializer):
    """
    Serializer for JWT token refresh.
    """
    refresh = serializers.CharField(
        required=True,
        help_text="JWT refresh token"
    )
    device_mac = serializers.CharField(
        required=False,
        max_length=17,
        help_text="Device MAC address for validation (optional)"
    )


class LogoutSerializer(serializers.Serializer):
    """
    Serializer for logout request.
    """
    refresh = serializers.CharField(
        required=False,
        help_text="JWT refresh token to blacklist (optional but recommended)"
    )


class TokenVerifySerializer(serializers.Serializer):
    """
    Serializer for token verification.
    """
    token = serializers.CharField(
        required=True,
        help_text="JWT token to verify"
    )


class SessionValidationSerializer(serializers.Serializer):
    """
    Serializer for session validation.
    """
    session_id = serializers.CharField(
        required=True,
        help_text="Session ID to validate"
    )