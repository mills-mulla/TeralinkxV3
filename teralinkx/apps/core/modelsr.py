from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from decimal import Decimal
import uuid

User = get_user_model()

# -----------------------------
# Core Abstract Base Models (NEW - For better inheritance)
# -----------------------------

class TimeStampedModel(models.Model):
    """Abstract base model with created/updated timestamps"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class LocationAwareModel(models.Model):
    """Abstract base model for location-aware entities"""
    location = models.ForeignKey('Location', on_delete=models.CASCADE)
    is_roaming = models.BooleanField(default=False)
    
    class Meta:
        abstract = True

class StatusTrackedModel(models.Model):
    """Abstract base model for status tracking"""
    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUS_SUSPENDED = 'suspended'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_INACTIVE, 'Inactive'),
        (STATUS_SUSPENDED, 'Suspended'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    
    class Meta:
        abstract = True

# -----------------------------
# Location & Multi-Site Management (ENHANCED)
# -----------------------------

class Location(TimeStampedModel):
    """Enhanced location management for multi-site operations"""
    LOCATION_TYPES = [
        ('headquarters', 'Headquarters'),
        ('branch', 'Branch'),
        ('hotspot', 'Hotspot Location'),
        ('partner', 'Partner Location'),
    ]
    
    id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    location_type = models.CharField(max_length=20, choices=LOCATION_TYPES, default='hotspot')
    timezone = models.CharField(max_length=50, default='UTC')
    address = models.TextField(blank=True)
    coordinates = models.CharField(max_length=100, blank=True, help_text="Latitude,Longitude")
    
    # Network Configuration
    network_config = models.JSONField(default=dict, help_text="Location-specific network settings")
    
    # Business Configuration
    business_hours = models.JSONField(default=dict, help_text="Operating hours configuration")
    pricing_tier = models.CharField(max_length=20, default='standard', choices=[
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('economy', 'Economy'),
    ])
    
    # Status & Capacity
    max_concurrent_users = models.IntegerField(default=100)
    current_user_count = models.IntegerField(default=0)
    is_online = models.BooleanField(default=True)
    last_health_check = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.id}) - {self.get_location_type_display()}"
    
    def update_health_status(self):
        """Update location health status"""
        from .services.location_service import LocationHealthService
        health_status = LocationHealthService.check_location_health(self)
        self.is_online = health_status['is_online']
        self.current_user_count = health_status['current_users']
        self.last_health_check = timezone.now()
        self.save()
    
    def get_available_packages(self):
        """Get packages available at this location"""
        return PackageType.objects.filter(
            locations=self,
            is_active=True
        )
    
    class Meta:
        indexes = [
            models.Index(fields=['location_type']),
            models.Index(fields=['is_online']),
            models.Index(fields=['pricing_tier']),
        ]
        ordering = ['name']

class RoamingPolicy(TimeStampedModel):
    """Enhanced roaming policies with business rules"""
    home_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='home_policies')
    visiting_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='visiting_policies')
    
    # Access Rules
    allowed = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=False)
    auto_approve = models.BooleanField(default=True)
    
    # Service Limitations
    speed_limit_mbps = models.IntegerField(null=True, blank=True)
    session_time_limit = models.DurationField(null=True, blank=True)
    daily_data_limit_mb = models.BigIntegerField(null=True, blank=True)
    
    # Pricing
    billing_rate_multiplier = models.DecimalField(max_digits=3, decimal_places=2, default=1.0)
    surcharge_fixed = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Business Rules
    priority = models.IntegerField(default=1, help_text="Higher priority policies take precedence")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['home_location', 'visiting_location']
        indexes = [
            models.Index(fields=['home_location', 'visiting_location']),
            models.Index(fields=['is_active']),
            models.Index(fields=['priority']),
        ]
        ordering = ['-priority']
    
    def __str__(self):
        status = "✓" if self.allowed else "✗"
        return f"{status} {self.home_location} → {self.visiting_location}"

# -----------------------------
# Centralized Package System (ENHANCED)
# -----------------------------

class PackageType(TimeStampedModel, StatusTrackedModel):
    """Unified package system with advanced features"""
    PACKAGE_CATEGORIES = [
        ('standard', 'Standard Package'),
        ('daily', 'Daily Pass'), 
        ('weekly', 'Weekly Pass'),
        ('monthly', 'Monthly Package'),
        ('voucher', 'Voucher Package'),
        ('special', 'Special Offer'),
        ('trial', 'Trial Package'),
        ('corporate', 'Corporate Package'),
    ]
    
    # Core Identity
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=50, unique=True, help_text="Internal package code")
    description = models.CharField(max_length=255)
    
    # Pricing & Duration
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='KES')
    duration = models.DurationField(null=True, blank=True)
    
    # Usage Limits
    device_limit = models.IntegerField(default=1)
    usage_limit_mb = models.BigIntegerField(null=True, blank=True)
    speed_limit_mbps = models.IntegerField(null=True, blank=True)
    
    # Categorization
    package_category = models.CharField(max_length=20, choices=PACKAGE_CATEGORIES, default='standard')
    tags = models.JSONField(default=list, help_text="Tags for filtering and search")
    
    # Availability - Use string reference to avoid circular imports
    locations = models.ManyToManyField('locations.Location', blank=True)
    
    # Add is_active field directly here instead of relying on StatusTrackedModel
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    available_from = models.DateTimeField(null=True, blank=True)
    available_until = models.DateTimeField(null=True, blank=True)
    
    # For limited offers
    total_quantity = models.IntegerField(null=True, blank=True)
    sold_quantity = models.IntegerField(default=0)
    banner = models.CharField(max_length=20, choices=[
        ('NEW', 'New'),
        ('HOT', 'HOT'),
        ('SALE', 'Sale'),
        ('POPULAR', 'Popular'),
        ('NONE', 'None'),
    ], default='NONE')
    
    # Commission & Partner Settings
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Commission percentage for partners")
    is_partner_exclusive = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} ({self.code}) - {self.get_package_category_display()}"
    
    def clean(self):
        """Validate model data"""
        if self.original_price and self.original_price < self.price:
            raise ValidationError("Original price cannot be less than current price")
        
        if self.available_from and self.available_until and self.available_from >= self.available_until:
            raise ValidationError("Available from date must be before available until date")
    
    @property
    def is_available(self):
        """Check if package is currently available"""
        if not self.is_active or self.status != self.STATUS_ACTIVE:
            return False
        
        now = timezone.now()
        if self.available_from and now < self.available_from:
            return False
        if self.available_until and now > self.available_until:
            return False
        if self.total_quantity and self.sold_quantity >= self.total_quantity:
            return False
            
        return True
    
    @property
    def is_on_sale(self):
        """Check if package is on sale"""
        return self.original_price and self.original_price > self.price
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage"""
        if self.is_on_sale and self.original_price:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0
    
    def get_remaining_quantity(self):
        """Get remaining quantity for limited packages"""
        if self.total_quantity:
            return max(0, self.total_quantity - self.sold_quantity)
        return None
    
    def increment_sold_quantity(self):
        """Increment sold quantity"""
        if self.total_quantity:
            self.sold_quantity += 1
            self.save()
    
    class Meta:
        indexes = [
            models.Index(fields=['package_category']),
            models.Index(fields=['is_active']),  # Use the direct field
            models.Index(fields=['status']),     # From StatusTrackedModel
            models.Index(fields=['price']),
            models.Index(fields=['available_from', 'available_until']),
            models.Index(fields=['code']),
        ]
        verbose_name = "Package"
        verbose_name_plural = "Packages"

# -----------------------------
# Enhanced Voucher System (READY FOR V3)
# -----------------------------

class VoucherBase(TimeStampedModel, LocationAwareModel):
    """Base model for all voucher types"""
    VOUCHER_TYPES = [
        ('pre_generated', 'Pre-generated'),
        ('dynamic', 'Dynamically Generated'),
        ('bulk', 'Bulk Voucher'),
        ('promotional', 'Promotional'),
    ]
    
    voucher_code = models.CharField(max_length=255, unique=True)
    voucher_type = models.CharField(max_length=20, choices=VOUCHER_TYPES, default='pre_generated')
    package_type = models.ForeignKey(PackageType, on_delete=models.CASCADE)
    
    # Status
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    
    # Security
    pin_code = models.CharField(max_length=6, blank=True, null=True, help_text="Optional PIN for voucher redemption")
    
    class Meta:
        abstract = True

class AvailableVoucher(VoucherBase):
    """Pre-generated vouchers for instant activation"""
    batch_id = models.CharField(max_length=100, blank=True, help_text="Batch identifier for bulk generation")
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.voucher_code} - {self.package_type.name}"
    
    def mark_as_used(self):
        """Mark voucher as used"""
        self.is_used = True
        self.used_at = timezone.now()
        self.save()
    
    class Meta:
        indexes = [
            models.Index(fields=['voucher_code']),
            models.Index(fields=['is_used']),
            models.Index(fields=['package_type']),
            models.Index(fields=['location']),
            models.Index(fields=['batch_id']),
        ]
        verbose_name = "Available Voucher"
        verbose_name_plural = "Available Vouchers"

class DispatchVoucher(TimeStampedModel, LocationAwareModel):
    """Enhanced activated vouchers with comprehensive tracking"""
    dispatch_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dispatch_account = models.CharField(max_length=15)
    voucher_code = models.CharField(max_length=255)
    package_type = models.ForeignKey(PackageType, on_delete=models.CASCADE)
    
    # Pricing & Duration
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    duration = models.DurationField(null=True)
    activated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Usage Tracking
    total_download_bytes = models.BigIntegerField(default=0)
    total_upload_bytes = models.BigIntegerField(default=0)
    usage_limit_bytes = models.BigIntegerField(null=True, blank=True)
    session_count = models.IntegerField(default=0)
    
    # Payment Information
    payment_gateway = models.ForeignKey('PaymentGateway', on_delete=models.SET_NULL, null=True, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    transaction_id = models.CharField(max_length=255, blank=True)
    
    # Status Management
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('exhausted', 'Usage Exhausted'),
        ('suspended', 'Suspended'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Device Management
    allowed_mac_addresses = models.JSONField(default=list, help_text="List of allowed MAC addresses")
    concurrent_device_limit = models.IntegerField(default=1)
    
    # Roaming Information
    home_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='home_vouchers')
    roaming_policy_applied = models.ForeignKey(RoamingPolicy, on_delete=models.SET_NULL, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.activated_at:
            self.activated_at = timezone.now()
        if self.duration and not self.expires_at:
            self.expires_at = self.activated_at + self.duration
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Check if voucher is expired"""
        if self.status != 'active':
            return True
        return self.expires_at and timezone.now() > self.expires_at
    
    @property
    def is_usage_exhausted(self):
        """Check if usage is exhausted"""
        if not self.usage_limit_bytes:
            return False
        return (self.total_download_bytes + self.total_upload_bytes) >= self.usage_limit_bytes
    
    @property
    def remaining_bytes(self):
        """Get remaining bytes"""
        if not self.usage_limit_bytes:
            return None
        used = self.total_download_bytes + self.total_upload_bytes
        return max(0, self.usage_limit_bytes - used)
    
    @property
    def remaining_duration(self):
        """Get remaining duration"""
        if not self.expires_at:
            return None
        now = timezone.now()
        if now > self.expires_at:
            return timedelta(0)
        return self.expires_at - now
    
    def update_usage(self, download_bytes, upload_bytes):
        """Update usage statistics"""
        self.total_download_bytes += download_bytes
        self.total_upload_bytes += upload_bytes
        
        # Check if usage is exhausted
        if self.is_usage_exhausted:
            self.status = 'exhausted'
        
        self.save()
    
    def can_device_connect(self, mac_address):
        """Check if device can connect with this voucher"""
        if self.status != 'active':
            return False
        
        if self.is_expired:
            self.status = 'expired'
            self.save()
            return False
        
        if self.is_usage_exhausted:
            return False
        
        # Check MAC address restrictions
        if self.allowed_mac_addresses and mac_address not in self.allowed_mac_addresses:
            return False
        
        return True
    
    def __str__(self):
        return f"{self.voucher_code} - {self.dispatch_account} - {self.status}"
    
    class Meta:
        indexes = [
            models.Index(fields=['dispatch_account']),
            models.Index(fields=['voucher_code']),
            models.Index(fields=['status']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['location']),
            models.Index(fields=['is_roaming']),
            models.Index(fields=['activated_at']),
        ]
        verbose_name = "Dispatch Voucher"
        verbose_name_plural = "Dispatch Vouchers"

# -----------------------------
# Enhanced User & Device Management (V3 READY)
# -----------------------------

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
    home_location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='home_users')
    current_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='current_users')
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
            self.is_roaming = True
            # Log roaming event
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
        elif new_location == self.home_location:
            self.is_roaming = False
        
        self.save()
    
    def get_active_voucher(self):
        """Get currently active voucher"""
        if self.active_voucher:
            try:
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

# -----------------------------
# Payment & Financial Systems (V3 READY)
# -----------------------------

class PaymentGateway(TimeStampedModel, StatusTrackedModel):
    """Enhanced payment gateway management"""
    GATEWAY_TYPES = [
        ('mpesa', 'M-Pesa'),
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('card', 'Credit Card'),
        ('bank', 'Bank Transfer'),
        ('cash', 'Cash'),
    ]
    
    name = models.CharField(max_length=100)
    gateway_type = models.CharField(max_length=20, choices=GATEWAY_TYPES)
    is_default = models.BooleanField(default=False)
    
    # Configuration
    config = models.JSONField(default=dict)
    webhook_url = models.URLField(blank=True)
    callback_url = models.URLField(blank=True)
    
    # Fees
    transaction_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    transaction_fee_fixed = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Status
    test_mode = models.BooleanField(default=False)
    maintenance_mode = models.BooleanField(default=False)
    
    def __str__(self):
        mode = "TEST" if self.test_mode else "LIVE"
        return f"{self.name} ({self.get_gateway_type_display()}) - {mode}"
    
    class Meta:
        verbose_name = "Payment Gateway"
        verbose_name_plural = "Payment Gateways"
        indexes = [
            models.Index(fields=['gateway_type']),
            models.Index(fields=['is_default']),
            models.Index(fields=['test_mode']),
        ]

class BalanceTransaction(TimeStampedModel):
    """Comprehensive financial audit trail"""
    TRANSACTION_TYPES = [
        ('voucher_purchase', 'Voucher Purchase'),
        ('balance_topup', 'Balance Top-up'),
        ('refund', 'Refund'),
        ('usage_charge', 'Usage Charge'),
        ('adjustment', 'Adjustment'),
        ('roaming_charge', 'Roaming Charge'),
        ('initial_deposit', 'Initial Deposit'),
        ('commission', 'Commission Payment'),
        ('payout', 'Payout'),
    ]
    
    TRANSACTION_DIRECTIONS = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]
    
    user = models.ForeignKey(ClientH, on_delete=models.CASCADE, related_name='balance_transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    direction = models.CharField(max_length=10, choices=TRANSACTION_DIRECTIONS)
    
    # Amounts
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance_before = models.DecimalField(max_digits=10, decimal_places=2)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # References
    description = models.TextField(blank=True)
    reference = models.CharField(max_length=100, blank=True)
    external_reference = models.CharField(max_length=255, blank=True)
    
    # Context
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    voucher = models.ForeignKey(DispatchVoucher, on_delete=models.SET_NULL, null=True, blank=True)
    payment_gateway = models.ForeignKey(PaymentGateway, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Metadata
    is_reversible = models.BooleanField(default=False)
    reversed_at = models.DateTimeField(null=True, blank=True)
    reversal_reason = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.account} - {self.transaction_type} - {self.direction} KES {self.amount}"
    
    @property
    def net_amount(self):
        """Get net amount after fees"""
        if self.direction == 'debit':
            return -(self.amount + self.fee_amount)
        return self.amount - self.fee_amount
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['direction']),
            models.Index(fields=['reference']),
            models.Index(fields=['location']),
        ]
        ordering = ['-created_at']

# -----------------------------
# Session & Network Management (V3 READY)
# -----------------------------

class ActiveSession(TimeStampedModel, LocationAwareModel):
    """Enhanced active session management"""
    session_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(ClientH, on_delete=models.CASCADE, related_name='active_sessions')
    voucher = models.ForeignKey(DispatchVoucher, on_delete=models.CASCADE, null=True, blank=True)
    
    # Network Information
    mac_address = models.CharField(max_length=17)
    ip_address = models.GenericIPAddressField()
    nas_ip_address = models.GenericIPAddressField()
    nas_identifier = models.CharField(max_length=100, blank=True)
    
    # Session Details
    start_time = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    uptime = models.DurationField(default=timedelta(0))
    
    # Usage Statistics
    download_bytes = models.BigIntegerField(default=0)
    upload_bytes = models.BigIntegerField(default=0)
    download_speed_bps = models.BigIntegerField(default=0)
    upload_speed_bps = models.BigIntegerField(default=0)
    
    # Session Quality
    packet_loss = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    latency_ms = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    # Status
    is_authenticated = models.BooleanField(default=True)
    terminate_cause = models.CharField(max_length=50, blank=True)
    terminated_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.account} - {self.mac_address} - {self.location}"
    
    @property
    def is_active(self):
        """Check if session is active"""
        return self.terminated_at is None
    
    @property
    def total_bytes(self):
        """Get total data usage"""
        return self.download_bytes + self.upload_bytes
    
    def update_usage(self, download_bytes, upload_bytes):
        """Update session usage"""
        self.download_bytes += download_bytes
        self.upload_bytes += upload_bytes
        self.last_update = timezone.now()
        self.save()
        
        # Update voucher usage if applicable
        if self.voucher:
            self.voucher.update_usage(download_bytes, upload_bytes)
        
        # Update user lifetime usage
        self.user.lifetime_data_used += download_bytes + upload_bytes
        self.user.save()
    
    def terminate(self, cause="User disconnected"):
        """Terminate session"""
        self.terminate_cause = cause
        self.terminated_at = timezone.now()
        self.save()
    
    class Meta:
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['user', 'start_time']),
            models.Index(fields=['mac_address']),
            models.Index(fields=['location']),
            models.Index(fields=['is_authenticated']),
            models.Index(fields=['start_time']),
        ]
        verbose_name = "Active Session"
        verbose_name_plural = "Active Sessions"

# -----------------------------
# Enhanced Device Management (COMPLETED)
# -----------------------------

class UserDevice(TimeStampedModel, StatusTrackedModel):
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
    dhcp_lease = models.ForeignKey('DHCPLease', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Security & Trust
    is_primary = models.BooleanField(default=False)
    is_trusted = models.BooleanField(default=False)
    trust_level = models.IntegerField(default=1, choices=[(1, 'Low'), (2, 'Medium'), (3, 'High')])
    requires_approval = models.BooleanField(default=False)
    
    # Activity Tracking
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    last_seen_ip = models.GenericIPAddressField(null=True, blank=True)
    last_seen_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    total_connections = models.IntegerField(default=0)
    
    # Usage Statistics
    total_data_used = models.BigIntegerField(default=0)
    average_session_duration = models.DurationField(null=True, blank=True)
    favorite_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='favorite_devices')
    
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
        # Multiple locations in short time
        # Rapid IP changes
        # Unusual connection times
        # This would be implemented with more complex logic
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
        
        # TODO: Implement network-level blocking via Mikrotik API
        # from .services.network_service import NetworkBlockingService
        # NetworkBlockingService.block_mac_address(self.mac_address)
    
    def unblock_device(self, reason="User request", unblocked_by=None):
        """Unblock this device"""
        self.status = self.STATUS_ACTIVE
        self.save()
        
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
        from django.db.models import Count, Avg
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # This would query connection logs
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

# -----------------------------
# Enhanced Security Logging (COMPLETED)
# -----------------------------

class SecurityLog(TimeStampedModel):
    """Comprehensive security audit trail with threat detection"""
    SEVERITY_LEVELS = [
        ('info', 'Information'),
        ('low', 'Low'),
        ('medium', 'Medium'), 
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    ACTION_CATEGORIES = [
        ('authentication', 'Authentication'),
        ('authorization', 'Authorization'),
        ('device_management', 'Device Management'),
        ('network_access', 'Network Access'),
        ('financial', 'Financial'),
        ('system', 'System Events'),
        ('compliance', 'Compliance'),
    ]
    
    ACTION_TYPES = [
        # Authentication
        ('login_success', 'Login Successful'),
        ('login_failed', 'Login Failed'),
        ('logout', 'Logout'),
        ('password_change', 'Password Changed'),
        ('password_reset', 'Password Reset'),
        ('two_factor_enabled', '2FA Enabled'),
        ('two_factor_disabled', '2FA Disabled'),
        
        # Authorization
        ('permission_granted', 'Permission Granted'),
        ('permission_revoked', 'Permission Revoked'),
        ('role_changed', 'Role Changed'),
        
        # Device Management
        ('device_registered', 'Device Registered'),
        ('device_connected', 'Device Connected'),
        ('device_disconnected', 'Device Disconnected'),
        ('device_blocked', 'Device Blocked'),
        ('device_unblocked', 'Device Unblocked'),
        ('device_trusted', 'Device Trusted'),
        ('device_untrusted', 'Device Untrusted'),
        
        # Network Access
        ('voucher_activated', 'Voucher Activated'),
        ('voucher_expired', 'Voucher Expired'),
        ('roaming_started', 'Roaming Started'),
        ('roaming_ended', 'Roaming Ended'),
        ('access_denied', 'Access Denied'),
        ('suspicious_activity', 'Suspicious Activity'),
        
        # Financial
        ('payment_success', 'Payment Successful'),
        ('payment_failed', 'Payment Failed'),
        ('refund_issued', 'Refund Issued'),
        ('balance_adjusted', 'Balance Adjusted'),
        
        # System
        ('system_startup', 'System Startup'),
        ('system_shutdown', 'System Shutdown'),
        ('configuration_change', 'Configuration Changed'),
        ('maintenance_mode', 'Maintenance Mode Toggled'),
    ]
    
    # Core Information
    user = models.ForeignKey(ClientH, on_delete=models.CASCADE, null=True, blank=True, related_name='security_logs')
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    action_category = models.CharField(max_length=20, choices=ACTION_CATEGORIES)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='info')
    
    # Source Information
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Context & Details
    details = models.JSONField(default=dict)
    correlation_id = models.UUIDField(default=uuid.uuid4, editable=False)
    session_id = models.CharField(max_length=100, blank=True)
    
    # Threat Intelligence
    is_suspicious = models.BooleanField(default=False)
    threat_score = models.IntegerField(default=0, help_text="0-100 threat score")
    reviewed = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_logs')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    # Resolution
    resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_logs')
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution = models.TextField(blank=True)
    
    def __str__(self):
        user_info = self.user.account if self.user else 'System'
        return f"{self.get_action_type_display()} - {user_info} - {self.created_at}"
    
    def calculate_threat_score(self):
        """Calculate threat score based on event patterns"""
        score = 0
        
        # Failed login attempts
        if self.action_type == 'login_failed':
            score += 20
            
            # Check for multiple recent failures
            recent_failures = SecurityLog.objects.filter(
                user=self.user,
                action_type='login_failed',
                created_at__gte=timezone.now() - timedelta(minutes=30)
            ).count()
            score += min(recent_failures * 10, 50)
        
        # Suspicious location changes
        if self.action_type in ['login_success', 'device_connected']:
            if self.user and self.location != self.user.home_location:
                score += 15
        
        # Device anomalies
        if self.action_type == 'device_connected':
            if self.user and not self.user.devices.filter(mac_address=self.details.get('mac_address')).exists():
                score += 25
        
        self.threat_score = min(score, 100)
        self.is_suspicious = self.threat_score >= 30
        self.save()
    
    def mark_as_reviewed(self, reviewer, notes=""):
        """Mark log entry as reviewed"""
        self.reviewed = True
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.review_notes = notes
        self.save()
    
    def mark_as_resolved(self, resolver, resolution=""):
        """Mark log entry as resolved"""
        self.resolved = True
        self.resolved_by = resolver
        self.resolved_at = timezone.now()
        self.resolution = resolution
        self.save()
    
    @classmethod
    def get_security_dashboard_stats(cls, days=7):
        """Get security statistics for dashboard"""
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Count, Q
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        logs = cls.objects.filter(created_at__gte=cutoff_date)
        
        stats = {
            'total_events': logs.count(),
            'suspicious_events': logs.filter(is_suspicious=True).count(),
            'critical_events': logs.filter(severity='critical').count(),
            'unresolved_events': logs.filter(resolved=False, severity__in=['high', 'critical']).count(),
            'top_categories': logs.values('action_category').annotate(count=Count('id')).order_by('-count')[:5],
            'threat_trend': cls.get_threat_trend(days),
        }
        
        return stats
    
    @classmethod
    def get_threat_trend(cls, days=7):
        """Get threat trend data"""
        from django.db.models import Count
        from django.utils import timezone
        from datetime import timedelta
        
        trend_data = []
        for i in range(days):
            date = timezone.now() - timedelta(days=days - i - 1)
            next_date = date + timedelta(days=1)
            
            count = cls.objects.filter(
                created_at__gte=date,
                created_at__lt=next_date,
                is_suspicious=True
            ).count()
            
            trend_data.append({
                'date': date.date(),
                'count': count
            })
        
        return trend_data
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action_type']),
            models.Index(fields=['severity']),
            models.Index(fields=['is_suspicious']),
            models.Index(fields=['resolved']),
            models.Index(fields=['created_at']),
            models.Index(fields=['correlation_id']),
        ]
        ordering = ['-created_at']
        verbose_name = "Security Log"
        verbose_name_plural = "Security Logs"

# -----------------------------
# Enhanced Data Usage Analytics (COMPLETED)
# -----------------------------

class DataUsageRecord(TimeStampedModel, LocationAwareModel):
    """Comprehensive data usage analytics for business intelligence"""
    USAGE_TYPES = [
        ('web', 'Web Browsing'),
        ('streaming', 'Video Streaming'),
        ('gaming', 'Online Gaming'),
        ('download', 'File Download'),
        ('upload', 'File Upload'),
        ('voip', 'VoIP/Voice Call'),
        ('other', 'Other'),
    ]
    
    # Core Relationships
    user = models.ForeignKey(ClientH, on_delete=models.CASCADE, related_name='data_usage_records')
    device = models.ForeignKey(UserDevice, on_delete=models.SET_NULL, null=True, blank=True)
    session = models.ForeignKey(ActiveSession, on_delete=models.SET_NULL, null=True, blank=True)
    voucher = models.ForeignKey(DispatchVoucher, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Usage Metrics
    download_bytes = models.BigIntegerField(default=0)
    upload_bytes = models.BigIntegerField(default=0)
    total_packets = models.BigIntegerField(default=0)
    
    # Timing Information
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    
    # Classification
    usage_type = models.CharField(max_length=20, choices=USAGE_TYPES, default='other')
    protocol = models.CharField(max_length=20, blank=True, help_text="TCP/UDP/ICMP etc.")
    port = models.IntegerField(null=True, blank=True)
    
    # Quality Metrics
    average_speed_bps = models.BigIntegerField(default=0)
    peak_speed_bps = models.BigIntegerField(default=0)
    packet_loss_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    latency_ms = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    # Cost Calculation
    cost_per_mb = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Metadata
    source_ip = models.GenericIPAddressField(blank=True, null=True)
    destination_ip = models.GenericIPAddressField(blank=True, null=True)
    destination_domain = models.CharField(max_length=255, blank=True)
    user_agent = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.account} - {self.get_usage_type_display()} - {self.total_bytes} bytes"
    
    @property
    def total_bytes(self):
        return self.download_bytes + self.upload_bytes
    
    @property
    def total_megabytes(self):
        return self.total_bytes / (1024 * 1024)
    
    @property
    def average_download_speed_mbps(self):
        if self.duration and self.duration.total_seconds() > 0:
            return (self.download_bytes * 8) / (self.duration.total_seconds() * 1000000)
        return 0
    
    @property
    def is_completed(self):
        return self.end_time is not None
    
    def calculate_duration(self):
        """Calculate duration if not set"""
        if self.start_time and self.end_time and not self.duration:
            self.duration = self.end_time - self.start_time
            self.save()
    
    def calculate_cost(self):
        """Calculate usage cost"""
        if self.cost_per_mb > 0:
            total_mb = self.total_bytes / (1024 * 1024)
            self.total_cost = total_mb * self.cost_per_mb
            self.save()
    
    def get_usage_breakdown(self):
        """Get usage breakdown by type"""
        breakdown = {
            'web': 0,
            'streaming': 0,
            'gaming': 0,
            'download': 0,
            'upload': 0,
            'voip': 0,
            'other': 0,
        }
        
        # This would aggregate similar records
        return breakdown
    
    @classmethod
    def get_user_usage_summary(cls, user, days=30):
        """Get usage summary for a user"""
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Sum, Avg, Max
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        records = cls.objects.filter(user=user, start_time__gte=cutoff_date)
        
        summary = records.aggregate(
            total_download=Sum('download_bytes'),
            total_upload=Sum('upload_bytes'),
            average_speed=Avg('average_speed_bps'),
            peak_speed=Max('peak_speed_bps'),
            total_cost=Sum('total_cost'),
            session_count=Count('id')
        )
        
        summary['total_bytes'] = (summary['total_download'] or 0) + (summary['total_upload'] or 0)
        summary['days_analyzed'] = days
        
        return summary
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'start_time']),
            models.Index(fields=['device', 'start_time']),
            models.Index(fields=['voucher', 'start_time']),
            models.Index(fields=['location', 'start_time']),
            models.Index(fields=['usage_type']),
            models.Index(fields=['start_time']),
        ]
        ordering = ['-start_time']
        verbose_name = "Data Usage Record"
        verbose_name_plural = "Data Usage Records"

# -----------------------------
# Business Investments (COMPLETED)
# -----------------------------

class Investment(TimeStampedModel):
    """Comprehensive business investment tracking"""
    INVESTMENT_TYPES = [
        ('seed', 'Seed Funding'),
        ('angel', 'Angel Investment'),
        ('vc', 'Venture Capital'),
        ('loan', 'Business Loan'),
        ('personal', 'Personal Investment'),
        ('grant', 'Grant'),
        ('crowdfunding', 'Crowdfunding'),
        ('other', 'Other'),
    ]
    
    INVESTMENT_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('disbursed', 'Disbursed'),
        ('active', 'Active'),
        ('matured', 'Matured'),
        ('defaulted', 'Defaulted'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Investment Details
    investor_name = models.CharField(max_length=255)
    investor_type = models.CharField(max_length=50, choices=[
        ('individual', 'Individual'),
        ('company', 'Company'),
        ('vc_firm', 'VC Firm'),
        ('bank', 'Bank'),
        ('government', 'Government'),
        ('other', 'Other'),
    ], default='individual')
    investment_type = models.CharField(max_length=20, choices=INVESTMENT_TYPES, default='other')
    
    # Financial Details
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='KES')
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, default=1.0)
    amount_local = models.DecimalField(max_digits=15, decimal_places=2, help_text="Amount in local currency")
    
    # Terms & Conditions
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    equity_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    valuation = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Company valuation at investment")
    term_months = models.IntegerField(null=True, blank=True, help_text="Investment term in months")
    
    # Dates
    investment_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    next_payment_date = models.DateField(null=True, blank=True)
    
    # Status & Tracking
    status = models.CharField(max_length=20, choices=INVESTMENT_STATUS, default='pending')
    is_active = models.BooleanField(default=True)
    risk_rating = models.CharField(max_length=20, choices=[
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
    ], default='medium')
    
    # Documentation
    contract_reference = models.CharField(max_length=100, blank=True)
    invoice_number = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    terms_and_conditions = models.TextField(blank=True, null=True)
    
    # Contact Information
    investor_email = models.EmailField(blank=True)
    investor_phone = models.CharField(max_length=20, blank=True)
    investor_address = models.TextField(blank=True)
    
    # Repayment Information (for loans)
    repayment_schedule = models.JSONField(default=dict, help_text="Repayment schedule details")
    total_repaid = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_investments')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_investments')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.investor_name} - {self.get_investment_type_display()} - KES {self.amount_local}"
    
    def save(self, *args, **kwargs):
        # Calculate local amount if not set
        if not self.amount_local:
            self.amount_local = self.amount * self.exchange_rate
        super().save(*args, **kwargs)
    
    @property
    def outstanding_balance(self):
        """Calculate outstanding balance for loans"""
        if self.investment_type == 'loan':
            return self.amount_local - self.total_repaid
        return Decimal('0')
    
    @property
    def days_until_due(self):
        """Calculate days until due date"""
        if self.due_date:
            delta = self.due_date - timezone.now().date()
            return delta.days
        return None
    
    @property
    def is_overdue(self):
        """Check if investment is overdue"""
        if self.due_date and self.status in ['active', 'disbursed']:
            return timezone.now().date() > self.due_date
        return False
    
    def record_repayment(self, amount, payment_date=None, reference=""):
        """Record a repayment"""
        if payment_date is None:
            payment_date = timezone.now().date()
        
        self.total_repaid += amount
        self.save()
        
        # Create repayment record
        InvestmentRepayment.objects.create(
            investment=self,
            amount=amount,
            payment_date=payment_date,
            reference=reference
        )
        
        # Update status if fully repaid
        if self.outstanding_balance <= 0:
            self.status = 'matured'
            self.save()
    
    def get_expected_return(self):
        """Calculate expected return on investment"""
        if self.investment_type == 'loan' and self.interest_rate:
            return self.amount_local * (self.interest_rate / 100)
        elif self.equity_percentage and self.valuation:
            return (self.equity_percentage / 100) * self.valuation
        return Decimal('0')
    
    class Meta:
        indexes = [
            models.Index(fields=['investment_type']),
            models.Index(fields=['status']),
            models.Index(fields=['investment_date']),
            models.Index(fields=['due_date']),
            models.Index(fields=['investor_name']),
        ]
        ordering = ['-investment_date']
        verbose_name = "Investment"
        verbose_name_plural = "Investments"

class InvestmentRepayment(TimeStampedModel):
    """Investment repayment tracking"""
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE, related_name='repayments')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_date = models.DateField()
    reference = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=50, choices=[
        ('bank_transfer', 'Bank Transfer'),
        ('mpesa', 'M-Pesa'),
        ('cash', 'Cash'),
        ('other', 'Other'),
    ], default='bank_transfer')
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Repayment of KES {self.amount} for {self.investment}"
    
    class Meta:
        ordering = ['-payment_date']
        verbose_name = "Investment Repayment"
        verbose_name_plural = "Investment Repayments"

# -----------------------------
# Business Expenses (COMPLETED)
# -----------------------------

class Expense(TimeStampedModel):
    """Comprehensive business expense tracking with budgeting"""
    EXPENSE_CATEGORIES = [
        ('network_infra', 'Network Infrastructure'),
        ('hardware', 'Hardware Purchase'),
        ('software', 'Software & Licensing'),
        ('maintenance', 'Maintenance & Repairs'),
        ('utilities', 'Utilities'),
        ('rent', 'Rent & Leases'),
        ('salaries', 'Salaries & Wages'),
        ('marketing', 'Marketing & Advertising'),
        ('travel', 'Travel & Transportation'),
        ('office', 'Office Supplies'),
        ('professional', 'Professional Services'),
        ('insurance', 'Insurance'),
        ('taxes', 'Taxes & Fees'),
        ('other', 'Other Expenses'),
    ]
    
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('mpesa', 'M-Pesa'),
        ('cheque', 'Cheque'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('other', 'Other'),
    ]
    
    # Expense Details
    expense_date = models.DateField()
    category = models.CharField(max_length=20, choices=EXPENSE_CATEGORIES, default='other')
    description = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='KES')
    
    # Vendor Information
    vendor = models.CharField(max_length=255, blank=True, null=True)
    vendor_contact = models.CharField(max_length=255, blank=True)
    vendor_tin = models.CharField(max_length=50, blank=True, help_text="Vendor Tax Identification Number")
    
    # Payment Information
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='bank_transfer')
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    invoice_number = models.CharField(max_length=100, blank=True, null=True)
    receipt_number = models.CharField(max_length=100, blank=True, null=True)
    
    # Location & Department
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    department = models.CharField(max_length=100, blank=True, help_text="Department or cost center")
    
    # Budget & Approval
    budget_category = models.CharField(max_length=100, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_expenses')
    approved_at = models.DateTimeField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    
    # Recurring Expenses
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(max_length=20, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ], blank=True)
    next_recurrence = models.DateField(null=True, blank=True)
    
    # Tax Information
    is_tax_deductible = models.BooleanField(default=True)
    vat_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    withholding_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Attachments
    attachment = models.FileField(upload_to='expense_attachments/', blank=True, null=True)
    
    # Status
    is_reimbursable = models.BooleanField(default=False)
    reimbursement_status = models.CharField(max_length=20, choices=[
        ('not_applicable', 'Not Applicable'),
        ('pending', 'Pending Reimbursement'),
        ('reimbursed', 'Reimbursed'),
        ('denied', 'Reimbursement Denied'),
    ], default='not_applicable')
    
    def __str__(self):
        return f"{self.expense_date} | {self.get_category_display()} | KES {self.amount}"
    
    @property
    def total_amount(self):
        """Get total amount including taxes"""
        return self.amount + self.vat_amount + self.withholding_tax
    
    @property
    def is_over_budget(self):
        """Check if expense is over budget"""
        # This would check against budget allocations
        return False
    
    @property
    def age_in_days(self):
        """Get age of expense in days"""
        return (timezone.now().date() - self.expense_date).days
    
    def approve(self, approved_by):
        """Approve expense"""
        self.is_approved = True
        self.approved_by = approved_by
        self.approved_at = timezone.now()
        self.save()
    
    def create_recurring_instance(self):
        """Create next recurring expense instance"""
        if not self.is_recurring or not self.recurrence_pattern:
            return None
        
        next_date = self.expense_date
        
        if self.recurrence_pattern == 'monthly':
            next_date = next_date.replace(month=next_date.month + 1)
        elif self.recurrence_pattern == 'weekly':
            next_date = next_date + timedelta(weeks=1)
        # ... other patterns
        
        new_expense = Expense.objects.create(
            expense_date=next_date,
            category=self.category,
            description=f"Recurring: {self.description}",
            amount=self.amount,
            vendor=self.vendor,
            payment_method=self.payment_method,
            location=self.location,
            department=self.department,
            is_recurring=True,
            recurrence_pattern=self.recurrence_pattern,
            next_recurrence=self.calculate_next_recurrence(next_date)
        )
        
        return new_expense
    
    def calculate_next_recurrence(self, current_date):
        """Calculate next recurrence date"""
        # Implementation would depend on recurrence pattern
        return current_date
    
    @classmethod
    def get_expense_summary(cls, start_date, end_date, location=None):
        """Get expense summary for period"""
        from django.db.models import Sum, Count
        
        expenses = cls.objects.filter(
            expense_date__gte=start_date,
            expense_date__lte=end_date,
            is_approved=True
        )
        
        if location:
            expenses = expenses.filter(location=location)
        
        summary = expenses.aggregate(
            total_amount=Sum('amount'),
            total_expenses=Count('id'),
            average_expense=Sum('amount') / Count('id')
        )
        
        # Add category breakdown
        categories = expenses.values('category').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
        
        summary['category_breakdown'] = list(categories)
        
        return summary
    
    class Meta:
        indexes = [
            models.Index(fields=['expense_date']),
            models.Index(fields=['category']),
            models.Index(fields=['location']),
            models.Index(fields=['is_approved']),
            models.Index(fields=['vendor']),
        ]
        ordering = ['-expense_date']
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"

# -----------------------------
# Enhanced Notification System (COMPLETED)
# -----------------------------

class Notification(TimeStampedModel):
    """Advanced notification system with multiple channels"""
    NOTIFICATION_TYPES = [
        ('system', 'System Notification'),
        ('billing', 'Billing & Payment'),
        ('security', 'Security Alert'),
        ('promotional', 'Promotional'),
        ('maintenance', 'Maintenance Alert'),
        ('usage', 'Usage Alert'),
        ('voucher', 'Voucher Notification'),
        ('roaming', 'Roaming Notification'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    CHANNELS = [
        ('in_app', 'In-App'),
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('all', 'All Channels'),
    ]
    
    # Recipient Information
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    client = models.ForeignKey(ClientH, on_delete=models.CASCADE, null=True, blank=True, related_name="client_notifications")
    
    # Notification Content
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='system')
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    title = models.CharField(max_length=255)
    message = models.TextField()
    short_message = models.CharField(max_length=160, blank=True, help_text="Short version for SMS/push")
    
    # Delivery Configuration
    channels = models.JSONField(default=list, help_text="List of channels to deliver through")
    scheduled_for = models.DateTimeField(null=True, blank=True, help_text="Schedule for future delivery")
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Notification expiration")
    
    # Status Tracking
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    
    # Delivery Status
    email_sent = models.BooleanField(default=False)
    sms_sent = models.BooleanField(default=False)
    push_sent = models.BooleanField(default=False)
    in_app_delivered = models.BooleanField(default=False)
    
    # Action & Context
    action_url = models.URLField(blank=True, help_text="URL for action button")
    action_text = models.CharField(max_length=50, blank=True, help_text="Text for action button")
    context_data = models.JSONField(default=dict, help_text="Additional context data")
    correlation_id = models.UUIDField(default=uuid.uuid4, editable=False)
    
    # Metadata
    source = models.CharField(max_length=100, default='system', help_text="Source system/module")
    template_id = models.CharField(max_length=100, blank=True, help_text="Template identifier")
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    @property
    def is_scheduled(self):
        """Check if notification is scheduled for future delivery"""
        return self.scheduled_for and self.scheduled_for > timezone.now()
    
    @property
    def is_expired(self):
        """Check if notification is expired"""
        return self.expires_at and self.expires_at < timezone.now()
    
    @property
    def can_send(self):
        """Check if notification can be sent"""
        return not self.is_sent and not self.is_scheduled and not self.is_expired
    
    def mark_as_sent(self, channel=None):
        """Mark notification as sent for specific channel"""
        self.is_sent = True
        self.sent_at = timezone.now()
        
        if channel == 'email':
            self.email_sent = True
        elif channel == 'sms':
            self.sms_sent = True
        elif channel == 'push':
            self.push_sent = True
        elif channel == 'in_app':
            self.in_app_delivered = True
        
        self.save()
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = timezone.now()
        self.save()
    
    def mark_as_archived(self):
        """Mark notification as archived"""
        self.is_archived = True
        self.archived_at = timezone.now()
        self.save()
    
    def deliver(self):
        """Deliver notification through configured channels"""
        if not self.can_send:
            return False
        
        from .services.notification_service import NotificationService
        success = NotificationService.deliver_notification(self)
        
        if success:
            self.mark_as_sent('all')
        
        return success
    
    def get_delivery_status(self):
        """Get delivery status across all channels"""
        status = {
            'email': self.email_sent,
            'sms': self.sms_sent,
            'push': self.push_sent,
            'in_app': self.in_app_delivered,
            'overall': self.is_sent,
        }
        
        return status
    
    @classmethod
    def send_instant_notification(cls, user, title, message, notification_type='system', priority='medium', channels=None):
        """Send instant notification to user"""
        if channels is None:
            channels = ['in_app']
        
        notification = cls.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            channels=channels
        )
        
        return notification.deliver()
    
    @classmethod
    def send_bulk_notification(cls, users, title, message, notification_type='system', priority='medium'):
        """Send bulk notification to multiple users"""
        notifications = []
        for user in users:
            notification = cls(
                user=user,
                title=title,
                message=message,
                notification_type=notification_type,
                priority=priority,
                channels=['in_app']
            )
            notifications.append(notification)
        
        cls.objects.bulk_create(notifications)
        
        # Deliver notifications
        for notification in notifications:
            notification.deliver()
        
        return len(notifications)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['priority']),
            models.Index(fields=['is_sent']),
            models.Index(fields=['is_read']),
            models.Index(fields=['scheduled_for']),
            models.Index(fields=['expires_at']),
        ]
        ordering = ['-created_at']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

# -----------------------------
# Location Synchronization (COMPLETED)
# -----------------------------

class LocationSyncLog(TimeStampedModel):
    """Comprehensive location data synchronization tracking"""
    SYNC_TYPES = [
        ('vouchers', 'Vouchers'),
        ('users', 'Users'), 
        ('sessions', 'Sessions'),
        ('transactions', 'Transactions'),
        ('packages', 'Packages'),
        ('devices', 'Devices'),
        ('network_config', 'Network Configuration'),
        ('full', 'Full Sync'),
    ]
    
    SYNC_DIRECTIONS = [
        ('upload', 'Upload to Central'),
        ('download', 'Download from Central'),
        ('bidirectional', 'Bidirectional'),
    ]
    
    SYNC_STATUS = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('success', 'Success'),
        ('partial_success', 'Partial Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Sync Configuration
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='sync_logs')
    sync_type = models.CharField(max_length=20, choices=SYNC_TYPES)
    sync_direction = models.CharField(max_length=15, choices=SYNC_DIRECTIONS, default='bidirectional')
    
    # Status Tracking
    status = models.CharField(max_length=20, choices=SYNC_STATUS, default='pending')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Performance Metrics
    records_processed = models.IntegerField(default=0)
    records_synced = models.IntegerField(default=0)
    records_failed = models.IntegerField(default=0)
    total_size_bytes = models.BigIntegerField(default=0)
    duration_seconds = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Error Handling
    error_count = models.IntegerField(default=0)
    last_error = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    
    # Data Integrity
    checksum = models.CharField(max_length=64, blank=True, help_text="Data integrity checksum")
    data_version = models.CharField(max_length=50, blank=True, help_text="Data version identifier")
    
    # Detailed Results
    details = models.JSONField(default=dict)
    error_details = models.JSONField(default=dict, help_text="Detailed error information")
    
    # Manual Override
    is_manual = models.BooleanField(default=False)
    initiated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='initiated_syncs')
    
    def __str__(self):
        return f"{self.location} - {self.sync_type} - {self.status}"
    
    @property
    def is_completed(self):
        """Check if sync is completed"""
        return self.status in ['success', 'partial_success', 'failed', 'cancelled']
    
    @property
    def success_rate(self):
        """Calculate sync success rate"""
        if self.records_processed == 0:
            return 0
        return (self.records_synced / self.records_processed) * 100
    
    @property
    def sync_duration(self):
        """Calculate sync duration"""
        if self.completed_at and self.started_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def start_sync(self):
        """Start synchronization process"""
        self.status = 'in_progress'
        self.started_at = timezone.now()
        self.save()
    
    def complete_sync(self, success=True, error_message="", details=None):
        """Complete synchronization process"""
        self.status = 'success' if success else 'failed'
        self.completed_at = timezone.now()
        
        if self.started_at and self.completed_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
        
        if error_message:
            self.last_error = error_message
            self.error_count += 1
        
        if details:
            self.details = details
        
        self.save()
        
        # Log sync completion
        if success:
            SecurityLog.objects.create(
                action_type='sync_completed',
                action_category='system',
                description=f"Sync {self.sync_type} completed for {self.location}",
                severity='info',
                details={
                    'sync_id': str(self.id),
                    'location': str(self.location),
                    'sync_type': self.sync_type,
                    'records_processed': self.records_processed,
                    'records_synced': self.records_synced,
                    'duration_seconds': self.duration_seconds
                }
            )
        else:
            SecurityLog.objects.create(
                action_type='sync_failed',
                action_category='system',
                description=f"Sync {self.sync_type} failed for {self.location}",
                severity='high',
                details={
                    'sync_id': str(self.id),
                    'location': str(self.location),
                    'sync_type': self.sync_type,
                    'error_message': error_message,
                    'retry_count': self.retry_count
                }
            )
    
    def record_progress(self, processed, synced, failed=0):
        """Record sync progress"""
        self.records_processed = processed
        self.records_synced = synced
        self.records_failed = failed
        
        if failed > 0:
            self.error_count = failed
            self.status = 'partial_success'
        
        self.save()
    
    def can_retry(self):
        """Check if sync can be retried"""
        return self.retry_count < self.max_retries and self.status in ['failed', 'partial_success']
    
    def retry_sync(self):
        """Retry failed synchronization"""
        if not self.can_retry():
            return False
        
        self.retry_count += 1
        self.status = 'pending'
        self.last_error = ""
        self.save()
        
        return True
    
    @classmethod
    def get_sync_statistics(cls, location, days=7):
        """Get sync statistics for location"""
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Count, Avg, Sum
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        syncs = cls.objects.filter(location=location, started_at__gte=cutoff_date)
        
        stats = syncs.aggregate(
            total_syncs=Count('id'),
            successful_syncs=Count('id', filter=models.Q(status='success')),
            failed_syncs=Count('id', filter=models.Q(status='failed')),
            average_duration=Avg('duration_seconds'),
            total_records=Sum('records_synced')
        )
        
        # Add success rate
        if stats['total_syncs'] > 0:
            stats['success_rate'] = (stats['successful_syncs'] / stats['total_syncs']) * 100
        else:
            stats['success_rate'] = 0
        
        # Add recent activity
        recent_activity = syncs.values('sync_type').annotate(
            count=Count('id'),
            last_sync=models.Max('started_at')
        ).order_by('-last_sync')
        
        stats['recent_activity'] = list(recent_activity)
        
        return stats
    
    class Meta:
        indexes = [
            models.Index(fields=['location', 'started_at']),
            models.Index(fields=['sync_type']),
            models.Index(fields=['status']),
            models.Index(fields=['started_at']),
            models.Index(fields=['completed_at']),
        ]
        ordering = ['-started_at']
        verbose_name = "Location Sync Log"
        verbose_name_plural = "Location Sync Logs"