# apps/security/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

User = get_user_model()

class PhoneAuthSerializer(serializers.Serializer):
    phone = serializers.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    method = serializers.ChoiceField(
        choices=['otp', 'password'],
        required=False
    )


class RequestOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    purpose = serializers.ChoiceField(
        choices=[
            ('signup', 'Sign Up'),
            ('login', 'Login'),
            ('verify', 'Phone Verification')
        ],
        default='login'
    )


class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    otp = serializers.CharField(min_length=6, max_length=6)
    session_token = serializers.CharField()
    purpose = serializers.ChoiceField(
        choices=[
            ('signup', 'Sign Up'),
            ('login', 'Login'),
            ('verify', 'Phone Verification')
        ],
        default='login'
    )


class PasswordLoginSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True)


class CompleteSignupSerializer(serializers.Serializer):
    session_token = serializers.CharField()
    display_name = serializers.CharField(max_length=100, required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(
        write_only=True, 
        required=False, 
        min_length=6,
        style={'input_type': 'password'}
    )
    current_ip = serializers.IPAddressField(required=False)
    current_mac = serializers.CharField(max_length=17, required=False)