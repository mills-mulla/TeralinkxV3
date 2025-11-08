# apps/packages/models.py
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
import uuid
from datetime import timedelta

from core.models import TimeStampedModel
from django.contrib.auth import get_user_model

User = get_user_model()

class PackageType(TimeStampedModel):
    """All packages available for purchase"""
    
    PACKAGE_CATEGORIES = [
        ('time_based', 'Time-Based'),
        ('data_based', 'Data-Based'),
        ('unlimited', 'Unlimited'),
        ('hybrid', 'Hybrid'),
        ('corporate', 'Corporate'),
    ]
    
    TIERS = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('business', 'Business'),
        ('enterprise', 'Enterprise'),
    ]
    
    # Core Identity
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    # Classification
    category = models.CharField(max_length=20, choices=PACKAGE_CATEGORIES, default='time_based')
    tier = models.CharField(max_length=20, choices=TIERS, default='basic')
    
    # Pricing & Duration
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    duration = models.DurationField(help_text="Package validity duration")
    
    # Technical Specifications
    speed_limit_mbps = models.IntegerField(help_text="Maximum speed in Mbps")
    data_limit_mb = models.BigIntegerField(null=True, blank=True, help_text="Data limit in MB (null = unlimited)")
    device_limit = models.IntegerField(default=1)
    
    # Network Quality
    qos_priority = models.CharField(max_length=20, choices=[
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('business', 'Business'),
        ('real_time', 'Real-time'),
    ], default='standard')
    
    # Availability & Targeting
    locations = models.ManyToManyField('locations.Location', blank=True)
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    
    # Enterprise Features
    allow_roaming = models.BooleanField(default=True)
    auto_renew = models.BooleanField(default=False)
    radius_group = models.CharField(max_length=100, blank=True)
    
    # Display & Marketing
    display_order = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    color_code = models.CharField(max_length=7, default='#007bff')
    tags = models.JSONField(default=list, help_text="Tags for filtering and search")
    
    # Inventory Management
    total_quantity = models.IntegerField(null=True, blank=True)
    sold_quantity = models.IntegerField(default=0)

    class Meta:
        db_table = 'packages'
        ordering = ['display_order', 'tier', 'price']
        indexes = [
            models.Index(fields=['category', 'tier']),
            models.Index(fields=['is_active', 'is_public']),
            models.Index(fields=['price']),
            models.Index(fields=['is_featured']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"

    def clean(self):
        """Enterprise-grade validation"""
        if self.original_price and self.original_price < self.price:
            raise ValidationError("Original price cannot be less than current price")
        
        if self.data_limit_mb and self.data_limit_mb <= 0:
            raise ValidationError("Data limit must be positive")

    @property
    def is_available(self):
        """Check if package is available for purchase"""
        if not self.is_active:
            return False
            
        if self.total_quantity and self.sold_quantity >= self.total_quantity:
            return False
            
        return True

    @property
    def is_unlimited(self):
        """Check if package has unlimited data"""
        return self.data_limit_mb is None

    @property
    def discount_percentage(self):
        """Calculate discount percentage for display"""
        if self.original_price and self.original_price > self.price:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0

    @property
    def available_quantity(self):
        """Get available quantity"""
        if self.total_quantity:
            return max(0, self.total_quantity - self.sold_quantity)
        return None

    def get_radius_attributes(self):
        """Generate RADIUS attributes for enterprise network integration"""
        attributes = {
            'Mikrotik-Rate-Limit': f"{self.speed_limit_mbps}M/{self.speed_limit_mbps}M",
            'Session-Timeout': int(self.duration.total_seconds()),
        }
        
        # Add QoS based on priority
        if self.qos_priority == 'premium':
            attributes['QoS-Priority'] = 'high'
        elif self.qos_priority == 'business':
            attributes['QoS-Priority'] = 'critical'
        elif self.qos_priority == 'real_time':
            attributes['QoS-Priority'] = 'real-time'
            
        return attributes

    def increment_sales(self):
        """Increment sold quantity - thread-safe"""
        if self.total_quantity:
            self.sold_quantity = models.F('sold_quantity') + 1
            self.save(update_fields=['sold_quantity'])


class DispatchVoucher(TimeStampedModel):
    """Dynamically generated vouchers linked to user accounts after purchase"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('exhausted', 'Data Exhausted'),
        ('suspended', 'Suspended'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Core Information - Dynamically generated
    voucher_code = models.CharField(max_length=255, unique=True, db_index=True)
    package = models.ForeignKey(PackageType, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dispatch_vouchers')
    location = models.ForeignKey('locations.Location', on_delete=models.CASCADE)
    
    # Purchase Details
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)
    activated_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    
    # Usage Tracking
    download_bytes = models.BigIntegerField(default=0)
    upload_bytes = models.BigIntegerField(default=0)
    session_count = models.IntegerField(default=0)
    
    # Status Management
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Device Management
    allowed_mac_addresses = models.JSONField(default=list, help_text="List of allowed MAC addresses")
    concurrent_sessions = models.IntegerField(default=0)
    
    # Roaming Information
    is_roaming = models.BooleanField(default=False)
    home_location = models.ForeignKey(
        'locations.Location', 
        on_delete=models.CASCADE, 
        related_name='home_dispatch_vouchers'
    )
    
    # Business Logic Tracking
    transaction_id = models.CharField(max_length=255, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'dispatch_vouchers'
        indexes = [
            models.Index(fields=['voucher_code']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['activated_at']),
            models.Index(fields=['is_roaming']),
            models.Index(fields=['transaction_id']),
        ]
        verbose_name = "Dispatch Voucher"
        verbose_name_plural = "Dispatch Vouchers"

    def __str__(self):
        return f"{self.voucher_code} - {self.user.username} - {self.status}"

    def save(self, *args, **kwargs):
        """Set expires_at based on package duration"""
        if not self.expires_at and self.package.duration:
            self.expires_at = self.activated_at + self.package.duration
        
        # Generate unique voucher code if not provided
        if not self.voucher_code:
            self.voucher_code = f"DISP-{uuid.uuid4().hex[:12].upper()}"
            
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        """Check if voucher is currently active"""
        now = timezone.now()
        return (self.status == 'active' and 
                now >= self.activated_at and 
                now <= self.expires_at and
                not self.is_data_exhausted)

    @property
    def is_data_exhausted(self):
        """Check if data limit is exhausted"""
        if self.package.is_unlimited:
            return False
            
        total_used = self.download_bytes + self.upload_bytes
        data_limit_bytes = self.package.data_limit_mb * 1024 * 1024 if self.package.data_limit_mb else None
        
        return data_limit_bytes and total_used >= data_limit_bytes

    @property
    def remaining_bytes(self):
        """Get remaining data bytes"""
        if self.package.is_unlimited:
            return None
            
        data_limit_bytes = self.package.data_limit_mb * 1024 * 1024 if self.package.data_limit_mb else None
        if not data_limit_bytes:
            return None
            
        total_used = self.download_bytes + self.upload_bytes
        return max(0, data_limit_bytes - total_used)

    @property
    def remaining_duration(self):
        """Get remaining time"""
        now = timezone.now()
        if now > self.expires_at:
            return timedelta(0)
        return self.expires_at - now

    def update_usage(self, download_bytes, upload_bytes):
        """Update usage statistics"""
        self.download_bytes += download_bytes
        self.upload_bytes += upload_bytes
        self.session_count += 1
        
        # Update status if data exhausted
        if self.is_data_exhausted:
            self.status = 'exhausted'
        
        self.save()

    def can_device_connect(self, mac_address):
        """Check if device can connect with this voucher"""
        if not self.is_active:
            return False
            
        if self.allowed_mac_addresses and mac_address not in self.allowed_mac_addresses:
            return False
            
        return True

    def add_allowed_device(self, mac_address):
        """Add device to allowed list"""
        if mac_address not in self.allowed_mac_addresses:
            self.allowed_mac_addresses.append(mac_address)
            self.save()

    def get_network_attributes(self):
        """Get network attributes for RADIUS/Mikrotik"""
        attributes = self.package.get_radius_attributes()
        
        # Add voucher-specific attributes
        if self.allowed_mac_addresses:
            attributes['Allowed-MAC-Addresses'] = ','.join(self.allowed_mac_addresses)
            
        if self.is_roaming:
            attributes['Roaming'] = 'true'
            
        return attributes


class AvailableVoucher(TimeStampedModel):
    """Pre-generated vouchers as fallback when dynamic generation fails"""
    
    VOUCHER_TYPES = [
        ('pre_generated', 'Pre-generated'),
        ('bulk', 'Bulk Voucher'),
        ('promotional', 'Promotional'),
    ]
    
    # Core Information - Pre-generated
    voucher_code = models.CharField(max_length=255, unique=True)
    voucher_type = models.CharField(max_length=20, choices=VOUCHER_TYPES, default='pre_generated')
    package = models.ForeignKey(PackageType, on_delete=models.CASCADE)
    location = models.ForeignKey('locations.Location', on_delete=models.CASCADE)
    
    # Status
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    used_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Batch Management
    batch_id = models.CharField(max_length=100, blank=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_vouchers')
    
    # Fallback Configuration
    is_roaming = models.BooleanField(default=False)
    price_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'available_vouchers'
        indexes = [
            models.Index(fields=['voucher_code']),
            models.Index(fields=['is_used']),
            models.Index(fields=['batch_id']),
            models.Index(fields=['location']),
            models.Index(fields=['valid_until']),
        ]
        verbose_name = "Available Voucher"
        verbose_name_plural = "Available Vouchers"

    def __str__(self):
        return f"{self.voucher_code} - {self.package.name}"

    @property
    def is_valid(self):
        """Check if voucher is valid for use as fallback"""
        if self.is_used:
            return False
            
        if self.valid_until and timezone.now() > self.valid_until:
            return False
            
        return self.package.is_available

    @property
    def final_price(self):
        """Get final price (override or package price)"""
        return self.price_override if self.price_override else self.package.price

    def mark_used(self, user):
        """Mark voucher as used"""
        self.is_used = True
        self.used_at = timezone.now()
        self.used_by = user
        self.save()

    def activate_as_fallback(self, user, location=None):
        """Activate pre-generated voucher as fallback and create dispatch voucher"""
        if not self.is_valid:
            raise ValidationError("Voucher is not valid for activation")
        
        # Use provided location or voucher's default location
        activation_location = location or self.location
        
        # Create dispatch voucher from this pre-generated one
        dispatch = DispatchVoucher.objects.create(
            voucher_code=self.voucher_code,
            package=self.package,
            location=activation_location,
            user=user,
            price_paid=self.final_price,
            is_roaming=self.is_roaming,
            home_location=activation_location,
        )
        
        # Mark as used
        self.mark_used(user)
        
        return dispatch

    @classmethod
    def generate_batch(cls, package, location, count, batch_id, generated_by, price_override=None):
        """Generate batch of pre-generated vouchers as fallback"""
        vouchers = []
        for i in range(count):
            voucher = cls(
                voucher_code=f"FALLBACK-{batch_id}-{i+1:06d}",
                package=package,
                location=location,
                batch_id=batch_id,
                generated_by=generated_by,
                voucher_type='bulk',
                price_override=price_override
            )
            vouchers.append(voucher)
        
        cls.objects.bulk_create(vouchers)
        return vouchers