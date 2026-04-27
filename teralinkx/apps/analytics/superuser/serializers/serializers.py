# serializers/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from users.models import ClientH
from packages.models import DispatchVoucher
from finance.models import PaymentTransaction, TransactionQueue

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class ClientSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', required=False)
    user_email = serializers.CharField(source='user.email', required=False)
    profile_image = serializers.SerializerMethodField()
    active_devices_count = serializers.SerializerMethodField()
    active_sessions_count = serializers.SerializerMethodField()
    home_location_name = serializers.CharField(source='home_location.name', read_only=True, allow_null=True)

    class Meta:
        model = ClientH
        fields = '__all__'

    def get_profile_image(self, obj):
        if obj.profile_image:
            request = self.context.get('request')
            if request:
                url = request.build_absolute_uri(obj.profile_image.url)
                return url.replace('http://', 'https://')
            return obj.profile_image.url.replace('http://', 'https://')
        return None

    def get_active_devices_count(self, obj):
        return obj.devices.filter(status='active').count()

    def get_active_sessions_count(self, obj):
        try:
            return obj.active_sessions.count()
        except Exception:
            return 0

    def update(self, instance, validated_data):
        user_data = {}
        if 'user' in validated_data:
            user_data = validated_data.pop('user')
        instance = super().update(instance, validated_data)
        if user_data:
            for attr, val in user_data.items():
                setattr(instance.user, attr, val)
            instance.user.save()
        return instance

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = '__all__'


from analytics.models import RefundLog, DowntimeRecord

class DowntimeRecordSerializer(serializers.ModelSerializer):
    duration_minutes = serializers.ReadOnlyField()
    class Meta:
        model = DowntimeRecord
        fields = '__all__'

class RefundLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundLog
        fields = '__all__'
