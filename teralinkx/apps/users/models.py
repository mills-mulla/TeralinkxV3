# apps/users/models.py
from django.db import models
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model

from apps.core.models import TimeStampedModel

User = get_user_model()

class ClientH(TimeStampedModel):
    """Enhanced user management for V3"""
    ACCOUNT_TIERS = [
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('business', 'Business'),
        ('enterprise', 'Enterprise'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    account = models.CharField(max_length=15, unique=True)
    
    # Personalization
    display_name = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Account Tier & Status
    account_tier = models.CharField(max_length=20, choices=ACCOUNT_TIERS, default='basic')
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('inactive', 'Inactive'),
        ('banned', 'Banned'),
    ], default='active')
    
    # Financials
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_spent = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    lifetime_data_used = models.BigIntegerField(default=0)
    
    # Location & Presence
    home_location = models.ForeignKey('locations.Location', on_delete=models.PROTECT, related_name='home_users')
    current_location = models.ForeignKey('locations.Location', on_delete=models.SET_NULL, null=True, blank=True, related_name='current_users')
    last_location_update = models.DateTimeField(null=True, blank=True)
    
    # Security
    failed_login_attempts = models.IntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    two_factor_enabled = models.BooleanField(default=False)
    security_notifications = models.BooleanField(default=True)
    
    # Preferences
    language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    marketing_emails = models.BooleanField(default=False)
    auto_renew = models.BooleanField(default=False)
    
    # Network Information
    current_ip_address = models.GenericIPAddressField(blank=True, null=True)
    current_mac_address = models.CharField(max_length=17, blank=True, null=True)
    active_voucher = models.CharField(max_length=50, blank=True, null=True)
    voucher_expiry = models.DateTimeField(blank=True, null=True)
    
    # Metadata
    last_login = models.DateTimeField(auto_now=True)
    last_balance_update = models.DateTimeField(auto_now=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.display_name or self.user.username} ({self.account})"
    
    @property
    def is_eligible_for_credit(self):
        """Check if user is eligible for credit purchases"""
        return self.account_tier in ['premium', 'business', 'enterprise'] and self.credit_limit > 0
    
    @property
    def available_credit(self):
        """Get available credit"""
        return max(0, self.credit_limit + self.balance)
    
    def update_location(self, new_location, mac_address=None, ip_address=None):
        """Update user's current location with network info"""
        old_location = self.current_location
        self.current_location = new_location
        self.last_location_update = timezone.now()
        
        if mac_address:
            self.current_mac_address = mac_address
        if ip_address:
            self.current_ip_address = ip_address
        
        # Handle roaming logic
        if old_location and new_location and old_location != new_location:
            # Log roaming event
            from apps.security.models import SecurityLog
            SecurityLog.objects.create(
                user=self,
                action_type='roaming_started',
                description=f"User started roaming from {old_location} to {new_location}",
                severity='low',
                details={
                    'from_location': str(old_location),
                    'to_location': str(new_location),
                    'mac_address': mac_address,
                    'ip_address': ip_address
                }
            )
        
        self.save()
    
    def get_active_voucher(self):
        """Get currently active voucher"""
        if self.active_voucher:
            try:
                from apps.packages.models import DispatchVoucher
                return DispatchVoucher.objects.get(
                    voucher_code=self.active_voucher,
                    status='active'
                )
            except DispatchVoucher.DoesNotExist:
                return None
        return None
    
    def get_active_devices(self):
        """Get all active devices"""
        return self.devices.filter(status='active')
    
    def can_add_device(self):
        """Check if user can add more devices"""
        active_devices = self.get_active_devices().count()
        max_devices = self.get_max_allowed_devices()
        return active_devices < max_devices
    
    def get_max_allowed_devices(self):
        """Get maximum allowed devices based on account tier"""
        tier_limits = {
            'basic': 3,
            'premium': 5,
            'business': 10,
            'enterprise': 50
        }
        return tier_limits.get(self.account_tier, 3)
    
    class Meta:
        indexes = [
            models.Index(fields=['account']),
            models.Index(fields=['status']),
            models.Index(fields=['account_tier']),
            models.Index(fields=['home_location']),
            models.Index(fields=['current_location']),
            models.Index(fields=['balance']),
            models.Index(fields=['last_login']),
        ]
        verbose_name = "Client"
        verbose_name_plural = "Clients"

class UserDevice(TimeStampedModel):
    """Enterprise-grade device management with security features"""
    DEVICE_TYPES = [
        ('phone', 'Smartphone'),
        ('laptop', 'Laptop'),
        ('tablet', 'Tablet'),
        ('desktop', 'Desktop Computer'),
        ('iot', 'IoT Device'),
        ('gaming', 'Gaming Console'),
        ('tv', 'Smart TV'),
        ('other', 'Other Device'),
    ]
    
    DEVICE_PLATFORMS = [
        ('windows', 'Windows'),
        ('macos', 'macOS'),
        ('linux', 'Linux'),
        ('android', 'Android'),
        ('ios', 'iOS'),
        ('other', 'Other OS'),
    ]
    
    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUS_SUSPENDED = 'suspended'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_INACTIVE, 'Inactive'),
        (STATUS_SUSPENDED, 'Suspended'),
    ]
    
    user = models.ForeignKey(ClientH, on_delete=models.CASCADE, related_name='devices')
    mac_address = models.CharField(max_length=17, unique=True)
    
    # Device Identity
    device_name = models.CharField(max_length=100, help_text="User-friendly device name")
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES, default='other')
    device_platform = models.CharField(max_length=20, choices=DEVICE_PLATFORMS, default='other')
    device_model = models.CharField(max_length=100, blank=True)
    device_manufacturer = models.CharField(max_length=100, blank=True)
    
    # Network Information
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    bound_ip = models.CharField(max_length=15, null=True, blank=True)
    dhcp_lease = models.ForeignKey('analytics.DHCPLease', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Security & Trust
    is_primary = models.BooleanField(default=False)
    is_trusted = models.BooleanField(default=False)
    trust_level = models.IntegerField(default=1, choices=[(1, 'Low'), (2, 'Medium'), (3, 'High')])
    requires_approval = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    
    # Activity Tracking
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    last_seen_ip = models.GenericIPAddressField(null=True, blank=True)
    last_seen_location = models.ForeignKey('locations.Location', on_delete=models.SET_NULL, null=True, blank=True)
    total_connections = models.IntegerField(default=0)
    
    # Usage Statistics
    total_data_used = models.BigIntegerField(default=0)
    average_session_duration = models.DurationField(null=True, blank=True)
    favorite_location = models.ForeignKey('locations.Location', on_delete=models.SET_NULL, null=True, blank=True, related_name='favorite_devices')
    
    # Configuration
    auto_connect = models.BooleanField(default=True)
    quality_of_service = models.CharField(max_length=20, choices=[
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('gaming', 'Gaming'),
        ('streaming', 'Streaming'),
    ], default='standard')
    
    # Metadata
    user_agent = models.TextField(blank=True)
    client_identifier = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True, help_text="Administrator notes about this device")
    
    def __str__(self):
        return f"{self.device_name} ({self.mac_address}) - {self.user.account}"
    
    @property
    def is_online(self):
        """Check if device is currently online"""
        if not self.last_seen:
            return False
        return timezone.now() - self.last_seen < timedelta(minutes=5)
    
    @property
    def is_suspicious(self):
        """Check if device shows suspicious activity"""
        return False
    
    def update_presence(self, ip_address=None, location=None):
        """Update device presence information"""
        self.last_seen = timezone.now()
        self.total_connections += 1
        
        if ip_address:
            self.last_seen_ip = ip_address
        if location:
            self.last_seen_location = location
            
        self.save()
        
        # Log device activity
        from apps.security.models import SecurityLog
        SecurityLog.objects.create(
            user=self.user,
            action_type='device_connected',
            description=f"Device {self.device_name} connected from {ip_address}",
            severity='low',
            details={
                'device_id': str(self.id),
                'mac_address': self.mac_address,
                'ip_address': ip_address,
                'location': str(location) if location else None
            }
        )
    
    def block_device(self, reason="Security concern", blocked_by=None):
        """Block this device from network access"""
        old_status = self.status
        self.status = self.STATUS_SUSPENDED
        self.save()
        
        from apps.security.models import SecurityLog
        SecurityLog.objects.create(
            user=self.user,
            action_type='device_blocked',
            description=f"Device {self.device_name} blocked: {reason}",
            severity='high',
            details={
                'device_id': str(self.id),
                'mac_address': self.mac_address,
                'old_status': old_status,
                'new_status': self.status,
                'reason': reason,
                'blocked_by': str(blocked_by) if blocked_by else 'system'
            }
        )
    
    def unblock_device(self, reason="User request", unblocked_by=None):
        """Unblock this device"""
        self.status = self.STATUS_ACTIVE
        self.save()
        
        from apps.security.models import SecurityLog
        SecurityLog.objects.create(
            user=self.user,
            action_type='device_unblocked',
            description=f"Device {self.device_name} unblocked: {reason}",
            severity='medium',
            details={
                'device_id': str(self.id),
                'mac_address': self.mac_address,
                'reason': reason,
                'unblocked_by': str(unblocked_by) if unblocked_by else 'system'
            }
        )
    
    def get_connection_stats(self, days=30):
        """Get connection statistics for given period"""
        stats = {
            'total_sessions': 0,
            'average_duration': timedelta(0),
            'peak_usage_time': 'N/A',
            'frequent_locations': []
        }
        return stats
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['mac_address']),
            models.Index(fields=['last_seen']),
            models.Index(fields=['is_primary']),
            models.Index(fields=['is_trusted']),
            models.Index(fields=['device_type']),
        ]
        ordering = ['-is_primary', '-last_seen']
        verbose_name = "User Device"
        verbose_name_plural = "User Devices"