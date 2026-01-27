# userprofile_serializer.py
from rest_framework import serializers
from django.contrib.auth.models import User
from users.models import ClientH, UserDevice
from locations.models import Location
from locations.serializers import LocationSerializer
from decimal import Decimal
import re

class UserDeviceSerializer(serializers.ModelSerializer):
    """Serializer for user devices in profile updates."""
    
    is_online = serializers.BooleanField(read_only=True)
    concurrent_sessions_count = serializers.IntegerField(read_only=True)
    has_active_voucher = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = UserDevice
        fields = [
            'id', 'device_name', 'mac_address', 'device_type', 'device_platform',
            'device_model', 'device_manufacturer', 'is_trusted', 'status',
            'last_seen', 'total_connections', 'auto_connect', 'is_online',
            'concurrent_sessions_count', 'has_active_voucher', 'created', 'updated'
        ]
        read_only_fields = ['id', 'mac_address', 'last_seen', 'total_connections', 
                           'created', 'updated']

class ClientProfileSerializer(serializers.ModelSerializer):
    """Enhanced serializer for ClientH model with comprehensive profile management."""
    
    # User model fields
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    email = serializers.EmailField(source='user.email', required=False)
    
    # Profile fields
    profile_image = serializers.ImageField(
        required=False, 
        allow_null=True,
        help_text="Profile picture (max 5MB)"
    )
    
    # Location fields with serializers
    home_location = LocationSerializer(read_only=True)
    current_location = LocationSerializer(read_only=True)
    home_location_id = serializers.UUIDField(
        write_only=True, 
        required=False,
        help_text="UUID of home location"
    )
    current_location_id = serializers.UUIDField(
        write_only=True, 
        required=False,
        help_text="UUID of current location"
    )
    
    # Computed properties
    is_eligible_for_credit = serializers.BooleanField(read_only=True)
    available_credit = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    current_ip_address = serializers.IPAddressField(read_only=True)
    current_mac_address = serializers.CharField(read_only=True)
    active_sessions_count = serializers.SerializerMethodField()
    connected_devices_count = serializers.SerializerMethodField()
    
    # Device management
    devices = UserDeviceSerializer(many=True, read_only=True)
    device_updates = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        help_text="List of device updates: [{'mac_address': '...', 'device_name': '...', ...}]"
    )
    
    # Statistics
    session_statistics = serializers.SerializerMethodField()
    usage_statistics = serializers.SerializerMethodField()
    
    class Meta:
        model = ClientH
        fields = [
            # User Information
            'username', 'first_name', 'last_name', 'email',
            
            # Account Information
            'account', 'display_name', 'phone_number', 'account_tier', 'status',
            'profile_image',
            
            # Financial Information
            'balance', 'credit_limit', 'total_spent', 'lifetime_data_used',
            'is_eligible_for_credit', 'available_credit',
            
            # Location Information
            'home_location', 'current_location',
            'home_location_id', 'current_location_id',
            'last_location_update',
            
            # Security
            'two_factor_enabled', 'failed_login_attempts',
            
            # Preferences
            'auto_renew',
            
            # Network Information
            'current_ip_address', 'current_mac_address',
            'active_voucher', 'voucher_expiry',
            
            # Statistics
            'active_sessions_count', 'connected_devices_count',
            'session_statistics', 'usage_statistics',
            
            # Device Management
            'devices', 'device_updates',
            
            # Timestamps
            'last_login', 'last_balance_update', 'created', 'updated'
        ]
        read_only_fields = [
            'account', 'balance', 'total_spent', 'lifetime_data_used',
            'is_eligible_for_credit', 'available_credit', 'current_ip_address',
            'current_mac_address', 'failed_login_attempts', 'last_login',
            'last_balance_update', 'created', 'updated', 'last_location_update',
            'active_sessions_count', 'connected_devices_count',
            'session_statistics', 'usage_statistics'
        ]
    
    def get_active_sessions_count(self, obj):
        """Get count of active sessions."""
        return obj.active_sessions.count()
    
    def get_connected_devices_count(self, obj):
        """Get count of connected devices."""
        return obj.connected_devices.count()
    
    def get_session_statistics(self, obj):
        """Get session statistics."""
        return obj.get_session_statistics()
    
    def get_usage_statistics(self, obj):
        """Get usage statistics."""
        return {
            'daily_average_connections': self._calculate_daily_average(obj),
            'favorite_location': str(obj.home_location) if obj.home_location else None,
            'total_days_active': (timezone.now() - obj.created).days if obj.created else 0,
        }
    
    def _calculate_daily_average(self, obj):
        """Calculate daily average connections."""
        if not obj.created:
            return 0
        
        days_active = (timezone.now() - obj.created).days
        if days_active == 0:
            days_active = 1
        
        return obj.devices.aggregate(
            total=models.Sum('total_connections')
        )['total'] or 0 / days_active
    
    def validate_phone_number(self, value):
        """Validate phone number format."""
        if value and not re.match(r'^\+?1?\d{9,15}$', value):
            raise serializers.ValidationError(
                "Phone number must be entered in the format: '+999999999'. "
                "Up to 15 digits allowed."
            )
        return value
    
    def validate_display_name(self, value):
        """Validate display name."""
        if value and len(value) < 2:
            raise serializers.ValidationError("Display name must be at least 2 characters long.")
        if value and len(value) > 100:
            raise serializers.ValidationError("Display name cannot exceed 100 characters.")
        return value
    
    def validate_account_tier(self, value):
        """Validate account tier."""
        valid_tiers = ['basic', 'premium', 'business', 'enterprise']
        if value not in valid_tiers:
            raise serializers.ValidationError(f"Account tier must be one of: {', '.join(valid_tiers)}")
        return value
    
    def validate(self, data):
        """Custom validation across fields."""
        # Validate location IDs exist
        if 'home_location_id' in data:
            try:
                location = Location.objects.get(id=data['home_location_id'])
                data['home_location'] = location
            except Location.DoesNotExist:
                raise serializers.ValidationError({
                    'home_location_id': 'Location not found'
                })
        
        if 'current_location_id' in data:
            try:
                location = Location.objects.get(id=data['current_location_id'])
                data['current_location'] = location
            except Location.DoesNotExist:
                raise serializers.ValidationError({
                    'current_location_id': 'Location not found'
                })
        
        # Validate user email uniqueness
        if 'user' in data and 'email' in data['user']:
            email = data['user']['email']
            if User.objects.filter(email=email).exclude(id=self.instance.user.id).exists():
                raise serializers.ValidationError({
                    'email': 'This email is already in use.'
                })
        
        # Validate device updates
        if 'device_updates' in data:
            self._validate_device_updates(data['device_updates'])
        
        return data
    
    def _validate_device_updates(self, device_updates):
        """Validate device update data."""
        for device_update in device_updates:
            if 'mac_address' not in device_update:
                raise serializers.ValidationError({
                    'device_updates': 'Each device update must include a mac_address'
                })
            
            mac_address = device_update['mac_address']
            if not re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', mac_address):
                raise serializers.ValidationError({
                    'device_updates': f'Invalid MAC address format: {mac_address}'
                })
    
    def update(self, instance, validated_data):
        """Enhanced update method with comprehensive field handling."""
        # Extract nested data
        user_data = validated_data.pop('user', {})
        device_updates = validated_data.pop('device_updates', [])
        home_location = validated_data.pop('home_location', None)
        current_location = validated_data.pop('current_location', None)
        
        # Update User model fields
        if user_data:
            user = instance.user
            for field, value in user_data.items():
                if hasattr(user, field):
                    setattr(user, field, value)
            user.save()
        
        # Update locations
        if home_location:
            instance.home_location = home_location
        
        if current_location:
            instance.current_location = current_location
            instance.last_location_update = timezone.now()
        
        # Update profile image
        if 'profile_image' in validated_data:
            instance.profile_image = validated_data.pop('profile_image')
        
        # Update other ClientH fields
        for field, value in validated_data.items():
            if hasattr(instance, field):
                setattr(instance, field, value)
        
        # Save ClientH instance
        instance.save()
        
        # Process device updates
        if device_updates:
            self._process_device_updates(instance, device_updates)
        
        return instance
    
    def _process_device_updates(self, client, device_updates):
        """Process updates for user devices."""
        for device_update in device_updates:
            mac_address = device_update.pop('mac_address')
            
            try:
                device = client.devices.get(mac_address=mac_address)
                
                # Only allow updates to specific fields
                allowed_fields = ['device_name', 'device_type', 'device_platform',
                                'device_model', 'device_manufacturer', 'auto_connect']
                
                for field, value in device_update.items():
                    if field in allowed_fields and hasattr(device, field):
                        setattr(device, field, value)
                
                device.save()
                
            except client.devices.model.DoesNotExist:
                # Device not found - skip or log warning
                continue
    
    def to_representation(self, instance):
        """Custom representation to include computed fields."""
        representation = super().to_representation(instance)
        
        # Add computed fields
        representation['max_allowed_devices'] = instance.get_max_allowed_devices()
        representation['can_add_more_devices'] = (
            instance.devices.filter(status='active').count() < instance.get_max_allowed_devices()
        )
        representation['has_active_voucher'] = bool(instance.active_voucher)
        
        # Add voucher time remaining if active
        if instance.voucher_expiry and instance.voucher_expiry > timezone.now():
            remaining = instance.voucher_expiry - timezone.now()
            representation['voucher_time_remaining'] = {
                'seconds': int(remaining.total_seconds()),
                'human_readable': str(remaining)
            }
        
        return representation