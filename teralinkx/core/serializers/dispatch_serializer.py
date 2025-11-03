from rest_framework import serializers
from ..models import DispatchVoucher
from django.utils import timezone
from ..tasks import mark_dispatch_as_expired
from decimal import Decimal

class DispatchSerializer(serializers.ModelSerializer):
    dispatch_expiry = serializers.DateTimeField(format="%d/%m/%Y at %H:%M:%S")
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = DispatchVoucher
        fields = [
            "dispatch_account", 
            "dispatch_devices",
            "dispatch_package", 
            "dispatch_price", 
            "dispatch_package_desc", 
            "dispatch_package_duration",
            "dispatch_status", 
            "dispatch_voucher_code",
            "dispatch_expiry",
            "total_download",
            "total_upload",
            "uptime",
            "usage_limit",
            "is_expired",
        ]

    def get_is_expired(self, obj):
        time_expired = obj.dispatch_expiry and timezone.now() > obj.dispatch_expiry
        usage_exceeded = False

        if obj.usage_limit is not None:
            # Safely cast usage fields to Decimal
            total_download = Decimal(str(obj.total_download or "0"))
            total_upload = Decimal(str(obj.total_upload or "0"))
            total_usage = total_download + total_upload
            usage_exceeded = total_usage >= obj.usage_limit

        expired = time_expired or usage_exceeded

        if expired and obj.dispatch_status != "expired":
            # 🚀 Trigger Celery task
            mark_dispatch_as_expired.delay(obj.dispatch_id)

        return expired
