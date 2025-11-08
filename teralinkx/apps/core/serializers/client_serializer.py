# core/serializers/client_serializer.py
from rest_framework import serializers
from users.models import ClientH, UserDevice
from django.contrib.auth import get_user_model

User = get_user_model()

class ClientSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    current_ip = serializers.IPAddressField(required=False)
    current_mac = serializers.CharField(max_length=17, required=False)
    display_name = serializers.CharField(max_length=100, required=False)
    email = serializers.EmailField(required=False)
    
    def validate_current_mac(self, value):
        if value and UserDevice.objects.filter(mac_address=value).exists():
            raise serializers.ValidationError("MAC address already registered")
        return value
    
    def validate_phone(self, value):
        if ClientH.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Phone number already registered")
        return value