# apps/packages/serializers/package_serializer.py
from rest_framework import serializers
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

# Updated imports - use relative or absolute paths correctly
from packages.models import PackageType, DispatchVoucher, AvailableVoucher, Coupon, CouponUsage, FeaturedPromotion


class PackageTypeSerializer(serializers.ModelSerializer):
    """Serializer for PackageType model including all relevant fields"""
    
    # Computed fields
    is_available = serializers.BooleanField(read_only=True)
    is_unlimited = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    available_quantity = serializers.IntegerField(read_only=True)
    
    # Duration in human-readable format
    duration_display = serializers.SerializerMethodField()
    
    # Location info
    location_names = serializers.SerializerMethodField()
    
    # For featured packages
    has_active_promotion = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageType
        fields = [
            'id',
            'name',
            'code', 
            'description',
            'category',
            'tier',
            'price',
            'original_price',
            'duration',
            'duration_display',
            'speed_limit_mbps',
            'data_limit_mb',
            'device_limit',
            'qos_priority',
            'is_active',
            'is_public',
            'allow_roaming',
            'auto_renew',
            'radius_group',
            'is_featured',
            'color_code',
            'tags',
            'total_quantity',
            'sold_quantity',
            'is_available',
            'is_unlimited',
            'discount_percentage',
            'available_quantity',
            'display_order',
            'created_at',
            'updated_at',
            'location_names',
            'has_active_promotion'
        ]
        read_only_fields = ['created_at', 'updated_at', 'sold_quantity']

    def get_duration_display(self, obj):
        """Convert duration to human-readable format"""
        if not obj.duration:
            return "Not specified"
        
        total_seconds = int(obj.duration.total_seconds())
        
        # Convert to appropriate units
        if total_seconds < 60:
            return f"{total_seconds} seconds"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        elif total_seconds < 86400:
            hours = total_seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''}"
        else:
            days = total_seconds // 86400
            return f"{days} day{'s' if days != 1 else ''}"

    def get_location_names(self, obj):
        """Get names of locations where package is available"""
        return [location.name for location in obj.locations.all()]

    def get_has_active_promotion(self, obj):
        """Check if package has active promotion"""
        now = timezone.now()
        return FeaturedPromotion.objects.filter(
            package=obj,
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).exists()

    def validate_price(self, value):
        """Validate price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Price must be positive")
        return value

    def validate_data_limit_mb(self, value):
        """Validate data limit is positive if provided"""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Data limit must be positive")
        return value

    def validate_device_limit(self, value):
        """Validate device limit is at least 1"""
        if value < 1:
            raise serializers.ValidationError("Device limit must be at least 1")
        return value

    def validate(self, data):
        """Cross-field validation"""
        # Validate original_price vs price
        original_price = data.get('original_price')
        price = data.get('price')
        
        if original_price and price and original_price < price:
            raise serializers.ValidationError({
                'original_price': 'Original price cannot be less than current price'
            })
        
        return data


class DispatchVoucherSerializer(serializers.ModelSerializer):
    """Serializer for DispatchVoucher model"""
    
    package_name = serializers.CharField(source='package.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    home_location_name = serializers.CharField(source='home_location.name', read_only=True)
    
    # Computed fields
    is_active = serializers.BooleanField(read_only=True)
    is_data_exhausted = serializers.BooleanField(read_only=True)
    remaining_bytes = serializers.IntegerField(read_only=True)
    remaining_duration = serializers.DurationField(read_only=True)
    
    # Usage statistics
    total_used_bytes = serializers.SerializerMethodField()
    total_used_mb = serializers.SerializerMethodField()
    remaining_mb = serializers.SerializerMethodField()
    
    # Applied coupon info
    applied_coupon = serializers.SerializerMethodField()
    
    class Meta:
        model = DispatchVoucher
        fields = [
            'id',
            'voucher_code',
            'package',
            'package_name',
            'user',
            'user_email',
            'user_username',
            'location',
            'location_name',
            'price_paid',
            'activated_at',
            'expires_at',
            'download_bytes',
            'upload_bytes',
            'total_used_bytes',
            'total_used_mb',
            'session_count',
            'status',
            'allowed_mac_addresses',
            'concurrent_sessions',
            'is_roaming',
            'home_location',
            'home_location_name',
            'transaction_id',
            'payment_reference',
            'is_active',
            'is_data_exhausted',
            'remaining_bytes',
            'remaining_mb',
            'remaining_duration',
            'applied_coupon',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'voucher_code', 'activated_at', 
            'download_bytes', 'upload_bytes', 'session_count', 'status'
        ]

    def get_total_used_bytes(self, obj):
        """Get total bytes used"""
        return obj.download_bytes + obj.upload_bytes

    def get_total_used_mb(self, obj):
        """Get total MB used"""
        total_bytes = obj.download_bytes + obj.upload_bytes
        return round(total_bytes / (1024 * 1024), 2)

    def get_remaining_mb(self, obj):
        """Get remaining MB"""
        if obj.remaining_bytes is None:
            return None
        return round(obj.remaining_bytes / (1024 * 1024), 2)

    def get_applied_coupon(self, obj):
        """Get applied coupon info if exists"""
        coupon_usage = CouponUsage.objects.filter(voucher=obj).first()
        if coupon_usage:
            return {
                'code': coupon_usage.coupon.code,
                'discount_amount': float(coupon_usage.discount_amount),
                'original_price': float(coupon_usage.original_price),
                'final_price': float(coupon_usage.final_price),
            }
        return None


class AvailableVoucherSerializer(serializers.ModelSerializer):
    """Serializer for AvailableVoucher model"""
    
    package_name = serializers.CharField(source='package.name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.get_full_name', read_only=True)
    used_by_name = serializers.CharField(source='used_by.get_full_name', read_only=True)
    
    # Computed fields
    is_valid = serializers.BooleanField(read_only=True)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = AvailableVoucher
        fields = [
            'id',
            'voucher_code',
            'voucher_type',
            'package',
            'package_name',
            'location',
            'location_name',
            'is_used',
            'used_at',
            'used_by',
            'used_by_name',
            'batch_id',
            'generated_by',
            'generated_by_name',
            'is_roaming',
            'price_override',
            'valid_until',
            'is_valid',
            'final_price',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_used', 'used_at', 'used_by']


class CouponSerializer(serializers.ModelSerializer):
    """Serializer for Coupon model"""
    
    # Computed fields
    is_valid = serializers.BooleanField(read_only=True)
    remaining_uses = serializers.SerializerMethodField()
    discount_message = serializers.SerializerMethodField()
    
    # Package info for specific coupons
    applicable_package_names = serializers.SerializerMethodField()
    
    class Meta:
        model = Coupon
        fields = [
            'id',
            'code',
            'name',
            'description',
            'coupon_type',
            'discount_value',
            'applicable_to',
            'applicable_category',
            'applicable_tier',
            'max_uses',
            'max_uses_per_user',
            'min_purchase_amount',
            'valid_from',
            'valid_until',
            'is_active',
            'total_uses',
            'is_valid',
            'remaining_uses',
            'discount_message',
            'applicable_package_names',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'total_uses']

    def get_remaining_uses(self, obj):
        """Get remaining number of uses"""
        return obj.max_uses - obj.total_uses

    def get_discount_message(self, obj):
        """Generate human-readable discount message"""
        if obj.coupon_type == 'percentage':
            return f"{obj.discount_value}% OFF"
        elif obj.coupon_type == 'fixed':
            return f"KSh {obj.discount_value} OFF"
        elif obj.coupon_type == 'package':
            return "Free Upgrade"
        return "Discount"

    def get_applicable_package_names(self, obj):
        """Get names of applicable packages"""
        if obj.applicable_to == 'specific':
            return [p.name for p in obj.applicable_packages.all()]
        return []


class CouponUsageSerializer(serializers.ModelSerializer):
    """Serializer for CouponUsage model"""
    
    coupon_code = serializers.CharField(source='coupon.code', read_only=True)
    coupon_name = serializers.CharField(source='coupon.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    package_name = serializers.CharField(source='package.name', read_only=True)
    voucher_code = serializers.CharField(source='voucher.voucher_code', read_only=True, allow_null=True)
    
    class Meta:
        model = CouponUsage
        fields = [
            'id',
            'coupon',
            'coupon_code',
            'coupon_name',
            'user',
            'user_email',
            'user_username',
            'package',
            'package_name',
            'voucher',
            'voucher_code',
            'original_price',
            'discount_amount',
            'final_price',
            'ip_address',
            'user_agent',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class FeaturedPromotionSerializer(serializers.ModelSerializer):
    """Serializer for FeaturedPromotion model"""
    
    package_name = serializers.CharField(source='package.name', read_only=True)
    package_price = serializers.DecimalField(source='package.price', max_digits=10, decimal_places=2, read_only=True)
    coupon_code = serializers.CharField(source='coupon.code', read_only=True, allow_null=True)
    coupon_discount_message = serializers.SerializerMethodField()
    
    # Computed fields
    is_live = serializers.BooleanField(read_only=True)
    time_remaining = serializers.DurationField(read_only=True)
    is_ending_soon = serializers.BooleanField(read_only=True)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    # Performance metrics
    click_through_rate = serializers.FloatField(read_only=True)
    conversion_rate = serializers.FloatField(read_only=True)
    
    # Location info
    location_names = serializers.SerializerMethodField()
    
    class Meta:
        model = FeaturedPromotion
        fields = [
            'id',
            'name',
            'promotion_type',
            'package',
            'package_name',
            'package_price',
            'coupon',
            'coupon_code',
            'coupon_discount_message',
            'headline',
            'description',
            'banner_image',
            'button_text',
            'button_color',
            'display_order',
            'is_active',
            'start_date',
            'end_date',
            'is_live',
            'time_remaining',
            'is_ending_soon',
            'final_price',
            'savings',
            'views',
            'clicks',
            'conversions',
            'click_through_rate',
            'conversion_rate',
            'location_names',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'views', 'clicks', 'conversions']

    def get_coupon_discount_message(self, obj):
        """Get discount message from coupon"""
        if obj.coupon:
            if obj.coupon.coupon_type == 'percentage':
                return f"Save {obj.coupon.discount_value}%"
            elif obj.coupon.coupon_type == 'fixed':
                return f"Save KSh {obj.coupon.discount_value}"
        return None

    def get_location_names(self, obj):
        """Get names of targeted locations"""
        return [location.name for location in obj.locations.all()]

    def validate(self, data):
        """Validate promotion dates"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError({
                'end_date': 'End date must be after start date'
            })
        
        return data


class SimplePackageSerializer(serializers.ModelSerializer):
    """Simplified package serializer for dropdowns and quick views"""
    
    class Meta:
        model = PackageType
        fields = [
            'id',
            'name',
            'code',
            'price',
            'duration',
            'speed_limit_mbps',
            'data_limit_mb',
            'is_unlimited',
            'is_featured'
        ]


# For backward compatibility - alias PackageSerializer to PackageTypeSerializer
PackageSerializer = PackageTypeSerializer


class VoucherActivationSerializer(serializers.Serializer):
    """Serializer for voucher activation"""
    voucher_code = serializers.CharField(max_length=255, required=True)
    mac_address = serializers.CharField(max_length=17, required=False, allow_blank=True)
    location_id = serializers.IntegerField(required=True)
    
    def validate_mac_address(self, value):
        """Validate MAC address format"""
        if value and len(value) not in [12, 17]:
            raise serializers.ValidationError("Invalid MAC address format")
        return value


class CouponValidationSerializer(serializers.Serializer):
    """Serializer for coupon validation"""
    coupon_code = serializers.CharField(max_length=50, required=True)
    package_id = serializers.IntegerField(required=True)
    
    def validate_coupon_code(self, value):
        """Convert coupon code to uppercase"""
        return value.strip().upper()