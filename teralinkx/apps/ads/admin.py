# apps/ads/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Advertisement, AdMedia

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = [
        'title', 
        'ad_type',
        'status',
        'campaign_name',
        'is_active',
        'start_date',
        'end_date',
        'impressions',
        'clicks',
        'ctr_display',
        'total_spent'
    ]
    
    list_filter = [
        'ad_type',
        'status',
        'is_active',
        'target_audience',
        'bidding_strategy',
        'start_date',
        'end_date'
    ]
    
    search_fields = [
        'title',
        'campaign_name',
        'campaign_id',
        'brand_name'
    ]
    
    readonly_fields = [
        'campaign_id',
        'impressions',
        'clicks',
        'total_spent',
        'ctr_calculated',
        'created_at_display',
        'is_live_display'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title',
                'caption',
                'ad_type',
                'status',
                'campaign_name',
                'campaign_id',
                'is_active'
            )
        }),
        ('Media Assets', {
            'fields': (
                'image',
                'video_file',
                'video_thumbnail',
                'video_duration',
                'audio_file',
                'audio_duration',
                'carousel_images',
                'content',
                'brand_logo'
            )
        }),
        ('Brand & Call-to-Action', {
            'fields': (
                'brand_name',
                'cta_text',
                'cta_url',
                'cta_color'
            )
        }),
        ('Targeting', {
            'fields': (
                'locations',
                'target_audience'
            )
        }),
        ('Scheduling', {
            'fields': (
                'start_date',
                'end_date',
                'priority'
            )
        }),
        ('Budget & Pricing', {
            'fields': (
                'budget',
                'bidding_strategy',
                'cost_per_click',
                'cost_per_impression',
                'total_spent'
            )
        }),
        ('Performance Metrics', {
            'fields': (
                'impressions',
                'clicks',
                'ctr_calculated'
            )
        }),
        ('Status Information', {
            'fields': (
                'is_live_display',
                'created_at_display'
            ),
            'classes': ('collapse',)
        })
    )
    
    filter_horizontal = ['locations']
    
    actions = [
        'activate_ads',
        'pause_ads',
        'archive_ads'
    ]
    
    def ctr_display(self, obj):
        """Display CTR in list view"""
        ctr = (obj.clicks / obj.impressions * 100) if obj.impressions > 0 else 0
        color = 'green' if ctr > 2 else 'orange' if ctr > 0.5 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.2f}%</span>',
            color,
            ctr
        )
    ctr_display.short_description = 'CTR'
    
    def ctr_calculated(self, obj):
        """Calculate and display CTR in detail view"""
        ctr = (obj.clicks / obj.impressions * 100) if obj.impressions > 0 else 0
        return f"{ctr:.2f}%"
    ctr_calculated.short_description = 'Click-Through Rate'
    
    def created_at_display(self, obj):
        """Format created_at date"""
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")
    created_at_display.short_description = 'Created'
    
    def is_live_display(self, obj):
        """Display live status"""
        if obj.is_live:
            return format_html('<span style="color: green; font-weight: bold;">✓ LIVE</span>')
        else:
            return format_html('<span style="color: red; font-weight: bold;">✗ INACTIVE</span>')
    is_live_display.short_description = 'Live Status'
    
    def activate_ads(self, request, queryset):
        """Admin action to activate ads"""
        updated = queryset.update(status='active', is_active=True)
        self.message_user(request, f'{updated} ads activated successfully.')
    activate_ads.short_description = "Activate selected ads"
    
    def pause_ads(self, request, queryset):
        """Admin action to pause ads"""
        updated = queryset.update(status='paused')
        self.message_user(request, f'{updated} ads paused successfully.')
    pause_ads.short_description = "Pause selected ads"
    
    def archive_ads(self, request, queryset):
        """Admin action to archive ads"""
        updated = queryset.update(status='archived')
        self.message_user(request, f'{updated} ads archived successfully.')
    archive_ads.short_description = "Archive selected ads"

@admin.register(AdMedia)
class AdMediaAdmin(admin.ModelAdmin):
    list_display = [
        'advertisement',
        'media_type',
        'format',
        'file_size_display',
        'duration_display',
        'created_at'
    ]
    
    list_filter = [
        'media_type',
        'created_at'
    ]
    
    search_fields = [
        'advertisement__title',
        'format'
    ]
    
    readonly_fields = ['created_at']
    
    def file_size_display(self, obj):
        """Display file size in human-readable format"""
        if obj.file_size:
            if obj.file_size < 1024:
                return f"{obj.file_size} B"
            elif obj.file_size < 1024 * 1024:
                return f"{obj.file_size / 1024:.1f} KB"
            else:
                return f"{obj.file_size / (1024 * 1024):.1f} MB"
        return "N/A"
    file_size_display.short_description = 'File Size'
    
    def duration_display(self, obj):
        """Display duration in human-readable format"""
        if obj.duration:
            total_seconds = obj.duration.total_seconds()
            if total_seconds < 60:
                return f"{int(total_seconds)}s"
            else:
                return f"{int(total_seconds // 60)}m {int(total_seconds % 60)}s"
        return "N/A"
    duration_display.short_description = 'Duration'