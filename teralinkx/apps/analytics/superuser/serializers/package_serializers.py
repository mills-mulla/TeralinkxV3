# serializers/package_serializers.py
from rest_framework import serializers
from packages.models import PackageType, DispatchVoucher, Coupon, FeaturedPromotion, PointTransaction
from locations.models import Location

class PackageTypeSerializer(serializers.ModelSerializer):
    """Serializer for PackageType model"""
    
    class Meta:
        model = PackageType
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class DispatchVoucherSerializer(serializers.ModelSerializer):
    """Serializer for DispatchVoucher model"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    package_name = serializers.CharField(source='package.name', read_only=True)
    total_usage_mb = serializers.SerializerMethodField()
    voucher_code = serializers.CharField(required=False, allow_blank=True)
    home_location = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        required=False, allow_null=True
    )

    class Meta:
        model = DispatchVoucher
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def get_total_usage_mb(self, obj):
        total_bytes = (obj.download_bytes or 0) + (obj.upload_bytes or 0)
        return round(total_bytes / (1024 * 1024), 2)


class CouponSerializer(serializers.ModelSerializer):
    """Serializer for Coupon model"""
    is_valid = serializers.BooleanField(read_only=True)
    usage_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Coupon
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'total_uses']
    
    def get_usage_percentage(self, obj):
        if obj.max_uses > 0:
            return round((obj.total_uses / obj.max_uses) * 100, 2)
        return 0


class FeaturedPromotionSerializer(serializers.ModelSerializer):
    """Serializer for FeaturedPromotion model"""
    package_name = serializers.CharField(source='package.name', read_only=True)
    coupon_code = serializers.CharField(source='coupon.code', read_only=True, allow_null=True)
    is_live = serializers.BooleanField(read_only=True)
    ctr = serializers.SerializerMethodField()
    
    class Meta:
        model = FeaturedPromotion
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'views', 'clicks', 'conversions']
    
    def get_ctr(self, obj):
        """Click-through rate"""
        if obj.views > 0:
            return round((obj.clicks / obj.views) * 100, 2)
        return 0


class PointTransactionSerializer(serializers.ModelSerializer):
    """Serializer for PointTransaction model"""
    user_account = serializers.CharField(source='user.account', read_only=True)
    user_display_name = serializers.CharField(source='user.display_name', read_only=True)
    
    class Meta:
        model = PointTransaction
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
