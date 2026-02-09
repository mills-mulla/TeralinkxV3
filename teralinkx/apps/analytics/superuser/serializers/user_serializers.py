# serializers/user_serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from users.models import ClientH, UserDevice, UserSession

class DjangoUserSerializer(serializers.ModelSerializer):
    """Serializer for Django User model"""
    client_profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'is_staff', 'is_active', 'is_superuser', 'date_joined', 
                  'last_login', 'client_profile']
        read_only_fields = ['date_joined', 'last_login']
    
    def get_client_profile(self, obj):
        try:
            return {
                'id': obj.client_profile.id,
                'account': obj.client_profile.account,
                'balance': str(obj.client_profile.balance),
                'status': obj.client_profile.status
            }
        except:
            return None


class UserDeviceSerializer(serializers.ModelSerializer):
    """Serializer for UserDevice model"""
    user_account = serializers.CharField(source='user.account', read_only=True)
    user_display_name = serializers.CharField(source='user.display_name', read_only=True)
    is_online = serializers.BooleanField(read_only=True)
    has_active_voucher = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = UserDevice
        fields = '__all__'
        read_only_fields = ['created', 'modified', 'last_seen', 'total_connections']


class UserSessionSerializer(serializers.ModelSerializer):
    """Serializer for UserSession model"""
    user_account = serializers.CharField(source='user.account', read_only=True)
    device_name = serializers.CharField(source='device.device_name', read_only=True)
    duration = serializers.SerializerMethodField()
    has_active_voucher = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = UserSession
        fields = '__all__'
        read_only_fields = ['created', 'modified', 'login_time', 'last_activity']
    
    def get_duration(self, obj):
        duration = obj.duration
        return str(duration).split('.')[0]  # Remove microseconds
