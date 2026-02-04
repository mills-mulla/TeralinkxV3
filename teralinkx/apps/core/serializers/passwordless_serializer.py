# core/serializers/passwordless_serializer.py
from rest_framework import serializers
from django.core.validators import RegexValidator
import re

class AccountCheckSerializer(serializers.Serializer):
    """Serializer for checking account status"""
    phone = serializers.CharField(
        max_length=16,  # Increased for +254XXXXXXXXX
        validators=[
            RegexValidator(
                regex=r'^(\+?254\d{9}|\d{9,12})$',
                message='Phone must be a valid Kenyan number'
            )
        ]
    )
    current_ip = serializers.IPAddressField(required=False)
    current_mac = serializers.CharField(
        max_length=17,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$',
                message='Enter a valid MAC address'
            )
        ]
    )

    def validate_phone(self, value):
        """Ensure phone is in correct format"""
        # Remove any spaces, dashes, or + signs
        cleaned = re.sub(r'[\s\-\+]+', '', value)
        
        # If starts with 0, replace with 254
        if cleaned.startswith('0'):
            cleaned = '254' + cleaned[1:]
        
        # Ensure it's 12 digits (254 + 9 digits)
        if not cleaned.startswith('254') or len(cleaned) != 12:
            raise serializers.ValidationError('Phone must be in format 254XXXXXXXXX')
        
        return '+' + cleaned  # Return with + prefix for consistency


class PasswordlessAuthSerializer(serializers.Serializer):
    """Serializer for passwordless authentication"""
    phone = serializers.CharField(
        max_length=16,  # Increased for +254XXXXXXXXX
        validators=[
            RegexValidator(
                regex=r'^(\+?254\d{9}|\d{9,12})$',
                message='Phone must be a valid Kenyan number'
            )
        ]
    )
    password = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=128,
        min_length=6
    )
    current_ip = serializers.IPAddressField(required=False)
    current_mac = serializers.CharField(
        max_length=17,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$',
                message='Enter a valid MAC address'
            )
        ]
    )
    device_info = serializers.JSONField(required=False)

    def validate(self, data):
        """Custom validation"""
        phone = data.get('phone')
        password = data.get('password', '')
        
        # Validate phone format - handle + prefix
        cleaned = re.sub(r'[\s\-\+]+', '', phone)
        if cleaned.startswith('0'):
            cleaned = '254' + cleaned[1:]
        
        if not cleaned.startswith('254') or len(cleaned) != 12:
            raise serializers.ValidationError({'phone': 'Phone must be in format 254XXXXXXXXX'})
        
        data['phone'] = '+' + cleaned  # Store with + prefix
        
        # If password is provided but empty string, remove it
        if password == '':
            data.pop('password', None)
        
        return data


class SetupPasswordSerializer(serializers.Serializer):
    """Serializer for setting up password"""
    phone = serializers.CharField(
        max_length=16,  # Increased for +254XXXXXXXXX
        validators=[
            RegexValidator(
                regex=r'^(\+?254\d{9}|\d{9,12})$',
                message='Phone must be a valid Kenyan number'
            )
        ]
    )
    password = serializers.CharField(
        max_length=128,
        min_length=6,
        write_only=True
    )

    def validate_phone(self, value):
        """Ensure phone is in correct format"""
        cleaned = re.sub(r'[\s\-\+]+', '', value)
        if cleaned.startswith('0'):
            cleaned = '254' + cleaned[1:]
        
        if not cleaned.startswith('254') or len(cleaned) != 12:
            raise serializers.ValidationError('Phone must be in format 254XXXXXXXXX')
        
        return '+' + cleaned


class VerifyOTPSerializer(serializers.Serializer):
    """Serializer for OTP verification"""
    phone = serializers.CharField(
        max_length=16,  # Increased for +254XXXXXXXXX
        validators=[
            RegexValidator(
                regex=r'^(\+?254\d{9}|\d{9,12})$',
                message='Phone must be a valid Kenyan number'
            )
        ]
    )
    otp_code = serializers.CharField(
        max_length=6,
        min_length=6,
        validators=[
            RegexValidator(
                regex=r'^\d{6}$',
                message='OTP must be 6 digits'
            )
        ]
    )
    session_id = serializers.CharField(max_length=50)

    def validate_phone(self, value):
        """Ensure phone is in correct format"""
        cleaned = re.sub(r'[\s\-\+]+', '', value)
        if cleaned.startswith('0'):
            cleaned = '254' + cleaned[1:]
        
        if not cleaned.startswith('254') or len(cleaned) != 12:
            raise serializers.ValidationError('Phone must be in format 254XXXXXXXXX')
        
        return '+' + cleaned