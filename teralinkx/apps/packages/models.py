# apps/packages/models.py
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
import uuid
from datetime import timedelta

from apps.core.models import TimeStampedModel, StatusTrackedModel

class PackageType(TimeStampedModel, StatusTrackedModel):
    """Unified package system with advanced features and personalization for ISP"""
    PACKAGE_CATEGORIES = [
        ('time_based', 'Time-Based Access'),
        ('data_based', 'Data-Based Access'),
        ('unlimited', 'Unlimited Access'),
        ('hybrid', 'Hybrid (Time + Data)'),
        ('corporate', 'Corporate/Business'),
        ('special', 'Special Offer'),
        ('trial', 'Trial Package'),
        ('voucher', 'Voucher Package'),
    ]
    
    PACKAGE_TIERS = [
        ('individual', 'Individual (1 Device)'),
        ('duo', 'Duo (2 Devices)'),
        ('family', 'Family (3 Devices)'),
        ('business', 'Business (5+ Devices)'),
        ('enterprise', 'Enterprise (10+ Devices)'),
    ]
    
    USAGE_TYPES = [
        ('any', 'Any Usage'),
        ('social', 'Social Media Only'),
        ('streaming', 'Streaming Optimized'),
        ('gaming', 'Gaming Optimized'),
        ('work', 'Work/Productivity'),
        ('browsing', 'Web Browsing'),
    ]
    
    # Core Identity
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=50, unique=True, help_text="Internal package code for billing")
    description = models.CharField(max_length=255)
    short_description = models.CharField(max_length=100, blank=True, help_text="Brief description for display")
    
    # ISP Package Classification
    package_category = models.CharField(max_length=20, choices=PACKAGE_CATEGORIES, default='time_based')
    package_tier = models.CharField(max_length=20, choices=PACKAGE_TIERS, default='individual')
    usage_type = models.CharField(max_length=20, choices=USAGE_TYPES, default='any')
    
    # Pricing & Duration
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='KES')
    duration = models.DurationField(null=True, blank=True)
    
    # ISP-Specific Technical Limits
    device_limit = models.IntegerField(default=1)
    speed_limit_mbps = models.IntegerField(null=True, blank=True, help_text="Maximum speed in Mbps")
    guaranteed_speed_mbps = models.IntegerField(null=True, blank=True, help_text="Minimum guaranteed speed")
    burst_speed_mbps = models.IntegerField(null=True, blank=True, help_text="Temporary burst speed")
    
    # Data Limits (for data-based packages)
    usage_limit_mb = models.BigIntegerField(null=True, blank=True, help_text="Data limit in MB")
    fair_usage_limit_mb = models.BigIntegerField(null=True, blank=True, help_text="Fair usage policy limit")
    throttle_speed_mbps = models.IntegerField(default=1, help_text="Speed after FUP limit")
    
    # Network Quality of Service
    qos_priority = models.CharField(max_length=20, choices=[
        ('standard', 'Standard Priority'),
        ('premium', 'Premium Priority'),
        ('business', 'Business Critical'),
        ('real_time', 'Real-time (VoIP/Gaming)'),
    ], default='standard')
    
    # Network Restrictions
    protocol_restrictions = models.JSONField(
        default=list,
        help_text="Allowed protocols: ['http', 'https', 'ftp', 'ssh', 'rtmp', 'rtsp']"
    )
    port_restrictions = models.JSONField(
        default=dict,
        help_text="Port restrictions: {'blocked_ports': [], 'open_ports': []}"
    )
    website_restrictions = models.JSONField(
        default=dict,
        help_text="Website access: {'allowed': [], 'blocked': []}"
    )
    
    # Billing & Validity
    billing_cycle = models.CharField(max_length=20, choices=[
        ('minutes', 'Minutes'),
        ('hours', 'Hours'),
        ('days', 'Days'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ], default='hours')
    auto_renew = models.BooleanField(default=False, help_text="Auto-renew package when expired")
    grace_period = models.DurationField(default=timedelta(minutes=5), help_text="Grace period after expiry")
    rollover_data = models.BooleanField(default=False, help_text="Allow unused data to roll over")
    
    # Categorization & Display
    tags = models.JSONField(default=list, help_text="Tags for filtering: ['hotspot', 'wifi', '4g', '5g', 'fiber']")
    color_code = models.CharField(max_length=7, default='#007bff', help_text="Display color in hex")
    display_order = models.IntegerField(default=0, help_text="Order in package listing")
    is_featured = models.BooleanField(default=False, help_text="Featured package on homepage")
    
    # Availability & Targeting
    locations = models.ManyToManyField('locations.Location', blank=True)
    network_nodes = models.ManyToManyField('network.NetworkNode', blank=True, help_text="Specific network nodes")
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    available_from = models.DateTimeField(null=True, blank=True)
    available_until = models.DateTimeField(null=True, blank=True)
    
    # Limited Offers & Inventory
    total_quantity = models.IntegerField(null=True, blank=True, help_text="Total available units")
    sold_quantity = models.IntegerField(default=0)
    reserved_quantity = models.IntegerField(default=0, help_text="Temporarily reserved units")
    
    # Promotional Display
    banner = models.CharField(max_length=20, choices=[
        ('NEW', 'New'),
        ('HOT', 'HOT'),
        ('SALE', 'Sale'),
        ('POPULAR', 'Popular'),
        ('RECOMMENDED', 'Recommended'),
        ('BEST_VALUE', 'Best Value'),
        ('LIMITED', 'Limited Time'),
        ('NONE', 'None'),
    ], default='NONE')
    promotion_text = models.CharField(max_length=100, blank=True, help_text="Promotional text overlay")
    
    # Commission & Partner Settings
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Commission percentage for partners")
    is_partner_exclusive = models.BooleanField(default=False)
    reseller_margin = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Margin for resellers")
    
    # ISP Technical Configuration
    radius_group = models.CharField(max_length=100, blank=True, help_text="RADIUS group for authentication")
    coa_support = models.BooleanField(default=True, help_text="Support Change of Authorization")
    session_timeout = models.IntegerField(default=3600, help_text="Session timeout in seconds")
    idle_timeout = models.IntegerField(default=300, help_text="Idle timeout in seconds")
    
    # Personalization Fields
    personalization_rules = models.JSONField(
        default=dict,
        help_text="Rules for dynamic personalization"
    )
    target_audience = models.JSONField(
        default=list,
        help_text="Target user segments"
    )
    target_conditions = models.JSONField(
        default=dict,
        help_text="Conditions for showing this package"
    )
    dynamic_pricing_rules = models.JSONField(
        default=dict,
        help_text="Dynamic pricing rules"
    )
    personalization_priority = models.IntegerField(
        default=0,
        help_text="Priority for personalization engine"
    )
    is_personalizable = models.BooleanField(
        default=False,
        help_text="Whether this package can be personalized"
    )
    max_personalization_discount = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        help_text="Maximum discount percentage for personalization"
    )
    personalization_triggers = models.JSONField(
        default=list,
        help_text="Triggers for personalization"
    )

    def __str__(self):
        return f"{self.name} ({self.code}) - {self.get_package_tier_display()}"
    
    def clean(self):
        """Validate ISP package data"""
        if self.original_price and self.original_price < self.price:
            raise ValidationError("Original price cannot be less than current price")
        
        if self.available_from and self.available_until and self.available_from >= self.available_until:
            raise ValidationError("Available from date must be before available until date")
        
        # Validate technical limits
        if self.speed_limit_mbps and self.guaranteed_speed_mbps:
            if self.guaranteed_speed_mbps > self.speed_limit_mbps:
                raise ValidationError("Guaranteed speed cannot exceed speed limit")
        
        if self.usage_limit_mb and self.fair_usage_limit_mb:
            if self.fair_usage_limit_mb > self.usage_limit_mb:
                raise ValidationError("Fair usage limit cannot exceed data limit")
    
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
        if self.total_quantity and (self.sold_quantity + self.reserved_quantity) >= self.total_quantity:
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
    
    @property
    def available_quantity(self):
        """Get available quantity for limited packages"""
        if self.total_quantity:
            return max(0, self.total_quantity - (self.sold_quantity + self.reserved_quantity))
        return None
    
    @property
    def is_unlimited_data(self):
        """Check if package has unlimited data"""
        return self.usage_limit_mb is None or self.usage_limit_mb == 0
    
    @property
    def is_time_based(self):
        """Check if package is time-based"""
        return self.package_category == 'time_based'
    
    @property
    def is_data_based(self):
        """Check if package is data-based"""
        return self.package_category == 'data_based'
    
    def get_technical_summary(self):
        """Get technical summary for network configuration"""
        return {
            'speed_limit': self.speed_limit_mbps,
            'data_limit': self.usage_limit_mb,
            'duration': self.duration.total_seconds() if self.duration else None,
            'device_limit': self.device_limit,
            'qos_priority': self.qos_priority,
            'radius_group': self.radius_group,
        }
    
    def get_radius_attributes(self):
        """Generate RADIUS attributes for this package"""
        attributes = {}
        
        if self.speed_limit_mbps:
            attributes['Mikrotik-Rate-Limit'] = f"{self.speed_limit_mbps}M/{self.speed_limit_mbps}M"
        
        if self.duration:
            attributes['Session-Timeout'] = int(self.duration.total_seconds())
        
        if self.idle_timeout:
            attributes['Idle-Timeout'] = self.idle_timeout
        
        # Add QoS attributes based on priority
        if self.qos_priority == 'premium':
            attributes['QoS-Priority'] = 'high'
        elif self.qos_priority == 'business':
            attributes['QoS-Priority'] = 'critical'
        elif self.qos_priority == 'real_time':
            attributes['QoS-Priority'] = 'real-time'
        
        return attributes
    
    def increment_sold_quantity(self):
        """Increment sold quantity"""
        if self.total_quantity:
            self.sold_quantity += 1
            self.save()
    
    def reserve_quantity(self, count=1):
        """Reserve package quantity"""
        if self.total_quantity:
            available = self.total_quantity - (self.sold_quantity + self.reserved_quantity)
            if count <= available:
                self.reserved_quantity += count
                self.save()
                return True
        return False
    
    def release_reserved_quantity(self, count=1):
        """Release reserved quantity"""
        if self.reserved_quantity >= count:
            self.reserved_quantity -= count
            self.save()
            return True
        return False
    
    def get_personalized_price(self, user=None, context=None):
        """Calculate personalized price based on user and context"""
        base_price = self.price
        
        if not self.is_personalizable or not user:
            return base_price
        
        # Apply dynamic pricing rules
        discount = Decimal('0')
        
        # User tier discounts
        if hasattr(user, 'client_profile'):
            user_tier = getattr(user.client_profile, 'account_tier', 'standard')
            tier_discounts = self.dynamic_pricing_rules.get('tier_discounts', {})
            discount = max(discount, tier_discounts.get(user_tier, Decimal('0')))
        
        # Time-based discounts
        time_discounts = self.dynamic_pricing_rules.get('time_based_discounts', {})
        current_hour = timezone.now().hour
        for time_range, time_discount in time_discounts.items():
            start_hour, end_hour = map(int, time_range.split('-'))
            if start_hour <= current_hour <= end_hour:
                discount = max(discount, Decimal(str(time_discount)))
        
        # Apply maximum discount limit
        max_discount = self.max_personalization_discount
        if max_discount > 0:
            discount = min(discount, max_discount)
        
        personalized_price = base_price * (1 - discount / 100)
        return max(personalized_price, Decimal('0'))
    
    def should_show_to_user(self, user, user_context=None):
        """Determine if package should be shown to specific user"""
        if not self.is_available:
            return False
        
        if not self.is_personalizable:
            return True
        
        # Check target audience
        if self.target_audience and user:
            if not self._matches_target_audience(user, user_context):
                return False
        
        # Check conditions
        if self.target_conditions and user:
            if not self._matches_conditions(user, user_context):
                return False
        
        return True
    
    def _matches_target_audience(self, user, user_context):
        """Check if user matches target audience"""
        if not self.target_audience:
            return True
            
        if hasattr(user, 'client_profile'):
            profile = user.client_profile
            
            for audience in self.target_audience:
                if audience == 'new_users' and profile.total_spent == 0:
                    return True
                elif audience == 'returning' and profile.total_spent > 0:
                    return True
                elif audience == 'high_usage' and profile.lifetime_data_used > 5368709120:  # 5GB
                    return True
                elif audience == 'premium' and profile.account_tier == 'premium':
                    return True
                elif audience == 'business' and profile.account_tier == 'business':
                    return True
                elif audience == 'roaming' and profile.is_roaming:
                    return True
        
        return False
    
    def _matches_conditions(self, user, user_context):
        """Check if user matches target conditions"""
        if not self.target_conditions:
            return True
            
        if hasattr(user, 'client_profile'):
            profile = user.client_profile
            
            min_balance = self.target_conditions.get('min_balance', 0)
            if profile.balance < min_balance:
                return False
            
            max_usage = self.target_conditions.get('max_usage')
            if max_usage and profile.lifetime_data_used > max_usage:
                return False
            
            required_tier = self.target_conditions.get('required_tier')
            if required_tier and profile.account_tier != required_tier:
                return False
        
        return True
    
    def get_personalization_score(self, user, user_context=None):
        """Calculate personalization score for ranking"""
        score = 0
        
        if not user or not self.is_personalizable:
            return score
        
        # Base priority
        score += self.personalization_priority
        
        # User preference matching
        try:
            preference = UserPackagePreference.objects.get(
                user=user, 
                package_type=self
            )
            score += preference.preference_score * 10
            if preference.frequently_purchased:
                score += 20
            if preference.rating:
                score += preference.rating * 2
        except UserPackagePreference.DoesNotExist:
            pass
        
        # Audience matching bonus
        if self._matches_target_audience(user, user_context):
            score += 15
        
        # Condition matching bonus
        if self._matches_conditions(user, user_context):
            score += 10
        
        return score
    
    class Meta:
        indexes = [
            models.Index(fields=['package_category']),
            models.Index(fields=['package_tier']),
            models.Index(fields=['usage_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['status']),
            models.Index(fields=['price']),
            models.Index(fields=['available_from', 'available_until']),
            models.Index(fields=['code']),
            models.Index(fields=['is_personalizable']),
            models.Index(fields=['personalization_priority']),
            models.Index(fields=['banner']),
            models.Index(fields=['display_order']),
            models.Index(fields=['is_featured']),
        ]
        ordering = ['display_order', '-is_featured', 'name']
        verbose_name = "Package"
        verbose_name_plural = "Packages"


class UserPackagePreference(TimeStampedModel):
    """Track user preferences and package interactions for personalization"""
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='package_preferences')
    package_type = models.ForeignKey(PackageType, on_delete=models.CASCADE, related_name='user_preferences')
    
    # Interaction metrics
    view_count = models.IntegerField(default=0)
    purchase_count = models.IntegerField(default=0)
    last_viewed = models.DateTimeField(null=True, blank=True)
    last_purchased = models.DateTimeField(null=True, blank=True)
    
    # Preference scores (0.0 to 1.0)
    preference_score = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    implicit_score = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    explicit_score = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    
    # User ratings
    rating = models.IntegerField(null=True, blank=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])
    review = models.TextField(blank=True)
    
    # Behavioral data
    frequently_purchased = models.BooleanField(default=False)
    abandoned_cart = models.BooleanField(default=False)
    wishlisted = models.BooleanField(default=False)
    
    # Usage patterns
    avg_session_duration = models.DurationField(null=True, blank=True)
    typical_usage_time = models.CharField(max_length=20, blank=True, choices=[
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
        ('night', 'Night'),
        ('anytime', 'Anytime'),
    ])
    
    # Contextual data
    preferred_locations = models.ManyToManyField('locations.Location', blank=True)
    typically_roaming = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user', 'package_type']
        indexes = [
            models.Index(fields=['user', 'preference_score']),
            models.Index(fields=['package_type', 'preference_score']),
            models.Index(fields=['frequently_purchased']),
            models.Index(fields=['wishlisted']),
            models.Index(fields=['last_purchased']),
        ]
        verbose_name = "User Package Preference"
        verbose_name_plural = "User Package Preferences"
    
    def __str__(self):
        return f"{self.user.username} - {self.package_type.name} ({self.preference_score})"
    
    def update_preference_score(self):
        """Calculate comprehensive preference score"""
        total_score = Decimal('0')
        weight_count = 0
        
        # Explicit rating (30% weight)
        if self.rating:
            total_score += Decimal(self.rating) / 5 * 30
            weight_count += 30
        
        # Purchase frequency (25% weight)
        if self.purchase_count > 0:
            purchase_score = min(self.purchase_count / 10, 1)  # Cap at 10 purchases
            total_score += purchase_score * 25
            weight_count += 25
        
        # View frequency (15% weight)
        if self.view_count > 0:
            view_score = min(self.view_count / 20, 1)  # Cap at 20 views
            total_score += view_score * 15
            weight_count += 15
        
        # Recency (20% weight)
        if self.last_purchased:
            days_since = (timezone.now() - self.last_purchased).days
            recency_score = max(0, 1 - (days_since / 30))  # Decay over 30 days
            total_score += recency_score * 20
            weight_count += 20
        
        # Behavioral flags (10% weight)
        behavior_score = 0
        if self.frequently_purchased:
            behavior_score += 0.5
        if self.wishlisted:
            behavior_score += 0.3
        if not self.abandoned_cart:
            behavior_score += 0.2
        total_score += behavior_score * 10
        weight_count += 10
        
        # Normalize score
        if weight_count > 0:
            self.preference_score = total_score / weight_count
        else:
            self.preference_score = Decimal('0')
        
        self.save()
    
    def record_view(self):
        """Record package view and update scores"""
        self.view_count += 1
        self.last_viewed = timezone.now()
        self.update_preference_score()
    
    def record_purchase(self):
        """Record package purchase and update scores"""
        self.purchase_count += 1
        self.last_purchased = timezone.now()
        self.abandoned_cart = False
        
        # Mark as frequently purchased if threshold met
        if self.purchase_count >= 3:
            self.frequently_purchased = True
        
        self.update_preference_score()
    
    def record_abandoned_cart(self):
        """Record cart abandonment"""
        self.abandoned_cart = True
        self.update_preference_score()


class PersonalizedPackageOffer(TimeStampedModel):
    """Generated personalized package offers for users"""
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='personalized_offers')
    package_type = models.ForeignKey(PackageType, on_delete=models.CASCADE, related_name='personalized_offers')
    
    # Offer details
    original_package = models.ForeignKey(PackageType, on_delete=models.CASCADE, related_name='derived_offers', null=True, blank=True)
    personalized_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Personalization context
    personalization_context = models.JSONField(default=dict, help_text="Context data used for personalization")
    personalization_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    personalization_factors = models.JSONField(default=list, help_text="Factors that influenced personalization")
    
    # Offer validity
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    # Tracking
    times_shown = models.IntegerField(default=0)
    times_clicked = models.IntegerField(default=0)
    times_purchased = models.IntegerField(default=0)
    last_shown = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'package_type', 'valid_until']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['valid_until']),
            models.Index(fields=['personalization_score']),
            models.Index(fields=['created_at']),
        ]
        verbose_name = "Personalized Package Offer"
        verbose_name_plural = "Personalized Package Offers"
    
    def __str__(self):
        return f"{self.user.username} - {self.package_type.name} - {self.discount_percentage}% off"
    
    @property
    def is_valid(self):
        """Check if offer is still valid"""
        now = timezone.now()
        return self.is_active and self.valid_from <= now <= self.valid_until
    
    def record_impression(self):
        """Record offer impression"""
        self.times_shown += 1
        self.last_shown = timezone.now()
        self.save()
    
    def record_click(self):
        """Record offer click"""
        self.times_clicked += 1
        self.save()
    
    def record_purchase(self):
        """Record offer purchase"""
        self.times_purchased += 1
        self.is_active = False  # Deactivate after purchase
        self.save()


class VoucherBase(TimeStampedModel):
    """Base model for all voucher types"""
    VOUCHER_TYPES = [
        ('pre_generated', 'Pre-generated'),
        ('dynamic', 'Dynamically Generated'),
        ('bulk', 'Bulk Voucher'),
        ('promotional', 'Promotional'),
        ('personalized', 'Personalized'),
    ]
    
    voucher_code = models.CharField(max_length=255, unique=True)
    voucher_type = models.CharField(max_length=20, choices=VOUCHER_TYPES, default='pre_generated')
    package_type = models.ForeignKey(PackageType, on_delete=models.CASCADE)
    location = models.ForeignKey('locations.Location', on_delete=models.CASCADE)
    is_roaming = models.BooleanField(default=False)
    
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
    generated_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Personalization for vouchers
    target_user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    personalization_data = models.JSONField(default=dict, help_text="Data used for voucher personalization")
    
    def __str__(self):
        return f"{self.voucher_code} - {self.package_type.name}"
    
    def mark_as_used(self):
        """Mark voucher as used"""
        self.is_used = True
        self.used_at = timezone.now()
        self.save()
    
    @property
    def is_personalized(self):
        """Check if voucher is personalized for specific user"""
        return self.target_user is not None
    
    class Meta:
        indexes = [
            models.Index(fields=['voucher_code']),
            models.Index(fields=['is_used']),
            models.Index(fields=['package_type']),
            models.Index(fields=['location']),
            models.Index(fields=['batch_id']),
            models.Index(fields=['target_user']),
        ]
        verbose_name = "Available Voucher"
        verbose_name_plural = "Available Vouchers"


class DispatchVoucher(TimeStampedModel):
    """Enhanced activated vouchers with comprehensive tracking"""
    dispatch_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dispatch_account = models.CharField(max_length=15)
    voucher_code = models.CharField(max_length=255)
    package_type = models.ForeignKey(PackageType, on_delete=models.CASCADE)
    location = models.ForeignKey('locations.Location', on_delete=models.CASCADE)
    is_roaming = models.BooleanField(default=False)
    
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
    payment_gateway = models.ForeignKey('finance.PaymentGateway', on_delete=models.SET_NULL, null=True, blank=True)
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
    home_location = models.ForeignKey('locations.Location', on_delete=models.CASCADE, related_name='home_vouchers')
    roaming_policy_applied = models.ForeignKey('locations.RoamingPolicy', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Personalization tracking
    was_personalized = models.BooleanField(default=False)
    personalization_offer = models.ForeignKey(
        PersonalizedPackageOffer, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    # ISP Network Integration
    radius_attributes = models.JSONField(default=dict, help_text="RADIUS attributes for this voucher")
    coa_support = models.BooleanField(default=True, help_text="Support Change of Authorization")
    session_timeout = models.IntegerField(default=3600, help_text="Session timeout in seconds")
    idle_timeout = models.IntegerField(default=300, help_text="Idle timeout in seconds")
    
    # Real-time Monitoring
    concurrent_sessions = models.IntegerField(default=0)
    last_session_update = models.DateTimeField(null=True, blank=True)
    current_speed_mbps = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
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
            models.Index(fields=['was_personalized']),
            models.Index(fields=['concurrent_sessions']),
        ]
        verbose_name = "Dispatch Voucher"
        verbose_name_plural = "Dispatch Vouchers"