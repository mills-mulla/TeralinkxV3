# apps/ads/models.py
from django.db import models
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import uuid
from core.models import TimeStampedModel

class Advertisement(TimeStampedModel):
    """Comprehensive advertisement system with full media support"""
    
    AD_TYPES = [
        ('banner', 'Banner Ad'),
        ('interstitial', 'Full Screen Ad'),
        ('popup', 'Popup Ad'),
        ('notification', 'Notification Ad'),
        ('video', 'Video Ad'),
        ('native', 'Native Content Ad'),
        ('carousel', 'Image Carousel Ad'),
        ('audio', 'Audio Ad'),
    ]
    
    AD_STATUS = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('expired', 'Expired'),
        ('archived', 'Archived'),
    ]
    
    # Core Advertisement Information
    title = models.CharField(max_length=200)
    caption = models.TextField(max_length=500, blank=True)
    ad_type = models.CharField(max_length=20, choices=AD_TYPES, default='banner')
    status = models.CharField(max_length=20, choices=AD_STATUS, default='draft')
    campaign_name = models.CharField(max_length=100, blank=True)
    
    # Comprehensive Media Assets
    # Banner, Popup, Native, Notification ads
    image = models.ImageField(
        upload_to='ads/images/%Y/%m/%d/', 
        blank=True, 
        null=True,
        help_text="Primary image for banner, popup, native, notification ads"
    )
    
    # Video ads
    video_file = models.FileField(
        upload_to='ads/videos/%Y/%m/%d/', 
        blank=True, 
        null=True,
        help_text="Video file for video ads (MP4, WebM)"
    )
    video_thumbnail = models.ImageField(
        upload_to='ads/thumbnails/%Y/%m/%d/', 
        blank=True, 
        null=True,
        help_text="Thumbnail for video ads"
    )
    video_duration = models.DurationField(
        blank=True, 
        null=True,
        help_text="Duration of video ad"
    )
    
    # Audio ads
    audio_file = models.FileField(
        upload_to='ads/audio/%Y/%m/%d/', 
        blank=True, 
        null=True,
        help_text="Audio file for audio ads (MP3, WAV)"
    )
    audio_duration = models.DurationField(
        blank=True, 
        null=True,
        help_text="Duration of audio ad"
    )
    
    # Carousel ads
    carousel_images = models.JSONField(
        default=list,
        help_text="List of image URLs/paths for carousel ads"
    )
    
    # Rich content for native ads
    content = models.TextField(blank=True, help_text="HTML/content for native ads")
    
    # Brand assets
    brand_name = models.CharField(max_length=100, blank=True)
    brand_logo = models.ImageField(
        upload_to='ads/logos/%Y/%m/%d/', 
        blank=True, 
        null=True
    )
    
    # Call-to-Action
    cta_text = models.CharField(max_length=50, default="Learn More")
    cta_url = models.URLField(blank=True)
    cta_color = models.CharField(max_length=7, default='#007bff')
    
    # Targeting
    locations = models.ManyToManyField(
        'locations.Location', 
        related_name='advertisements'
    )
    target_audience = models.CharField(
        max_length=20, 
        choices=[
            ('all', 'All Users'),
            ('new', 'New Users'),
            ('returning', 'Returning Users'),
            ('premium', 'Premium Users'),
        ], 
        default='all'
    )
    
    # Scheduling
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    priority = models.IntegerField(default=1, choices=[(1, 'Low'), (2, 'Medium'), (3, 'High')])
    
    # Budget & Pricing
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bidding_strategy = models.CharField(
        max_length=20,
        choices=[
            ('cpc', 'Cost Per Click'),
            ('cpm', 'Cost Per 1000 Impressions'),
            ('fixed', 'Fixed Cost')
        ],
        default='cpc'
    )
    cost_per_click = models.DecimalField(max_digits=8, decimal_places=4, default=0.50)
    cost_per_impression = models.DecimalField(max_digits=8, decimal_places=4, default=0.02)
    
    # Performance Tracking
    impressions = models.BigIntegerField(default=0)
    clicks = models.BigIntegerField(default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Technical
    campaign_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'advertisements'
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['status', 'start_date', 'end_date']),
            models.Index(fields=['ad_type', 'is_active']),
            models.Index(fields=['campaign_id']),
        ]

    def __str__(self):
        return f"{self.title} - {self.get_ad_type_display()}"

    @property
    def is_live(self):
        """Check if ad is currently active and should be shown"""
        if not self.start_date or not self.end_date:
            return False
            
        now = timezone.now()
        is_within_dates = self.start_date <= now <= self.end_date
        has_budget = self.budget == 0 or self.total_spent < self.budget
        return self.status == 'active' and self.is_active and is_within_dates and has_budget

    @property
    def media_assets(self):
        """Get all media assets for this ad type"""
        assets = {}
        
        if self.ad_type in ['banner', 'popup', 'notification', 'native']:
            if self.image:
                assets['primary_image'] = self.image.url
        
        elif self.ad_type == 'video':
            if self.video_file:
                assets['video'] = self.video_file.url
            if self.video_thumbnail:
                assets['thumbnail'] = self.video_thumbnail.url
            assets['duration'] = self.video_duration
        
        elif self.ad_type == 'audio':
            if self.audio_file:
                assets['audio'] = self.audio_file.url
            assets['duration'] = self.audio_duration
        
        elif self.ad_type == 'carousel':
            assets['images'] = self.carousel_images
        
        elif self.ad_type == 'native':
            assets['content'] = self.content
            if self.brand_logo:
                assets['brand_logo'] = self.brand_logo.url
        
        if self.brand_logo and self.ad_type != 'native':
            assets['brand_logo'] = self.brand_logo.url
            
        return assets

    @property
    def supported_media_formats(self):
        """Get supported media formats for this ad type"""
        formats = {
            'banner': ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
            'interstitial': ['image/jpeg', 'image/png', 'image/webp'],
            'popup': ['image/jpeg', 'image/png', 'image/gif'],
            'notification': ['image/jpeg', 'image/png'],
            'video': ['video/mp4', 'video/webm', 'video/ogg'],
            'native': ['image/jpeg', 'image/png', 'text/html'],
            'carousel': ['image/jpeg', 'image/png', 'image/webp'],
            'audio': ['audio/mpeg', 'audio/wav', 'audio/ogg'],
        }
        return formats.get(self.ad_type, [])

    def validate_media_assets(self):
        """Validate that required media assets are present for the ad type"""
        errors = []
        
        if self.ad_type in ['banner', 'popup', 'notification']:
            if not self.image:
                errors.append(f"{self.ad_type} ads require a primary image")
        
        elif self.ad_type == 'video':
            if not self.video_file:
                errors.append("Video ads require a video file")
            if not self.video_thumbnail:
                errors.append("Video ads require a thumbnail image")
        
        elif self.ad_type == 'audio':
            if not self.audio_file:
                errors.append("Audio ads require an audio file")
        
        elif self.ad_type == 'carousel':
            if not self.carousel_images or len(self.carousel_images) < 2:
                errors.append("Carousel ads require at least 2 images")
        
        elif self.ad_type == 'native':
            if not self.content and not self.image:
                errors.append("Native ads require either content or an image")
        
        return errors

    def get_ad_configuration(self):
        """Get ad configuration for frontend rendering"""
        config = {
            'type': self.ad_type,
            'title': self.title,
            'caption': self.caption,
            'cta': {
                'text': self.cta_text,
                'url': self.cta_url,
                'color': self.cta_color,
            },
            'brand': {
                'name': self.brand_name,
                'logo': self.brand_logo.url if self.brand_logo else None,
            },
            'media': self.media_assets,
            'duration': self._get_auto_close_duration(),
        }
        
        # Add type-specific configurations
        if self.ad_type == 'carousel':
            config['carousel_settings'] = {
                'auto_rotate': True,
                'rotation_interval': 5,  # seconds
                'show_indicators': True,
            }
        elif self.ad_type == 'video':
            config['video_settings'] = {
                'autoplay': True,
                'controls': True,
                'muted': True,  # Required for autoplay in many browsers
            }
        elif self.ad_type == 'audio':
            config['audio_settings'] = {
                'autoplay': False,  # Usually don't autoplay audio
                'controls': True,
            }
        
        return config

    def _get_auto_close_duration(self):
        """Get automatic close duration for different ad types"""
        durations = {
            'banner': None,  # No auto-close
            'interstitial': 15,  # 15 seconds
            'popup': 10,  # 10 seconds
            'notification': 5,  # 5 seconds
            'video': None,  # Close after video ends
            'native': None,  # No auto-close
            'carousel': 30,  # 30 seconds for carousel cycle
            'audio': None,  # Close after audio ends or manually
        }
        return durations.get(self.ad_type)

    def record_impression(self):
        """Record an ad impression"""
        self.impressions += 1
        
        # Calculate cost for CPM
        if self.bidding_strategy == 'cpm':
            self.total_spent += self.cost_per_impression / 1000
        
        self.save()

    def record_click(self):
        """Record an ad click"""
        self.clicks += 1
        
        # Calculate cost for CPC
        if self.bidding_strategy == 'cpc':
            self.total_spent += self.cost_per_click
        
        self.save()

    def get_performance_metrics(self):
        """Calculate performance metrics"""
        ctr = (self.clicks / self.impressions * 100) if self.impressions > 0 else 0
        
        return {
            'impressions': self.impressions,
            'clicks': self.clicks,
            'click_through_rate': round(ctr, 2),
            'total_spent': self.total_spent,
            'remaining_budget': max(0, self.budget - self.total_spent),
            'cost_per_click_actual': (self.total_spent / self.clicks) if self.clicks > 0 else 0,
        }

    def can_show_to_user(self, user=None, location=None):
        """Basic targeting check"""
        if not self.is_live:
            return False
        
        # Location targeting
        if location and self.locations.exists():
            if location not in self.locations.all():
                return False
        
        # Audience targeting
        if user and hasattr(user, 'client_profile'):
            client = user.client_profile
            
            if self.target_audience == 'new' and client.total_spent > 0:
                return False
            elif self.target_audience == 'returning' and client.total_spent == 0:
                return False
            elif self.target_audience == 'premium' and client.account_tier != 'premium':
                return False
        
        return True

    def clean(self):
        """Model validation"""
        from django.core.exceptions import ValidationError
        
        # Validate date range
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError('End date must be after start date')
        
        # Require end_date for active ads
        if self.status == 'active' and not self.end_date:
            raise ValidationError('End date is required for active ads')
        
        # Validate budget
        if self.budget < 0:
            raise ValidationError('Budget cannot be negative')
        
        # Validate media assets for ad type
        if self.status == 'active':
            errors = self.validate_media_assets()
            if errors:
                raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        """Custom save with validation"""
        self.full_clean()  # Run model validation
        super().save(*args, **kwargs)


class AdMedia(models.Model):
    """Separate model for managing ad media assets"""
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE, related_name='media_files')
    file = models.FileField(upload_to='ads/media/%Y/%m/%d/')
    media_type = models.CharField(max_length=20, choices=[
        ('image', 'Image'),
        ('video', 'Video'), 
        ('audio', 'Audio'),
        ('document', 'Document'),
    ])
    format = models.CharField(max_length=10)
    file_size = models.BigIntegerField(help_text="File size in bytes")
    duration = models.DurationField(blank=True, null=True, help_text="For video/audio files")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ad_media'
    
    def __str__(self):
        return f"{self.media_type} - {self.advertisement.title}"