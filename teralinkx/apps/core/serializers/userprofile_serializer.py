# Userprofile_serializer.py
from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import ClientH

class ClientProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    email = serializers.CharField(source='user.email', required=False)
    profile_image = serializers.ImageField(required=False)
    
    # Computed properties from the model
    is_eligible_for_credit = serializers.BooleanField(read_only=True)
    available_credit = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    current_ip_address = serializers.IPAddressField(read_only=True)
    current_mac_address = serializers.CharField(read_only=True)

    class Meta:
        model = ClientH
        fields = [
            'first_name', 'last_name', 'email', 'profile_image', 
            'account', 'display_name', 'phone_number', 'balance', 
            'status', 'account_tier', 'credit_limit', 'total_spent',
            'lifetime_data_used', 'home_location', 'current_location',
            'two_factor_enabled', 'auto_renew', 'is_eligible_for_credit',
            'available_credit', 'current_ip_address', 'current_mac_address'
        ]
        read_only_fields = [
            'account', 'balance', 'total_spent', 'lifetime_data_used',
            'is_eligible_for_credit', 'available_credit', 'current_ip_address',
            'current_mac_address'
        ]

    def update(self, instance, validated_data):
        # Extract user data
        user_data = validated_data.pop('user', {})
        
        # Update user fields if provided
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                if attr in ['first_name', 'last_name', 'email']:
                    setattr(user, attr, value)
            user.save()

        # Update profile image if provided
        if 'profile_image' in validated_data:
            instance.profile_image = validated_data['profile_image']

        # Update other ClientH fields
        for attr, value in validated_data.items():
            if hasattr(instance, attr):
                setattr(instance, attr, value)
        
        instance.save()
        return instance