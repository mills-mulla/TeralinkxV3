# apps/ads/models.py
from django.db import models
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import uuid

from locations.models import Location
from core.models import TimeStampedModel

class Advertisement(TimeStampedModel):
    """Enterprise-grade advertisement system with advanced location targeting"""
    
    AD_TYPES = [
        ('banner', 'Banner Ad'),
        ('interstitial', 'Full Screen Ad'),
        ('popup', 'Popup Ad'),
        ('notification', 'Notification Ad'),
        ('video', 'Video Ad'),
        ('native', 'Native Content Ad'),
        ('carousel', 'Image Carousel Ad'),
    ]
    
    AD_STATUS = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('expired', 'Expired'),
        ('archived', 'Archived'),
        ('scheduled', 'Scheduled'),
    ]
    
    TARGET_AUDIENCE = [
        ('all', 'All Users'),
        ('new', 'New Users (First Time)'),
        ('returning', 'Returning Users'),
        ('premium', 'Premium Tier Users'),
        ('business', 'Business Tier Users'),
        ('enterprise', 'Enterprise Tier Users'),
        ('high_usage', 'High Data Usage Users'),
        ('low_usage', 'Low Data Usage Users'),
        ('roaming', 'Roaming Users'),
    ]
    
    DEVICE_TARGETING = [
        ('all', 'All Devices'),
        ('mobile', 'Mobile Only'),
        ('desktop', 'Desktop Only'),
        ('tablet', 'Tablet Only'),
        ('ios', 'iOS Devices'),
        ('android', 'Android Devices'),
    ]

    # Core Advertisement Information
    title = models.CharField(max_length=200, help_text="Primary headline for the advertisement")
    caption = models.TextField(max_length=500, help_text="Supporting text or description")
    ad_type = models.CharField(max_length=20, choices=AD_TYPES, default='banner')
    status = models.CharField(max_length=20, choices=AD_STATUS, default='draft')
    campaign_name = models.CharField(max_length=100, blank=True, help_text="Campaign identifier")
    
    # Location Reference (replacing multiple inheritance)
    location = models.ForeignKey(
        'locations.Location',
        on_delete=models.CASCADE,
        related_name='advertisements',
        help_text="Primary location for this advertisement"
    )
    is_roaming = models.BooleanField(default=False, help_text="Whether this ad is for roaming users")
    roaming_partner = models.CharField(max_length=100, blank=True, help_text="Roaming partner name")
    signal_strength = models.DecimalField(max_digits=3, decimal_places=1, default=0, help_text="Signal strength at location")
    
    # Media Assets
    image = models.ImageField(
        upload_to='ads/images/%Y/%m/%d/', 
        blank=True, 
        null=True,
        help_text="Primary image for banner, popup, or native ads"
    )
    video = models.FileField(
        upload_to='ads/videos/%Y/%m/%d/', 
        blank=True, 
        null=True,
        help_text="Video file for video ads (MP4, WebM, max 50MB)"
    )
    thumbnail = models.ImageField(
        upload_to='ads/thumbnails/%Y/%m/%d/', 
        blank=True, 
        null=True,
        help_text="Thumbnail for video ads or secondary image"
    )
    carousel_images = models.JSONField(
        default=list,
        help_text="List of image URLs for carousel ads"
    )
    
    # Content & Engagement
    content = models.TextField(
        blank=True, 
        help_text="Detailed content (supports HTML for rich content ads)"
    )
    cta_text = models.CharField(
        max_length=50, 
        default="Learn More",
        help_text="Call-to-Action button text"
    )
    cta_url = models.URLField(
        blank=True, 
        help_text="Destination URL when ad is clicked"
    )
    cta_color = models.CharField(
        max_length=7, 
        default='#007bff',
        help_text="CTA button color in hex format"
    )
    brand_name = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Brand or company name"
    )
    logo = models.ImageField(
        upload_to='ads/logos/%Y/%m/%d/', 
        blank=True, 
        null=True,
        help_text="Brand logo image"
    )

    # Scheduling & Priority
    start_date = models.DateTimeField(
        default=timezone.now,
        help_text="Date and time when the ad should start being displayed"
    )
    end_date = models.DateTimeField(
        help_text="Date and time when the ad should stop being displayed"
    )
    priority = models.IntegerField(
        default=1,
        choices=[(1, 'Low'), (2, 'Medium'), (3, 'High'), (4, 'Urgent')],
        help_text="Display priority relative to other ads"
    )
    weight = models.IntegerField(
        default=100,
        help_text="Relative weight for ad rotation (higher = more frequent)"
    )

    # Budget & Pricing Model
    budget = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        help_text="Total campaign budget in KES"
    )
    bidding_strategy = models.CharField(
        max_length=20,
        choices=[
            ('cpc', 'Cost Per Click'),
            ('cpm', 'Cost Per 1000 Impressions'),
            ('cpa', 'Cost Per Action'),
            ('fixed', 'Fixed Cost')
        ],
        default='cpc'
    )
    cost_per_click = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        default=0.50,
        help_text="Cost per click in KES"
    )
    cost_per_impression = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        default=0.02,
        help_text="Cost per 1000 impressions in KES"
    )
    cost_per_action = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        default=5.00,
        help_text="Cost per conversion/action in KES"
    )
    daily_budget = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Maximum daily spend in KES"
    )
    total_spent = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0
    )

    # Performance Metrics
    impressions = models.BigIntegerField(default=0)
    clicks = models.BigIntegerField(default=0)
    conversions = models.BigIntegerField(default=0)
    unique_users_reached = models.BigIntegerField(default=0)
    last_shown = models.DateTimeField(null=True, blank=True)
    avg_display_time = models.DurationField(default=timedelta(0))

    # Advanced Targeting
    target_audience = models.CharField(
        max_length=20, 
        choices=TARGET_AUDIENCE, 
        default='all'
    )
    target_devices = models.CharField(
        max_length=20,
        choices=DEVICE_TARGETING,
        default='all'
    )
    target_packages = models.ManyToManyField(
        'packages.PackageType', 
        blank=True,
        help_text="Show ad to users with specific package types"
    )
    target_locations = models.ManyToManyField(
        'locations.Location', 
        blank=True,
        related_name='targeted_ads',
        help_text="Specific locations where this ad should be shown"
    )
    exclude_locations = models.ManyToManyField(
        'locations.Location', 
        blank=True,
        related_name='excluded_ads',
        help_text="Locations where this ad should never be shown"
    )
    min_user_balance = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Minimum user balance to show ad"
    )
    require_premium = models.BooleanField(
        default=False,
        help_text="Only show to premium tier users"
    )

    # Frequency Capping & Rotation
    max_impressions_per_user = models.IntegerField(
        default=5,
        help_text="Maximum times to show this ad to the same user"
    )
    impression_interval = models.DurationField(
        default=timedelta(hours=24),
        help_text="Time window for frequency capping"
    )
    min_time_between_views = models.DurationField(
        default=timedelta(minutes=30),
        help_text="Minimum time between showing same ad to same user"
    )

    # Analytics & Optimization
    click_through_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0
    )
    conversion_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0
    )
    performance_score = models.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        default=0
    )
    quality_score = models.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        default=5.0,
        help_text="Ad quality rating (1-10)"
    )

    # Technical Metadata
    campaign_id = models.UUIDField(
        default=uuid.uuid4, 
        editable=False, 
        unique=True
    )
    created_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.CASCADE,
        related_name='created_advertisements'
    )
    tags = models.JSONField(
        default=list,
        help_text="Tags for categorization and filtering"
    )
    custom_parameters = models.JSONField(
        default=dict,
        help_text="Custom parameters for ad serving"
    )
    notes = models.TextField(
        blank=True,
        help_text="Internal notes and comments"
    )

    class Meta:
        db_table = 'advertisements'
        verbose_name = 'Advertisement'
        verbose_name_plural = 'Advertisements'
        indexes = [
            models.Index(fields=['status', 'start_date', 'end_date']),
            models.Index(fields=['ad_type', 'priority']),
            models.Index(fields=['location', 'is_roaming']),
            models.Index(fields=['campaign_id']),
            models.Index(fields=['created_at']),
            models.Index(fields=['performance_score']),
            models.Index(fields=['target_audience']),
        ]
        ordering = ['-priority', '-performance_score', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.get_ad_type_display()} - {self.campaign_id}"

    @property
    def is_active(self):
        """Check if ad is currently active and should be shown"""
        now = timezone.now()
        is_within_date_range = self.start_date <= now <= self.end_date
        has_budget = self.budget == 0 or self.total_spent < self.budget
        has_daily_budget = self.daily_budget == 0 or self.get_today_spend() < self.daily_budget
        
        return (self.status == 'active' and 
                is_within_date_range and 
                has_budget and 
                has_daily_budget)

    @property
    def remaining_budget(self):
        """Calculate remaining campaign budget"""
        return max(Decimal('0'), self.budget - self.total_spent)

    @property
    def days_remaining(self):
        """Calculate days until campaign ends"""
        if self.end_date:
            delta = self.end_date - timezone.now()
            return max(0, delta.days)
        return 0

    @property
    def calculated_ctr(self):
        """Calculate current click-through rate"""
        if self.impressions > 0:
            return (self.clicks / self.impressions) * 100
        return Decimal('0')

    @property
    def calculated_conversion_rate(self):
        """Calculate current conversion rate"""
        if self.clicks > 0:
            return (self.conversions / self.clicks) * 100
        return Decimal('0')

    @property
    def estimated_reach(self):
        """Estimate potential reach based on targeting"""
        from apps.users.models import ClientH
        from django.db.models import Q
        
        base_query = ClientH.objects.filter(status='active')
        
        # Apply audience filters
        if self.target_audience != 'all':
            if self.target_audience == 'new':
                base_query = base_query.filter(total_spent=0)
            elif self.target_audience == 'returning':
                base_query = base_query.filter(total_spent__gt=0)
            elif self.target_audience == 'premium':
                base_query = base_query.filter(account_tier='premium')
            elif self.target_audience == 'business':
                base_query = base_query.filter(account_tier='business')
            elif self.target_audience == 'enterprise':
                base_query = base_query.filter(account_tier='enterprise')
            elif self.target_audience == 'high_usage':
                base_query = base_query.filter(lifetime_data_used__gte=10737418240)  # 10GB
            elif self.target_audience == 'low_usage':
                base_query = base_query.filter(lifetime_data_used__lt=1073741824)  # 1GB
        
        if self.require_premium:
            base_query = base_query.filter(account_tier__in=['premium', 'business', 'enterprise'])
        
        return base_query.count()

    def get_today_spend(self):
        """Calculate today's spend"""
        from apps.analytics.models import AdClick, AdImpression
        from django.utils import timezone
        from datetime import datetime, time
        
        today_start = datetime.combine(timezone.now().date(), time.min)
        today_end = datetime.combine(timezone.now().date(), time.max)
        
        today_clicks = AdClick.objects.filter(
            advertisement=self,
            created_at__range=(today_start, today_end)
        ).count()
        
        today_impressions = AdImpression.objects.filter(
            advertisement=self,
            created_at__range=(today_start, today_end)
        ).count()
        
        spend = Decimal('0')
        if self.bidding_strategy == 'cpc':
            spend += today_clicks * self.cost_per_click
        elif self.bidding_strategy == 'cpm':
            spend += (today_impressions / 1000) * self.cost_per_impression
        
        return spend

    def record_impression(self, user=None, device_type=None, ip_address=None, session_duration=None):
        """Record an ad impression with detailed tracking"""
        from apps.analytics.models import AdImpression
        
        self.impressions += 1
        self.last_shown = timezone.now()
        
        if user and self.unique_users_reached == 0:
            self.unique_users_reached = 1
        elif user:
            # Check if this is a unique user
            existing_impressions = AdImpression.objects.filter(
                advertisement=self,
                user=user
            ).count()
            if existing_impressions == 0:
                self.unique_users_reached += 1
        
        if session_duration:
            current_avg = self.avg_display_time.total_seconds()
            total_impressions = self.impressions
            new_avg = ((current_avg * (total_impressions - 1)) + session_duration) / total_impressions
            self.avg_display_time = timedelta(seconds=new_avg)
        
        self.click_through_rate = self.calculated_ctr
        self.save()
        
        # Create detailed impression record
        AdImpression.objects.create(
            advertisement=self,
            user=user,
            device_type=device_type or '',
            ip_address=ip_address,
            location=self.location,
            session_duration=session_duration or 0,
            user_agent=self._get_user_agent_from_request()
        )
        
        self.update_performance_score()

    def record_click(self, user=None, device_type=None, ip_address=None, referrer=''):
        """Record an ad click with cost calculation"""
        from apps.analytics.models import AdClick
        
        self.clicks += 1
        
        # Calculate and add cost based on bidding strategy
        if self.bidding_strategy == 'cpc' and self.cost_per_click > 0:
            self.total_spent += self.cost_per_click
        elif self.bidding_strategy == 'cpa':
            # Cost per action is only charged on conversion
            pass
        
        self.click_through_rate = self.calculated_ctr
        self.save()
        
        # Create detailed click record
        AdClick.objects.create(
            advertisement=self,
            user=user,
            device_type=device_type or '',
            ip_address=ip_address,
            location=self.location,
            referrer=referrer,
            user_agent=self._get_user_agent_from_request()
        )
        
        self.update_performance_score()

    def record_conversion(self, user, conversion_value=0, conversion_type='signup', metadata=None):
        """Record a conversion with value tracking"""
        from apps.analytics.models import AdConversion
        
        self.conversions += 1
        
        # Add cost for CPA bidding
        if self.bidding_strategy == 'cpa' and self.cost_per_action > 0:
            self.total_spent += self.cost_per_action
        
        self.conversion_rate = self.calculated_conversion_rate
        self.save()
        
        # Create conversion record
        AdConversion.objects.create(
            advertisement=self,
            user=user,
            conversion_value=conversion_value,
            conversion_type=conversion_type,
            location=self.location,
            metadata=metadata or {}
        )
        
        self.update_performance_score()

    def update_performance_score(self):
        """Comprehensive performance scoring algorithm"""
        score = Decimal('0')
        
        # CTR Score (max 4 points)
        ctr = self.calculated_ctr
        if ctr > 5:  # 5% CTR = excellent
            score += 4
        elif ctr > 2:  # 2% CTR = good
            score += 3
        elif ctr > 0.5:  # 0.5% CTR = average
            score += 2
        elif ctr > 0.1:  # 0.1% CTR = poor
            score += 1
        
        # Conversion Rate Score (max 3 points)
        conv_rate = self.calculated_conversion_rate
        if conv_rate > 10:  # 10% conversion rate = excellent
            score += 3
        elif conv_rate > 5:  # 5% conversion rate = good
            score += 2
        elif conv_rate > 1:  # 1% conversion rate = average
            score += 1
        
        # Engagement Score (max 2 points)
        if self.avg_display_time.total_seconds() > 30:  # 30+ seconds view time
            score += 2
        elif self.avg_display_time.total_seconds() > 10:  # 10+ seconds view time
            score += 1
        
        # Volume Score (max 1 point)
        if self.impressions > 1000:
            score += 1
        
        self.performance_score = min(score, 10)
        self.save()

    def can_show_to_user(self, user, current_location, device_type='desktop'):
        """Comprehensive user targeting check"""
        if not self.is_active:
            return False
        
        # Location targeting check
        if self.target_locations.exists() and current_location not in self.target_locations.all():
            return False
        
        if current_location in self.exclude_locations.all():
            return False
        
        # Device targeting check
        if self.target_devices != 'all':
            if self.target_devices == 'mobile' and device_type not in ['phone', 'tablet']:
                return False
            elif self.target_devices == 'desktop' and device_type != 'desktop':
                return False
            elif self.target_devices == 'tablet' and device_type != 'tablet':
                return False
            elif self.target_devices == 'ios' and 'ios' not in device_type.lower():
                return False
            elif self.target_devices == 'android' and 'android' not in device_type.lower():
                return False
        
        # User-based targeting
        if user and hasattr(user, 'client_profile'):
            client_profile = user.client_profile
            
            # Audience targeting
            if self.target_audience != 'all':
                if self.target_audience == 'new' and client_profile.total_spent > 0:
                    return False
                elif self.target_audience == 'returning' and client_profile.total_spent == 0:
                    return False
                elif self.target_audience == 'premium' and client_profile.account_tier != 'premium':
                    return False
                elif self.target_audience == 'business' and client_profile.account_tier != 'business':
                    return False
                elif self.target_audience == 'enterprise' and client_profile.account_tier != 'enterprise':
                    return False
                elif self.target_audience == 'high_usage' and client_profile.lifetime_data_used < 10737418240:  # 10GB
                    return False
                elif self.target_audience == 'low_usage' and client_profile.lifetime_data_used >= 1073741824:  # 1GB
                    return False
                elif self.target_audience == 'roaming' and not client_profile.is_roaming:
                    return False
            
            # Balance check
            if client_profile.balance < self.min_user_balance:
                return False
            
            # Package targeting
            if self.target_packages.exists():
                user_packages = client_profile.get_active_packages()
                if not any(pkg in user_packages for pkg in self.target_packages.all()):
                    return False
            
            # Premium requirement
            if self.require_premium and client_profile.account_tier not in ['premium', 'business', 'enterprise']:
                return False
            
            # Frequency capping
            if self.max_impressions_per_user > 0:
                from apps.analytics.models import AdImpression
                recent_impressions = AdImpression.objects.filter(
                    advertisement=self,
                    user=client_profile,
                    created_at__gte=timezone.now() - self.impression_interval
                ).count()
                
                if recent_impressions >= self.max_impressions_per_user:
                    return False
            
            # Time-based capping
            if self.min_time_between_views > timedelta(0):
                from apps.analytics.models import AdImpression
                last_impression = AdImpression.objects.filter(
                    advertisement=self,
                    user=client_profile
                ).order_by('-created_at').first()
                
                if last_impression and (timezone.now() - last_impression.created_at) < self.min_time_between_views:
                    return False
        
        return True

    def get_available_locations(self):
        """Get all locations where this ad can be shown"""
        if self.target_locations.exists():
            return self.target_locations.all()
        elif self.location:
            return [self.location]
        else:
            from apps.locations.models import Location
            return Location.objects.filter(is_online=True)

    def is_available_in_roaming(self, home_location, visiting_location):
        """Check if ad should be shown during roaming"""
        try:
            from apps.locations.models import RoamingPolicy
            roaming_policy = RoamingPolicy.objects.get(
                home_location=home_location,
                visiting_location=visiting_location,
                is_active=True
            )
            
            # Custom rules for roaming ads
            if roaming_policy.allowed:
                # You might want to show different ads or adjust bidding for roaming users
                return True
            else:
                return False
                
        except RoamingPolicy.DoesNotExist:
            # No specific policy, use default behavior
            pass
        
        return True

    def pause(self):
        """Pause the advertisement campaign"""
        self.status = 'paused'
        self.save()

    def activate(self):
        """Activate the advertisement campaign"""
        self.status = 'active'
        self.save()

    def archive(self):
        """Archive the advertisement campaign"""
        self.status = 'archived'
        self.save()

    def duplicate(self):
        """Create a duplicate of this advertisement with new campaign ID"""
        duplicate = Advertisement.objects.get(pk=self.pk)
        duplicate.pk = None
        duplicate.campaign_id = uuid.uuid4()
        duplicate.title = f"Copy of {self.title}"
        duplicate.status = 'draft'
        duplicate.impressions = 0
        duplicate.clicks = 0
        duplicate.conversions = 0
        duplicate.unique_users_reached = 0
        duplicate.total_spent = 0
        duplicate.performance_score = 0
        duplicate.save()
        
        # Copy many-to-many relationships
        duplicate.target_locations.set(self.target_locations.all())
        duplicate.exclude_locations.set(self.exclude_locations.all())
        duplicate.target_packages.set(self.target_packages.all())
        
        return duplicate

    def get_performance_report(self, start_date=None, end_date=None):
        """Generate comprehensive performance report"""
        from apps.analytics.models import AdImpression, AdClick, AdConversion
        from django.db.models import Count, Avg, Sum
        
        if not start_date:
            start_date = self.start_date
        if not end_date:
            end_date = timezone.now()
        
        impressions = AdImpression.objects.filter(
            advertisement=self,
            created_at__range=(start_date, end_date)
        )
        clicks = AdClick.objects.filter(
            advertisement=self,
            created_at__range=(start_date, end_date)
        )
        conversions = AdConversion.objects.filter(
            advertisement=self,
            created_at__range=(start_date, end_date)
        )
        
        report = {
            'period': {
                'start': start_date,
                'end': end_date
            },
            'impressions': impressions.count(),
            'clicks': clicks.count(),
            'conversions': conversions.count(),
            'ctr': self.calculated_ctr,
            'conversion_rate': self.calculated_conversion_rate,
            'total_spend': self.total_spent,
            'avg_session_duration': self.avg_display_time,
            'unique_users': self.unique_users_reached,
            'performance_score': self.performance_score,
            'device_breakdown': impressions.values('device_type').annotate(count=Count('id')),
            'location_breakdown': impressions.values('location__name').annotate(count=Count('id')),
        }
        
        return report

    @classmethod
    def get_ads_for_user(cls, user, current_location, device_type='desktop', limit=5, context='default'):
        """Get personalized ads for a specific user and context"""
        now = timezone.now()
        
        ads = cls.objects.filter(
            status='active',
            start_date__lte=now,
            end_date__gte=now
        ).select_related('location').prefetch_related(
            'target_locations', 'exclude_locations', 'target_packages'
        ).order_by('-priority', '-performance_score', '-weight')
        
        filtered_ads = []
        for ad in ads:
            if ad.can_show_to_user(user, current_location, device_type):
                filtered_ads.append(ad)
            if len(filtered_ads) >= limit:
                break
        
        return filtered_ads

    def _get_user_agent_from_request(self):
        """Extract user agent from request context"""
        # This would be implemented based on your request handling
        # For now, return empty string
        return ""

    def save(self, *args, **kwargs):
        """Custom save method with validation"""
        # Auto-update performance metrics before saving
        if self.impressions > 0:
            self.click_through_rate = self.calculated_ctr
            self.conversion_rate = self.calculated_conversion_rate
        
        # Validate budget constraints
        if self.total_spent > self.budget and self.budget > 0:
            self.status = 'paused'
        
        super().save(*args, **kwargs)