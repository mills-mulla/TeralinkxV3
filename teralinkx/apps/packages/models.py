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

# --------------------------------------------------------------------
# EXPLICIT THROUGH MODELS (Place these BEFORE the models that use them)
# --------------------------------------------------------------------

class PackageTypeLocation(models.Model):
    """Explicit through model for PackageType locations"""
    packagetype = models.ForeignKey('PackageType', on_delete=models.CASCADE)
    location = models.ForeignKey('locations.Location', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'package_type_locations'
        app_label = 'packages'
        unique_together = [['packagetype', 'location']]

class FeaturedPromotionLocation(models.Model):
    """Explicit through model for FeaturedPromotion locations"""
    promotion = models.ForeignKey('FeaturedPromotion', on_delete=models.CASCADE)
    location = models.ForeignKey('locations.Location', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'featured_promotion_locations'
        app_label = 'packages'
        unique_together = [['promotion', 'location']]

# --------------------------------------------------------------------
# MAIN MODELS
# --------------------------------------------------------------------

class PackageType(TimeStampedModel):
    """All packages available for purchase"""
    
    PACKAGE_CATEGORIES = [
        ('time_based_unlimited', 'Time-Based-Unlimited'),
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
    category = models.CharField(max_length=20, choices=PACKAGE_CATEGORIES, default='time_based_unlimited')
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
    
    # FIXED: Use explicit through model
    locations = models.ManyToManyField(
        'locations.Location',
        through=PackageTypeLocation,  # Explicit through model
        blank=True,
        related_name='available_packages'
    )
    
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
    promotion_start = models.DateTimeField(null=True, blank=True)
    promotion_end = models.DateTimeField(null=True, blank=True)
    
    def get_active_promotions(self, location=None):
        """Get active promotions for this package"""
        # Avoid circular import by importing inside method
        from .models import FeaturedPromotion
        return FeaturedPromotion.get_promotions_for_package(self, active_only=True)
    
    @property
    def has_active_promotion(self):
        """Check if package has any active promotion"""
        return len(self.get_active_promotions()) > 0
        
    @property
    def is_promotion_active(self):
        """Check if promotion is currently active"""
        if not self.is_featured:
            return False
        if self.promotion_start and self.promotion_end:
            now = timezone.now()
            return self.promotion_start <= now <= self.promotion_end
        return True  # Always featured if no time limits

    class Meta:
        db_table = 'packages'
        app_label = 'packages'
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
        app_label = 'packages'
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
        """Set expires_at based on package duration and update status"""
        if not self.expires_at and self.package.duration:
            self.expires_at = self.activated_at + self.package.duration
        
        # Generate unique voucher code if not provided
        if not self.voucher_code:
            self.voucher_code = f"DISP-{uuid.uuid4().hex[:12].upper()}"
        
        # Auto-update status based on expiry and data usage
        self.update_status()
            
        super().save(*args, **kwargs)
    
    def update_status(self):
        """Update voucher status based on current conditions"""
        now = timezone.now()
        
        # Check if expired by time
        if self.expires_at and now > self.expires_at:
            self.status = 'expired'
            return
        
        # Check if data exhausted
        if self.is_data_exhausted:
            self.status = 'exhausted'
            return
        
        # If not expired or exhausted, should be active
        if self.status in ['expired', 'exhausted'] and now <= self.expires_at and not self.is_data_exhausted:
            self.status = 'active'

    @property
    def is_active(self):
        """Check if voucher is currently active"""
        now = timezone.now()
        return (self.status == 'active' and 
                now >= self.activated_at and 
                (not self.expires_at or now <= self.expires_at) and
                not self.is_data_exhausted)
    
    @property
    def computed_status(self):
        """Get computed status based on current conditions"""
        now = timezone.now()
        
        # Check expiry first
        if self.expires_at and now > self.expires_at:
            return 'expired'
        
        # Check data exhaustion
        if self.is_data_exhausted:
            return 'exhausted'
        
        # Check if suspended or cancelled
        if self.status in ['suspended', 'cancelled']:
            return self.status
        
        # Default to active if none of the above
        return 'active'

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
        app_label = 'packages'
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
                voucher_code=f"FBK-{batch_id}-{i+1:06d}",
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


class Coupon(TimeStampedModel):
    """Simple coupon/promo code system with rewards integration"""
    
    COUPON_TYPES = [
        ('percentage', 'Percentage Discount'),
        ('fixed', 'Fixed Amount Discount'),
        ('package', 'Free Package Upgrade'),
    ]
    
    APPLICABLE_TO = [
        ('all', 'All Packages'),
        ('specific', 'Specific Packages'),
        ('category', 'Package Category'),
        ('tier', 'Package Tier'),
    ]
    
    # Core Information
    code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Discount Configuration
    coupon_type = models.CharField(max_length=20, choices=COUPON_TYPES, default='percentage')
    discount_value = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Percentage (e.g., 10.00) or Fixed amount"
    )
    
    # Applicability
    applicable_to = models.CharField(max_length=20, choices=APPLICABLE_TO, default='all')
    applicable_packages = models.ManyToManyField(
        PackageType, 
        blank=True,
        help_text="Specific packages this coupon applies to"
    )
    applicable_category = models.CharField(
        max_length=20, 
        choices=PackageType.PACKAGE_CATEGORIES, 
        blank=True
    )
    applicable_tier = models.CharField(
        max_length=20, 
        choices=PackageType.TIERS, 
        blank=True
    )
    
    # Usage Limits
    max_uses = models.IntegerField(
        default=100,
        help_text="Maximum number of times this coupon can be used"
    )
    max_uses_per_user = models.IntegerField(
        default=1,
        help_text="Maximum uses per user"
    )
    min_purchase_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Minimum purchase amount required"
    )
    
    # Validity Period
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    # Tracking
    total_uses = models.IntegerField(default=0)
    
    # REWARD SYSTEM FIELDS
    is_reward = models.BooleanField(default=False, help_text="Generated from rewards system")
    points_cost = models.IntegerField(null=True, blank=True, help_text="Points required to redeem")
    reward_tier_required = models.CharField(
        max_length=20, 
        choices=[('bronze', 'Bronze'), ('silver', 'Silver'), ('gold', 'Gold'), ('platinum', 'Platinum')],
        blank=True,
        help_text="Minimum tier required to redeem"
    )
    auto_generated = models.BooleanField(default=False, help_text="Auto-generated reward coupon")
    
    class Meta:
        db_table = 'coupons'
        app_label = 'packages'
        indexes = [
            models.Index(fields=['code', 'is_active']),
            models.Index(fields=['valid_until']),
            models.Index(fields=['applicable_to']),
            models.Index(fields=['is_reward', 'points_cost']),
        ]
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def is_valid(self):
        """Check if coupon is currently valid"""
        now = timezone.now()
        return (
            self.is_active and
            self.total_uses < self.max_uses and
            now >= self.valid_from and
            now <= self.valid_until
        )
    
    def can_apply_to_package(self, package):
        """Check if coupon can be applied to specific package"""
        if not self.is_valid:
            return False, "Coupon is not valid"
        
        if self.applicable_to == 'all':
            return True, "Valid for all packages"
        
        elif self.applicable_to == 'specific':
            if package in self.applicable_packages.all():
                return True, "Valid for this package"
            return False, "Coupon not applicable to this package"
        
        elif self.applicable_to == 'category':
            if package.category == self.applicable_category:
                return True, f"Valid for {self.applicable_category} packages"
            return False, f"Coupon only for {self.applicable_category} packages"
        
        elif self.applicable_to == 'tier':
            if package.tier == self.applicable_tier:
                return True, f"Valid for {self.applicable_tier} tier"
            return False, f"Coupon only for {self.applicable_tier} tier"
        
        return False, "Not applicable"
    
    def calculate_discount(self, package_price):
        """Calculate discount amount"""
        if self.coupon_type == 'percentage':
            return (package_price * self.discount_value) / 100
        elif self.coupon_type == 'fixed':
            return min(self.discount_value, package_price)  # Can't discount more than price
        elif self.coupon_type == 'package':
            # For free upgrades, you might need special handling
            return Decimal('0.00')
        return Decimal('0.00')
    
    def increment_use(self):
        """Increment usage count - thread-safe"""
        self.total_uses = models.F('total_uses') + 1
        self.save(update_fields=['total_uses'])


class CouponUsage(TimeStampedModel):
    """Track coupon usage per user"""
    
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coupon_usages')
    package = models.ForeignKey(PackageType, on_delete=models.SET_NULL, null=True)
    voucher = models.ForeignKey(
        DispatchVoucher, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='applied_coupon'
    )
    
    # Transaction Details
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        db_table = 'coupon_usages'
        app_label = 'packages'
        indexes = [
            models.Index(fields=['coupon', 'user']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['voucher']),
        ]
        verbose_name = "Coupon Usage"
        verbose_name_plural = "Coupon Usages"
        constraints = [
            models.UniqueConstraint(
                fields=['coupon', 'voucher'],
                name='unique_coupon_per_voucher',
                condition=models.Q(voucher__isnull=False)
            )
        ]
    
    def __str__(self):
        return f"{self.coupon.code} used by {self.user.username}"

    @classmethod
    def get_user_usage_count(cls, user, coupon):
        """Get how many times user has used this coupon"""
        return cls.objects.filter(user=user, coupon=coupon).count()


class PointTransaction(TimeStampedModel):
    """Track point earning and spending transactions"""
    
    TRANSACTION_TYPES = [
        ('earned_purchase', 'Earned from Purchase'),
        ('earned_referral', 'Referral Bonus'),
        ('earned_streak', 'Streak Bonus'),
        ('earned_achievement', 'Achievement Unlock'),
        ('redeemed_coupon', 'Redeemed for Coupon'),
        ('expired', 'Points Expired'),
    ]
    
    user = models.ForeignKey('users.ClientH', on_delete=models.CASCADE, related_name='point_transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    points = models.IntegerField()  # Positive for earning, negative for spending
    description = models.CharField(max_length=255)
    
    # Related objects
    related_voucher = models.ForeignKey(DispatchVoucher, null=True, blank=True, on_delete=models.SET_NULL)
    related_coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    
    class Meta:
        db_table = 'point_transactions'
        app_label = 'packages'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['user', 'transaction_type']),
        ]
        verbose_name = "Point Transaction"
        verbose_name_plural = "Point Transactions"
    
    def __str__(self):
        return f"{self.user.account} - {self.points} points - {self.transaction_type}"


class FeaturedPromotion(TimeStampedModel):
    """
    Connect featured packages with coupons for marketing promotions.
    This allows you to run promotions like: "Featured Package X with Coupon Y"
    """
    
    PROMOTION_TYPES = [
        ('featured_coupon', 'Featured Package with Coupon'),
        ('bundle', 'Package Bundle'),
        ('seasonal', 'Seasonal Promotion'),
        ('flash_sale', 'Flash Sale'),
        ('new_arrival', 'New Package Launch'),
        ('best_seller', 'Best Seller Highlight'),
    ]
    
    # Core Promotion Information
    name = models.CharField(max_length=255, help_text="Promotion name e.g., 'Summer Special 2024'")
    promotion_type = models.CharField(max_length=20, choices=PROMOTION_TYPES, default='featured_coupon')
    
    # What's being promoted
    package = models.ForeignKey(
        PackageType, 
        on_delete=models.CASCADE,
        help_text="Package being featured in this promotion"
    )
    coupon = models.ForeignKey(
        Coupon, 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        help_text="Optional coupon for this promotion"
    )
    
    # Promotion Content
    headline = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    banner_image = models.ImageField(
        upload_to='promotion_banners/', 
        blank=True,
        help_text="Promotion banner image (1200x400px recommended)"
    )
    button_text = models.CharField(max_length=50, default="Get Offer")
    button_color = models.CharField(max_length=7, default="#FF6B35")
    
    # Display Settings
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # Schedule
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(help_text="When promotion ends")
    
    # FIXED: Use explicit through model
    locations = models.ManyToManyField(
        'locations.Location',
        through=FeaturedPromotionLocation,  # Explicit through model
        blank=True,
        help_text="Specific locations for this promotion (empty = all locations)"
    )
    
    # Performance Tracking
    views = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    conversions = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'featured_promotions'
        app_label = 'packages'
        ordering = ['display_order', '-start_date']
        indexes = [
            models.Index(fields=['is_active', 'start_date', 'end_date']),
            models.Index(fields=['promotion_type', 'is_active']),
            models.Index(fields=['package', 'is_active']),
        ]
        verbose_name = "Featured Promotion"
        verbose_name_plural = "Featured Promotions"
    
    def __str__(self):
        return f"{self.name} - {self.package.name}"
    
    @property
    def is_live(self):
        """Check if promotion is currently active"""
        now = timezone.now()
        
        # Basic checks
        if not self.is_active:
            return False
        
        if now < self.start_date or now > self.end_date:
            return False
        
        # Check package availability
        if not self.package.is_active or not self.package.is_public:
            return False
        
        # Check coupon validity if exists
        if self.coupon and not self.coupon.is_valid:
            return False
        
        return True
    
    @property
    def time_remaining(self):
        """Get time remaining for promotion"""
        now = timezone.now()
        if now > self.end_date:
            return timedelta(0)
        return self.end_date - now
    
    @property
    def is_ending_soon(self):
        """Check if promotion ends in less than 24 hours"""
        return self.time_remaining < timedelta(hours=24)
    
    @property
    def discount_message(self):
        """Generate discount message based on coupon"""
        if not self.coupon:
            return None
        
        if self.coupon.coupon_type == 'percentage':
            return f"Save {self.coupon.discount_value}%"
        elif self.coupon.coupon_type == 'fixed':
            return f"Save KSh {self.coupon.discount_value}"
        elif self.coupon.coupon_type == 'package':
            return "Free Upgrade Available"
        return None
    
    @property
    def final_price(self):
        """Calculate final price with coupon discount"""
        if self.coupon:
            discount = self.coupon.calculate_discount(self.package.price)
            return self.package.price - discount
        return self.package.price
    
    def increment_views(self):
        """Increment view count - for tracking impressions"""
        self.views = models.F('views') + 1
        self.save(update_fields=['views'])
    
    def increment_clicks(self):
        """Increment click count - when users click the promotion"""
        self.clicks = models.F('clicks') + 1
        self.save(update_fields=['clicks'])
    
    def increment_conversions(self):
        """Increment conversion count - when purchase is made"""
        self.conversions = models.F('conversions') + 1
        self.save(update_fields=['conversions'])
    
    @property
    def click_through_rate(self):
        """Calculate click-through rate"""
        if self.views == 0:
            return 0
        return (self.clicks / self.views) * 100
    
    @property
    def conversion_rate(self):
        """Calculate conversion rate"""
        if self.clicks == 0:
            return 0
        return (self.conversions / self.clicks) * 100
    
    def get_promotion_data(self, for_user=None):
        """
        Get complete promotion data for display
        Includes package details and coupon information
        """
        data = {
            'promotion_id': self.id,
            'name': self.name,
            'headline': self.headline,
            'description': self.description,
            'promotion_type': self.promotion_type,
            'is_live': self.is_live,
            'time_remaining_hours': int(self.time_remaining.total_seconds() / 3600),
            'is_ending_soon': self.is_ending_soon,
            
            # Package details
            'package': {
                'id': self.package.id,
                'name': self.package.name,
                'code': self.package.code,
                'original_price': float(self.package.price),
                'description': self.package.description,
                'duration_days': self.package.duration.days,
                'speed_mbps': self.package.speed_limit_mbps,
                'data_limit_mb': self.package.data_limit_mb,
                'is_unlimited': self.package.is_unlimited,
            },
            
            # Display settings
            'button_text': self.button_text,
            'button_color': self.button_color,
            'has_banner': bool(self.banner_image),
        }
        
        # Add coupon details if exists
        if self.coupon:
            data['coupon'] = {
                'code': self.coupon.code,
                'coupon_type': self.coupon.coupon_type,
                'discount_value': float(self.coupon.discount_value),
                'discount_message': self.discount_message,
            }
            data['final_price'] = float(self.final_price)
            data['savings'] = float(self.package.price - self.final_price)
        
        # Check if user can use the coupon
        if for_user and self.coupon:
            can_apply, message = self.coupon.can_apply_to_package(self.package)
            user_uses = CouponUsage.get_user_usage_count(for_user, self.coupon)
            data['user_can_use'] = (
                can_apply and 
                user_uses < self.coupon.max_uses_per_user and
                self.coupon.is_valid
            )
            data['user_uses'] = user_uses
        
        return data
    
    @classmethod
    def get_active_promotions(cls, location=None, user=None, limit=10):
        """
        Get active promotions for display
        Filters by location and checks validity
        """
        queryset = cls.objects.filter(is_active=True)
        
        # Filter by location if specified
        if location:
            queryset = queryset.filter(
                models.Q(locations__isnull=True) | 
                models.Q(locations=location)
            )
        
        # Get promotions that are currently live
        now = timezone.now()
        promotions = []
        for promotion in queryset.order_by('display_order', '-start_date'):
            if promotion.is_live:
                promotions.append(promotion.get_promotion_data(for_user=user))
            
            if len(promotions) >= limit:
                break
        
        return promotions
    
    @classmethod
    def get_promotions_for_package(cls, package, active_only=True):
        """Get all promotions for a specific package"""
        queryset = cls.objects.filter(package=package)
        
        if active_only:
            now = timezone.now()
            # Filter in Python to use the is_live property
            return [p for p in queryset if p.is_live]
        
        return list(queryset)