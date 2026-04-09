from rest_framework import serializers
from .models import RadCheck, RadReply, RadUserGroup, RadGroupCheck, RadGroupReply, RadAcct, Nas


class CreateUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255, required=False)
    profile = serializers.CharField(max_length=255, required=False)
    is_voucher = serializers.BooleanField(default=False, help_text="True for time-based vouchers")
    duration_seconds = serializers.IntegerField(required=False, help_text="Voucher duration in seconds (for vouchers only)")


class UserSerializer(serializers.Serializer):
    username = serializers.CharField()
    profile = serializers.CharField(required=False)


class CreateProfileSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    upload_limit = serializers.CharField(help_text="e.g., 5M, 10M")
    download_limit = serializers.CharField(help_text="e.g., 2M, 8M")
    session_timeout = serializers.IntegerField(required=False, help_text="Session duration in seconds")
    data_limit = serializers.IntegerField(required=False, help_text="Total data limit in bytes")


class ProfileSerializer(serializers.Serializer):
    name = serializers.CharField()
    upload_limit = serializers.CharField()
    download_limit = serializers.CharField()


class RadAcctSerializer(serializers.ModelSerializer):
    class Meta:
        model = RadAcct
        fields = '__all__'


class NasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nas
        fields = '__all__'
