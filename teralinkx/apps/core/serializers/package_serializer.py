# apps/packages/serializers/package_serializer.py
from rest_framework import serializers
from packages.models import PackageType, DispatchVoucher, AvailableVoucher

class PackageTypeSerializer(serializers.ModelSerializer):
    """Serializer for PackageType model including all relevant fields"""
    
    # Computed fields
    is_available = serializers.BooleanField(read_only=True)
    is_unlimited = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    available_quantity = serializers.IntegerField(read_only=True)
    
    # Duration in human-readable format
    duration_display = serializers.SerializerMethodField()
    
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
            'updated_at'
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
    location_name = serializers.CharField(source='location.name', read_only=True)
    
    # Computed fields
    is_active = serializers.BooleanField(read_only=True)
    is_data_exhausted = serializers.BooleanField(read_only=True)
    remaining_bytes = serializers.IntegerField(read_only=True)
    remaining_duration = serializers.DurationField(read_only=True)
    total_used_bytes = serializers.SerializerMethodField()
    
    class Meta:
        model = DispatchVoucher
        fields = [
            'id',
            'voucher_code',
            'package',
            'package_name',
            'user',
            'user_email',
            'location',
            'location_name',
            'price_paid',
            'activated_at',
            'expires_at',
            'download_bytes',
            'upload_bytes',
            'total_used_bytes',
            'session_count',
            'status',
            'allowed_mac_addresses',
            'concurrent_sessions',
            'is_roaming',
            'home_location',
            'transaction_id',
            'payment_reference',
            'is_active',
            'is_data_exhausted',
            'remaining_bytes',
            'remaining_duration',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'voucher_code', 'activated_at', 
            'download_bytes', 'upload_bytes', 'session_count'
        ]

    def get_total_used_bytes(self, obj):
        """Get total bytes used"""
        return obj.download_bytes + obj.upload_bytes


class AvailableVoucherSerializer(serializers.ModelSerializer):
    """Serializer for AvailableVoucher model"""
    
    package_name = serializers.CharField(source='package.name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.get_full_name', read_only=True)
    
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


# For backward compatibility - alias PackageSerializer to PackageTypeSerializer
PackageSerializer = PackageTypeSerializer