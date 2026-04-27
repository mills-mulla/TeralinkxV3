# serializers/user_serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User, Group, Permission
from users.models import ClientH, UserDevice, UserSession

class DjangoUserSerializer(serializers.ModelSerializer):
    """Serializer for Django User model"""
    client_profile = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True, required=False)
    groups = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Group.objects.all(), required=False
    )
    user_permissions = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Permission.objects.all(), required=False
    )
    group_names = serializers.SerializerMethodField()
    permission_codenames = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'is_staff', 'is_active', 'is_superuser', 'date_joined',
                  'last_login', 'client_profile', 'password',
                  'groups', 'user_permissions', 'group_names', 'permission_codenames']
        read_only_fields = ['date_joined', 'last_login']

    def get_group_names(self, obj):
        return list(obj.groups.values('id', 'name'))

    def get_permission_codenames(self, obj):
        return list(obj.user_permissions.values('id', 'codename', 'content_type__app_label', 'content_type__model'))
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
    
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
        read_only_fields = ['created_at', 'updated_at', 'last_seen', 'total_connections']


class UserSessionSerializer(serializers.ModelSerializer):
    """Serializer for UserSession model"""
    user_account = serializers.CharField(source='user.account', read_only=True)
    device_name = serializers.CharField(source='device.device_name', read_only=True)
    duration = serializers.SerializerMethodField()
    has_active_voucher = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = UserSession
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'login_time', 'last_activity']
    
    def get_duration(self, obj):
        duration = obj.duration
        return str(duration).split('.')[0]  # Remove microseconds
