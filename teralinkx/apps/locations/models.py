# apps/locations/models.py
from django.db import models
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import uuid

from core.models import TimeStampedModel

class Location(TimeStampedModel):
    """Enterprise-grade location management with advanced advertisement capabilities"""
    
    LOCATION_TYPES = [
        ('headquarters', 'Headquarters'),
        ('branch', 'Branch'),
        ('hotspot', 'Hotspot Location'),
        ('partner', 'Partner Location'),
        ('popup', 'Popup Location'),
        ('residential', 'Residential Complex'),
        ('commercial', 'Commercial Building'),
        ('educational', 'Educational Institution'),
    ]
    
    PRICING_TIERS = [
        ('economy', 'Economy'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ]
    
    # Core Identification
    id = models.CharField(max_length=20, primary_key=True, help_text="Unique location identifier")
    name = models.CharField(max_length=100, help_text="Display name for the location")
    location_type = models.CharField(max_length=20, choices=LOCATION_TYPES, default='hotspot')
    timezone = models.CharField(max_length=50, default='Africa/Nairobi', help_text="Location timezone")
    
    # Physical Location
    address = models.TextField(blank=True, help_text="Full physical address")
    coordinates = models.CharField(max_length=100, blank=True, help_text="Latitude,Longitude")
    city = models.CharField(max_length=50, blank=True, help_text="City or town")
    country = models.CharField(max_length=50, default='Kenya', help_text="Country")
    region = models.CharField(max_length=50, blank=True, help_text="Region or county")
    
    # Network Infrastructure
    network_config = models.JSONField(
        default=dict, 
        help_text="Location-specific network configuration and settings"
    )
    router_ip = models.GenericIPAddressField(blank=True, null=True, help_text="Primary router IP address")
    nas_identifier = models.CharField(max_length=100, blank=True, help_text="Network Access Server identifier")
    bandwidth_capacity = models.IntegerField(default=1000, help_text="Total bandwidth capacity in Mbps")
    current_bandwidth_usage = models.IntegerField(default=0, help_text="Current bandwidth usage in Mbps")
    
    # Business Configuration
    business_hours = models.JSONField(
        default=dict, 
        help_text="Operating hours configuration {day: {open: 'HH:MM', close: 'HH:MM'}}"
    )
    pricing_tier = models.CharField(max_length=20, choices=PRICING_TIERS, default='standard')
    base_price_multiplier = models.DecimalField(max_digits=3, decimal_places=2, default=1.0, help_text="Price multiplier for this location")
    tax_rate = models.DecimalField(max_digits=4, decimal_places=2, default=16.0, help_text="VAT rate percentage")
    
    # Capacity Management
    max_concurrent_users = models.IntegerField(default=100, help_text="Maximum number of concurrent users")
    current_user_count = models.IntegerField(default=0, help_text="Current number of active users")
    max_devices_per_user = models.IntegerField(default=3, help_text="Maximum devices allowed per user")
    peak_hours = models.JSONField(default=list, help_text="List of peak usage hours [0-23]")
    
    # Status & Monitoring
    is_online = models.BooleanField(default=True, help_text="Whether the location is currently operational")
    is_public = models.BooleanField(default=True, help_text="Whether the location is publicly accessible")
    maintenance_mode = models.BooleanField(default=False, help_text="Whether location is in maintenance mode")
    last_health_check = models.DateTimeField(null=True, blank=True, help_text="Last successful health check")
    health_status = models.CharField(
        max_length=20,
        choices=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('poor', 'Poor'),
            ('critical', 'Critical'),
        ],
        default='good'
    )
    uptime_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=100.0, help_text="Uptime percentage over last 30 days")
    
    # Advertisement Configuration
    ad_settings = models.JSONField(
        default=dict,
        help_text="Location-specific advertisement configuration and rules"
    )
    max_ads_per_session = models.IntegerField(
        default=3,
        help_text="Maximum number of ads to show per user session"
    )
    ad_refresh_interval = models.IntegerField(
        default=30,
        help_text="Minutes between ad rotations for the same user"
    )
    allow_video_ads = models.BooleanField(
        default=True,
        help_text="Allow video advertisements at this location"
    )
    allow_popup_ads = models.BooleanField(
        default=False,
        help_text="Allow popup advertisements at this location"
    )
    allow_audio_ads = models.BooleanField(
        default=False,
        help_text="Allow audio advertisements at this location"
    )
    ad_density = models.CharField(
        max_length=10,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        default='medium',
        help_text="Ad density setting for this location"
    )
    min_ad_quality_score = models.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        default=3.0,
        help_text="Minimum quality score for ads shown at this location (1-10)"
    )
    
    # Advertisement Performance Tracking
    total_ad_impressions = models.BigIntegerField(
        default=0,
        help_text="Total advertisements shown at this location"
    )
    total_ad_clicks = models.BigIntegerField(
        default=0,
        help_text="Total advertisement clicks at this location"
    )
    total_ad_revenue = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        help_text="Total advertisement revenue generated at this location in KES"
    )
    avg_ad_ctr = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        help_text="Average click-through rate for ads at this location"
    )
    last_ad_shown = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When the last advertisement was shown at this location"
    )
    ad_health_score = models.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        default=5.0,
        help_text="Overall advertisement health score for this location (1-10)"
    )
    
    # Financial Metrics
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Total revenue generated")
    monthly_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Current month revenue")
    operational_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Monthly operational cost")
    
    # Metadata
    description = models.TextField(blank=True, help_text="Location description and notes")
    contact_person = models.CharField(max_length=100, blank=True, help_text="Primary contact person")
    contact_phone = models.CharField(max_length=20, blank=True, help_text="Contact phone number")
    contact_email = models.EmailField(blank=True, help_text="Contact email address")
    tags = models.JSONField(default=list, help_text="Tags for categorization and filtering")
    
    class Meta:
        db_table = 'locations'
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'
        indexes = [
            models.Index(fields=['location_type']),
            models.Index(fields=['is_online']),
            models.Index(fields=['pricing_tier']),
            models.Index(fields=['city', 'country']),
            models.Index(fields=['health_status']),
            models.Index(fields=['ad_health_score']),
            models.Index(fields=['total_revenue']),
        ]
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.id}) - {self.get_location_type_display()}"

    @property
    def is_operational(self):
        """Check if location is fully operational"""
        return self.is_online and not self.maintenance_mode and self.health_status not in ['poor', 'critical']

    @property
    def available_capacity(self):
        """Calculate available user capacity"""
        return max(0, self.max_concurrent_users - self.current_user_count)

    @property
    def capacity_percentage(self):
        """Calculate current capacity usage percentage"""
        if self.max_concurrent_users == 0:
            return 0
        return (self.current_user_count / self.max_concurrent_users) * 100

    @property
    def bandwidth_usage_percentage(self):
        """Calculate current bandwidth usage percentage"""
        if self.bandwidth_capacity == 0:
            return 0
        return (self.current_bandwidth_usage / self.bandwidth_capacity) * 100

    @property
    def is_at_capacity(self):
        """Check if location is at or near capacity"""
        return self.capacity_percentage >= 90

    @property
    def ad_revenue_share(self):
        """Calculate advertisement revenue as percentage of total revenue"""
        if self.total_revenue == 0:
            return 0
        return (self.total_ad_revenue / self.total_revenue) * 100

    def update_health_status(self):
        """Comprehensive location health status update"""
        from apps.analytics.models import ActiveSession
        from django.utils import timezone
        from datetime import timedelta
        
        # Check current session count
        active_sessions = ActiveSession.objects.filter(
            location=self,
            terminated_at__isnull=True
        ).count()
        
        self.current_user_count = active_sessions
        
        # Calculate bandwidth usage (simplified - would integrate with actual monitoring)
        self.current_bandwidth_usage = min(
            self.bandwidth_capacity,
            active_sessions * 5  # Assume 5 Mbps per user average
        )
        
        # Determine health status based on multiple factors
        health_score = 100
        
        # Capacity factor
        if self.capacity_percentage >= 90:
            health_score -= 30
        elif self.capacity_percentage >= 75:
            health_score -= 15
        
        # Bandwidth factor
        if self.bandwidth_usage_percentage >= 90:
            health_score -= 25
        elif self.bandwidth_usage_percentage >= 75:
            health_score -= 10
        
        # Uptime factor
        if self.uptime_percentage < 95:
            health_score -= 20
        elif self.uptime_percentage < 99:
            health_score -= 10
        
        # Map score to status
        if health_score >= 90:
            self.health_status = 'excellent'
        elif health_score >= 75:
            self.health_status = 'good'
        elif health_score >= 60:
            self.health_status = 'fair'
        elif health_score >= 40:
            self.health_status = 'poor'
        else:
            self.health_status = 'critical'
        
        self.last_health_check = timezone.now()
        self.save()

    def get_available_packages(self):
        """Get packages available at this location"""
        from apps.packages.models import PackageType
        return PackageType.objects.filter(
            locations=self,
            is_active=True
        ).order_by('price')

    def get_advertisement_stats(self, days=30):
        """Get comprehensive advertisement statistics for this location"""
        from apps.analytics.models import AdImpression, AdClick, AdConversion
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Count, Avg, Sum
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        impressions = AdImpression.objects.filter(
            location=self,
            created_at__gte=cutoff_date
        )
        clicks = AdClick.objects.filter(
            location=self,
            created_at__gte=cutoff_date
        )
        conversions = AdConversion.objects.filter(
            location=self,
            created_at__gte=cutoff_date
        )
        
        total_impressions = impressions.count()
        total_clicks = clicks.count()
        total_conversions = conversions.count()
        
        ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        
        # Calculate revenue from different bidding strategies
        revenue = Decimal('0')
        for click in clicks.select_related('advertisement'):
            ad = click.advertisement
            if ad.bidding_strategy == 'cpc':
                revenue += ad.cost_per_click
            elif ad.bidding_strategy == 'cpm':
                # For CPM, we need impressions data
                ad_impressions = impressions.filter(advertisement=ad).count()
                revenue += (ad_impressions / 1000) * ad.cost_per_impression
        
        stats = {
            'period': {
                'days': days,
                'start_date': cutoff_date.date(),
                'end_date': timezone.now().date()
            },
            'performance': {
                'total_impressions': total_impressions,
                'total_clicks': total_clicks,
                'total_conversions': total_conversions,
                'click_through_rate': ctr,
                'conversion_rate': conversion_rate,
                'revenue_earned': revenue,
                'revenue_per_user': revenue / max(1, self.current_user_count),
            },
            'engagement': {
                'avg_session_duration': impressions.aggregate(avg=Avg('session_duration'))['avg'] or 0,
                'unique_users_reached': impressions.values('user').distinct().count(),
                'avg_impressions_per_user': total_impressions / max(1, impressions.values('user').distinct().count()),
            },
            'breakdowns': {
                'top_performing_ads': self.get_top_performing_ads(days),
                'device_breakdown': self.get_ad_device_breakdown(days),
                'hourly_traffic': self.get_ad_hourly_traffic(days),
                'ad_type_performance': self.get_ad_type_performance(days),
            }
        }
        
        return stats

    def get_top_performing_ads(self, days=30, limit=10):
        """Get top performing advertisements for this location"""
        from apps.analytics.models import AdImpression
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Count, Avg
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        top_ads = AdImpression.objects.filter(
            location=self,
            created_at__gte=cutoff_date
        ).values(
            'advertisement__id',
            'advertisement__title',
            'advertisement__ad_type',
            'advertisement__campaign_id',
            'advertisement__cta_text'
        ).annotate(
            impressions=Count('id'),
            clicks=Count('advertisement__ad_clicks'),
            conversions=Count('advertisement__ad_conversions'),
            avg_session_duration=Avg('session_duration')
        ).order_by('-impressions')[:limit]
        
        # Calculate metrics for each ad
        for ad in top_ads:
            ad['ctr'] = (ad['clicks'] / ad['impressions'] * 100) if ad['impressions'] > 0 else 0
            ad['conversion_rate'] = (ad['conversions'] / ad['clicks'] * 100) if ad['clicks'] > 0 else 0
            ad['performance_score'] = min(
                (ad['ctr'] * 0.4) + (ad['conversion_rate'] * 0.3) + (min(ad['avg_session_duration'] or 0, 60) * 0.3),
                10
            )
        
        return list(top_ads)

    def get_ad_device_breakdown(self, days=30):
        """Get advertisement performance breakdown by device type"""
        from apps.analytics.models import AdImpression
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Count
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        device_breakdown = AdImpression.objects.filter(
            location=self,
            created_at__gte=cutoff_date
        ).values('device_type').annotate(
            impressions=Count('id'),
            clicks=Count('advertisement__ad_clicks'),
            conversions=Count('advertisement__ad_conversions')
        ).order_by('-impressions')
        
        # Calculate metrics for each device type
        for device in device_breakdown:
            device['ctr'] = (device['clicks'] / device['impressions'] * 100) if device['impressions'] > 0 else 0
            device['conversion_rate'] = (device['conversions'] / device['clicks'] * 100) if device['clicks'] > 0 else 0
        
        return list(device_breakdown)

    def get_ad_hourly_traffic(self, days=30):
        """Get advertisement traffic patterns by hour of day"""
        from apps.analytics.models import AdImpression
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Count
        from django.db.models.functions import ExtractHour
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        hourly_traffic = AdImpression.objects.filter(
            location=self,
            created_at__gte=cutoff_date
        ).annotate(
            hour=ExtractHour('created_at')
        ).values('hour').annotate(
            impressions=Count('id'),
            clicks=Count('advertisement__ad_clicks')
        ).order_by('hour')
        
        return list(hourly_traffic)

    def get_ad_type_performance(self, days=30):
        """Get performance metrics by advertisement type"""
        from apps.analytics.models import AdImpression
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Count, Avg
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        type_performance = AdImpression.objects.filter(
            location=self,
            created_at__gte=cutoff_date
        ).values('advertisement__ad_type').annotate(
            impressions=Count('id'),
            clicks=Count('advertisement__ad_clicks'),
            conversions=Count('advertisement__ad_conversions'),
            avg_duration=Avg('session_duration')
        ).order_by('-impressions')
        
        for perf in type_performance:
            perf['ctr'] = (perf['clicks'] / perf['impressions'] * 100) if perf['impressions'] > 0 else 0
            perf['conversion_rate'] = (perf['conversions'] / perf['clicks'] * 100) if perf['clicks'] > 0 else 0
        
        return list(type_performance)

    def calculate_ad_revenue(self, days=30):
        """Calculate total advertisement revenue for this location"""
        from apps.analytics.models import AdClick, AdImpression
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        clicks = AdClick.objects.filter(
            location=self,
            created_at__gte=cutoff_date
        ).select_related('advertisement')
        
        revenue = Decimal('0')
        for click in clicks:
            ad = click.advertisement
            if ad.bidding_strategy == 'cpc':
                revenue += ad.cost_per_click
            elif ad.bidding_strategy == 'cpm':
                # Get impressions for this ad in the period
                impressions = AdImpression.objects.filter(
                    advertisement=ad,
                    location=self,
                    created_at__gte=cutoff_date
                ).count()
                revenue += (impressions / 1000) * ad.cost_per_impression
            elif ad.bidding_strategy == 'cpa':
                # CPA is handled in conversion recording
                pass
        
        return revenue

    def get_recommended_ads(self, user_tier=None, limit=5):
        """Get advertisements recommended for this location based on performance"""
        from django.db.models import Avg, Count, Q
        
        # Base query for active ads
        base_query = Advertisement.objects.filter(
            status='active',
            performance_score__gte=self.min_ad_quality_score
        )
        
        # Filter by location compatibility
        compatible_ads = base_query.filter(
            Q(location=self) | 
            Q(target_locations=self) |
            Q(target_locations__isnull=True)
        ).exclude(
            exclude_locations=self
        ).distinct()
        
        # Get ads that perform well at similar locations
        similar_locations = Location.objects.filter(
            location_type=self.location_type,
            pricing_tier=self.pricing_tier
        ).exclude(id=self.id)
        
        recommended_ads = compatible_ads.filter(
            Q(location__in=similar_locations) |
            Q(target_locations__in=similar_locations)
        ).annotate(
            avg_performance=Avg('performance_score'),
            location_count=Count('location'),
            similar_location_performance=Avg('adimpression__session_duration', filter=Q(adimpression__location__in=similar_locations))
        ).filter(
            avg_performance__gte=7.0,
            location_count__lte=10  # Don't recommend over-saturated ads
        ).order_by('-avg_performance', '-similar_location_performance')[:limit]
        
        return recommended_ads

    def update_ad_health_metrics(self):
        """Update comprehensive advertisement health metrics for this location"""
        from apps.analytics.models import AdImpression, AdClick
        from django.utils import timezone
        from datetime import timedelta
        
        # Calculate recent activity (last 24 hours)
        recent_impressions = AdImpression.objects.filter(
            location=self,
            created_at__gte=timezone.now() - timedelta(hours=24)
        )
        recent_clicks = AdClick.objects.filter(
            location=self,
            created_at__gte=timezone.now() - timedelta(hours=24)
        )
        
        total_recent_impressions = recent_impressions.count()
        total_recent_clicks = recent_clicks.count()
        
        # Update location's advertisement metrics
        self.total_ad_impressions += total_recent_impressions
        self.total_ad_clicks += total_recent_clicks
        
        # Calculate CTR
        if total_recent_impressions > 0:
            recent_ctr = (total_recent_clicks / total_recent_impressions) * 100
            # Update average CTR with smoothing
            if self.avg_ad_ctr == 0:
                self.avg_ad_ctr = recent_ctr
            else:
                self.avg_ad_ctr = (self.avg_ad_ctr * 0.7) + (recent_ctr * 0.3)
        
        # Update last shown timestamp
        if total_recent_impressions > 0:
            self.last_ad_shown = timezone.now()
        
        # Calculate ad health score
        health_factors = []
        
        # Impression volume factor
        if total_recent_impressions > 50:
            health_factors.append(2.0)
        elif total_recent_impressions > 20:
            health_factors.append(1.5)
        elif total_recent_impressions > 5:
            health_factors.append(1.0)
        else:
            health_factors.append(0.5)
        
        # CTR factor
        if self.avg_ad_ctr > 5:
            health_factors.append(2.0)
        elif self.avg_ad_ctr > 2:
            health_factors.append(1.5)
        elif self.avg_ad_ctr > 0.5:
            health_factors.append(1.0)
        else:
            health_factors.append(0.5)
        
        # Engagement factor (average session duration)
        avg_duration = recent_impressions.aggregate(avg=Avg('session_duration'))['avg'] or 0
        if avg_duration > 30:
            health_factors.append(2.0)
        elif avg_duration > 15:
            health_factors.append(1.5)
        elif avg_duration > 5:
            health_factors.append(1.0)
        else:
            health_factors.append(0.5)
        
        # Calculate overall health score (1-10)
        if health_factors:
            base_score = sum(health_factors) / len(health_factors)
            self.ad_health_score = min(base_score * 2.5, 10)  # Scale to 1-10
        
        self.save()

    def get_optimal_ad_schedule(self):
        """Generate optimal advertisement schedule based on traffic patterns"""
        hourly_traffic = self.get_ad_hourly_traffic(days=7)
        
        if not hourly_traffic:
            # Default schedule if no data available
            return {
                'peak_hours': [9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
                'off_peak_hours': [0, 1, 2, 3, 4, 5, 6, 7, 8, 19, 20, 21, 22, 23],
                'recommended_ad_density': {
                    'peak': 'high',
                    'off_peak': 'medium'
                }
            }
        
        # Find peak hours (top 50% of traffic)
        traffic_data = {item['hour']: item['impressions'] for item in hourly_traffic}
        max_impressions = max(traffic_data.values()) if traffic_data else 0
        peak_threshold = max_impressions * 0.5
        
        peak_hours = [hour for hour, impressions in traffic_data.items() if impressions >= peak_threshold]
        off_peak_hours = [hour for hour, impressions in traffic_data.items() if impressions < peak_threshold]
        
        return {
            'peak_hours': sorted(peak_hours),
            'off_peak_hours': sorted(off_peak_hours),
            'recommended_ad_density': {
                'peak': 'high',
                'off_peak': 'medium' if len(off_peak_hours) > 0 else 'low'
            },
            'traffic_summary': {
                'total_daily_impressions': sum(traffic_data.values()),
                'busiest_hour': max(traffic_data, key=traffic_data.get) if traffic_data else None,
                'quietest_hour': min(traffic_data, key=traffic_data.get) if traffic_data else None,
            }
        }

    def can_show_ad_type(self, ad_type):
        """Check if specific ad type is allowed at this location"""
        ad_type_restrictions = {
            'video': self.allow_video_ads,
            'popup': self.allow_popup_ads,
            'audio': self.allow_audio_ads,
        }
        
        return ad_type_restrictions.get(ad_type, True)

    def get_ad_display_rules(self):
        """Get comprehensive ad display rules for this location"""
        return {
            'max_ads_per_session': self.max_ads_per_session,
            'ad_refresh_interval': self.ad_refresh_interval,
            'allowed_ad_types': {
                'banner': True,  # Always allowed
                'interstitial': True,  # Always allowed
                'video': self.allow_video_ads,
                'popup': self.allow_popup_ads,
                'notification': True,  # Always allowed
                'native': True,  # Always allowed
                'carousel': True,  # Always allowed
                'audio': self.allow_audio_ads,
            },
            'density': self.ad_density,
            'min_quality_score': float(self.min_ad_quality_score),
            'frequency_capping': {
                'max_impressions_per_user': 5,  # Default, can be overridden per ad
                'impression_interval_hours': 24,  # Default, can be overridden per ad
            }
        }

    def record_ad_revenue(self, amount, ad_campaign=None):
        """Record advertisement revenue for this location"""
        from apps.finance.models import BalanceTransaction
        
        self.total_ad_revenue += amount
        self.total_revenue += amount
        self.monthly_revenue += amount
        self.save()
        
        # Create financial transaction record
        if ad_campaign:
            BalanceTransaction.objects.create(
                transaction_type='ad_revenue',
                direction='credit',
                amount=amount,
                description=f"Ad revenue from campaign: {ad_campaign}",
                location=self
            )

    def get_location_insights(self):
        """Generate comprehensive insights for this location"""
        stats = self.get_advertisement_stats(days=7)
        health = self.health_status
        capacity = self.capacity_percentage
        ad_health = self.ad_health_score
        
        insights = {
            'operational': {
                'status': 'optimal' if health in ['excellent', 'good'] else 'needs_attention',
                'message': f"Location health is {health} with {capacity:.1f}% capacity used",
                'recommendations': []
            },
            'advertising': {
                'status': 'performing_well' if ad_health >= 7 else 'needs_optimization',
                'message': f"Ad health score: {ad_health}/10, CTR: {stats['performance']['click_through_rate']:.2f}%",
                'recommendations': []
            },
            'revenue': {
                'status': 'growing' if self.monthly_revenue > 0 else 'initial',
                'message': f"Monthly revenue: KES {self.monthly_revenue:,.2f} (Ad share: {self.ad_revenue_share:.1f}%)",
                'recommendations': []
            }
        }
        
        # Generate recommendations
        if health in ['poor', 'critical']:
            insights['operational']['recommendations'].append("Consider maintenance or upgrade to improve location health")
        
        if capacity >= 90:
            insights['operational']['recommendations'].append("Location near capacity - consider expanding infrastructure")
        
        if ad_health < 5:
            insights['advertising']['recommendations'].append("Optimize ad targeting and refresh underperforming campaigns")
        
        if self.ad_revenue_share < 10:
            insights['revenue']['recommendations'].append("Increase ad inventory and improve ad placement for higher revenue")
        
        return insights

    def get_geographic_context(self):
        """Get geographic context for location-based targeting"""
        return {
            'coordinates': self.coordinates,
            'address': self.address,
            'city': self.city,
            'region': self.region,
            'country': self.country,
            'timezone': self.timezone,
            'location_type': self.location_type,
            'pricing_tier': self.pricing_tier,
        }

    def is_similar_to(self, other_location):
        """Check if this location is similar to another for ad targeting"""
        similarity_score = 0
        
        if self.location_type == other_location.location_type:
            similarity_score += 3
        
        if self.pricing_tier == other_location.pricing_tier:
            similarity_score += 2
        
        if self.city == other_location.city:
            similarity_score += 2
        
        if self.region == other_location.region:
            similarity_score += 1
        
        return similarity_score >= 4  # Threshold for similarity

    def __str__(self):
        return f"{self.name} ({self.id}) - {self.get_location_type_display()} - {self.city}"


class RoamingPolicy(TimeStampedModel):
    """Enhanced roaming policies with business rules and advertisement support"""
    
    home_location = models.ForeignKey(
        Location, 
        on_delete=models.CASCADE, 
        related_name='home_policies'
    )
    visiting_location = models.ForeignKey(
        Location, 
        on_delete=models.CASCADE, 
        related_name='visiting_policies'
    )
    
    # Access Rules
    allowed = models.BooleanField(default=True, help_text="Whether roaming is allowed between these locations")
    requires_approval = models.BooleanField(default=False, help_text="Whether manual approval is required")
    auto_approve = models.BooleanField(default=True, help_text="Whether to auto-approve roaming requests")
    
    # Service Limitations
    speed_limit_mbps = models.IntegerField(null=True, blank=True, help_text="Maximum speed allowed while roaming")
    session_time_limit = models.DurationField(null=True, blank=True, help_text="Maximum session duration while roaming")
    daily_data_limit_mb = models.BigIntegerField(null=True, blank=True, help_text="Daily data limit while roaming")
    concurrent_sessions_limit = models.IntegerField(default=1, help_text="Maximum concurrent sessions while roaming")
    
    # Pricing & Billing
    billing_rate_multiplier = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=1.0,
        help_text="Price multiplier for roaming usage"
    )
    surcharge_fixed = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Fixed surcharge for roaming access"
    )
    ad_revenue_share = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.5,
        help_text="Revenue share percentage for ads shown during roaming"
    )
    
    # Advertisement Rules for Roaming
    show_roaming_ads = models.BooleanField(
        default=True,
        help_text="Whether to show advertisements to roaming users"
    )
    roaming_ad_intensity = models.CharField(
        max_length=10,
        choices=[('low', 'Low'), ('normal', 'Normal'), ('high', 'High')],
        default='normal',
        help_text="Advertisement intensity for roaming users"
    )
    roaming_ad_categories = models.JSONField(
        default=list,
        help_text="Specific ad categories to show to roaming users"
    )
    
    # Business Rules
    priority = models.IntegerField(
        default=1, 
        help_text="Higher priority policies take precedence"
    )
    is_active = models.BooleanField(default=True, help_text="Whether this policy is active")
    effective_date = models.DateTimeField(default=timezone.now, help_text="When this policy becomes effective")
    expiration_date = models.DateTimeField(null=True, blank=True, help_text="When this policy expires")
    
    # Metadata
    description = models.TextField(blank=True, help_text="Policy description and notes")
    created_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True,
        help_text="User who created this policy"
    )

    class Meta:
        db_table = 'roaming_policies'
        verbose_name = 'Roaming Policy'
        verbose_name_plural = 'Roaming Policies'
        unique_together = ['home_location', 'visiting_location']
        indexes = [
            models.Index(fields=['home_location', 'visiting_location']),
            models.Index(fields=['is_active']),
            models.Index(fields=['priority']),
            models.Index(fields=['effective_date', 'expiration_date']),
        ]
        ordering = ['-priority', '-created_at']

    def __str__(self):
        status = "✓" if self.allowed else "✗"
        return f"{status} {self.home_location} → {self.visiting_location} (Priority: {self.priority})"

    @property
    def is_effective(self):
        """Check if policy is currently effective"""
        now = timezone.now()
        is_within_dates = (
            self.effective_date <= now and 
            (self.expiration_date is None or now <= self.expiration_date)
        )
        return self.is_active and is_within_dates

    @property
    def roaming_cost_multiplier(self):
        """Calculate total cost multiplier for roaming"""
        return max(Decimal('1.0'), self.billing_rate_multiplier)

    def can_user_roam(self, user, check_approval=True):
        """Check if a user can roam under this policy"""
        if not self.is_effective or not self.allowed:
            return False
        
        if check_approval and self.requires_approval and not self.auto_approve:
            # Check if user has approval
            from apps.users.models import RoamingApproval
            try:
                approval = RoamingApproval.objects.get(
                    user=user,
                    home_location=self.home_location,
                    visiting_location=self.visiting_location,
                    is_approved=True
                )
                return approval.is_active
            except RoamingApproval.DoesNotExist:
                return False
        
        return True

    def get_roaming_ad_settings(self):
        """Get advertisement settings specific to roaming"""
        intensity_multipliers = {
            'low': 0.5,
            'normal': 1.0,
            'high': 1.5
        }
        
        return {
            'show_ads': self.show_roaming_ads,
            'intensity_multiplier': intensity_multipliers.get(self.roaming_ad_intensity, 1.0),
            'categories': self.roaming_ad_categories,
            'revenue_share': float(self.ad_revenue_share),
            'max_ads_per_session': 3,  # Conservative limit for roaming
            'ad_refresh_interval': 45,  # Longer interval for roaming
        }

    def calculate_roaming_revenue_split(self, ad_revenue):
        """Calculate revenue split between home and visiting locations"""
        home_share = ad_revenue * (1 - self.ad_revenue_share)
        visiting_share = ad_revenue * self.ad_revenue_share
        
        return {
            'home_location': home_share,
            'visiting_location': visiting_share,
            'total': ad_revenue
        }

    def get_usage_restrictions(self):
        """Get comprehensive usage restrictions for roaming"""
        return {
            'speed_limit_mbps': self.speed_limit_mbps,
            'session_time_limit': self.session_time_limit.total_seconds() if self.session_time_limit else None,
            'daily_data_limit_mb': self.daily_data_limit_mb,
            'concurrent_sessions': self.concurrent_sessions_limit,
            'billing_multiplier': float(self.billing_rate_multiplier),
            'surcharge': float(self.surcharge_fixed),
        }

    def is_reciprocal(self):
        """Check if there's a reciprocal policy in the opposite direction"""
        try:
            reciprocal = RoamingPolicy.objects.get(
                home_location=self.visiting_location,
                visiting_location=self.home_location,
                is_active=True
            )
            return reciprocal.is_effective
        except RoamingPolicy.DoesNotExist:
            return False

    def get_reciprocal_policy(self):
        """Get the reciprocal roaming policy if it exists"""
        try:
            return RoamingPolicy.objects.get(
                home_location=self.visiting_location,
                visiting_location=self.home_location
            )
        except RoamingPolicy.DoesNotExist:
            return None

    def create_reciprocal_policy(self, created_by=None):
        """Create a reciprocal roaming policy"""
        if self.get_reciprocal_policy():
            return None  # Reciprocal already exists
        
        reciprocal = RoamingPolicy.objects.create(
            home_location=self.visiting_location,
            visiting_location=self.home_location,
            allowed=self.allowed,
            requires_approval=self.requires_approval,
            auto_approve=self.auto_approve,
            speed_limit_mbps=self.speed_limit_mbps,
            session_time_limit=self.session_time_limit,
            daily_data_limit_mb=self.daily_data_limit_mb,
            billing_rate_multiplier=self.billing_rate_multiplier,
            surcharge_fixed=self.surcharge_fixed,
            ad_revenue_share=Decimal('1.0') - self.ad_revenue_share,  # Inverse revenue share
            show_roaming_ads=self.show_roaming_ads,
            roaming_ad_intensity=self.roaming_ad_intensity,
            roaming_ad_categories=self.roaming_ad_categories,
            priority=self.priority,
            is_active=self.is_active,
            effective_date=self.effective_date,
            expiration_date=self.expiration_date,
            description=f"Reciprocal policy for {self}",
            created_by=created_by or self.created_by
        )
        
        return reciprocal

    def deactivate(self):
        """Deactivate this roaming policy"""
        self.is_active = False
        self.save()

    def activate(self):
        """Activate this roaming policy"""
        self.is_active = True
        self.save()

    def extends_existing_policy(self):
        """Check if this policy extends an existing one"""
        existing_policies = RoamingPolicy.objects.filter(
            home_location=self.home_location,
            visiting_location=self.visiting_location
        ).exclude(id=self.id)
        
        return existing_policies.exists()