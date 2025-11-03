from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum, Avg
from .models import Advertisement

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = [
        'title', 
        'ad_type_badge', 
        'status_badge', 
        'priority', 
        'campaign_name',
        'impressions', 
        'clicks', 
        'ctr_display', 
        'performance_score_badge',
        'is_active_badge',
        'days_remaining',
        'created_at'
    ]
    
    list_filter = [
        'ad_type',
        'status', 
        'priority',
        'target_audience',
        'bidding_strategy',
        'location',
        'created_at',
        'start_date',
        'end_date'
    ]
    
    search_fields = [
        'title',
        'campaign_name', 
        'campaign_id',
        'brand_name',
        'caption'
    ]
    
    readonly_fields = [
        'campaign_id',
        'created_at',
        'updated_at',
        'last_shown',
        'impressions',
        'clicks',
        'conversions',
        'unique_users_reached',
        'total_spent',
        'click_through_rate',
        'conversion_rate',
        'performance_score',
        'quality_score',
        'avg_display_time',
        'calculated_ctr',
        'calculated_conversion_rate',
        'is_active',
        'remaining_budget',
        'days_remaining',
        'estimated_reach'
    ]
    
    filter_horizontal = [
        'target_locations',
        'exclude_locations',
        'target_packages'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title',
                'caption', 
                'ad_type',
                'status',
                'campaign_name',
                'campaign_id'
            )
        }),
        
        ('Media Content', {
            'fields': (
                'image',
                'video',
                'thumbnail',
                'carousel_images',
                'logo',
                'brand_name'
            )
        }),
        
        ('Content & Engagement', {
            'fields': (
                'content',
                'cta_text',
                'cta_url', 
                'cta_color'
            )
        }),
        
        ('Scheduling & Priority', {
            'fields': (
                'start_date',
                'end_date',
                'priority',
                'weight'
            )
        }),
        
        ('Budget & Pricing', {
            'fields': (
                'budget',
                'bidding_strategy',
                'cost_per_click',
                'cost_per_impression',
                'cost_per_action',
                'daily_budget',
                'total_spent',
                'remaining_budget'
            )
        }),
        
        ('Advanced Targeting', {
            'fields': (
                'target_audience',
                'target_devices',
                'target_packages',
                'target_locations',
                'exclude_locations',
                'min_user_balance',
                'require_premium'
            )
        }),
        
        ('Frequency Capping', {
            'fields': (
                'max_impressions_per_user',
                'impression_interval',
                'min_time_between_views'
            ),
            'classes': ('collapse',)
        }),
        
        ('Performance Metrics', {
            'fields': (
                'impressions',
                'clicks',
                'conversions',
                'unique_users_reached',
                'click_through_rate',
                'conversion_rate',
                'performance_score',
                'quality_score',
                'avg_display_time',
                'last_shown'
            )
        }),
        
        ('Location & Context', {
            'fields': (
                'location',
                'is_roaming'
            )
        }),
        
        ('Metadata', {
            'fields': (
                'created_by',
                'tags',
                'custom_parameters',
                'notes'
            ),
            'classes': ('collapse',)
        }),
        
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    # Custom methods for list display
    def ad_type_badge(self, obj):
        colors = {
            'banner': 'blue',
            'interstitial': 'purple',
            'popup': 'orange',
            'notification': 'green',
            'video': 'red',
            'native': 'teal',
            'carousel': 'pink'
        }
        color = colors.get(obj.ad_type, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            color, obj.get_ad_type_display()
        )
    ad_type_badge.short_description = 'Type'
    
    def status_badge(self, obj):
        colors = {
            'draft': 'gray',
            'active': 'green',
            'paused': 'orange',
            'expired': 'red',
            'archived': 'darkgray',
            'scheduled': 'blue'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            color, obj.status.upper()
        )
    status_badge.short_description = 'Status'
    
    def ctr_display(self, obj):
        ctr = obj.calculated_ctr
        color = 'green' if ctr > 2 else 'orange' if ctr > 0.5 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.2f}%</span>',
            color, ctr
        )
    ctr_display.short_description = 'CTR'
    
    def performance_score_badge(self, obj):
        score = obj.performance_score
        if score >= 8:
            color = 'green'
            emoji = '🚀'
        elif score >= 6:
            color = 'orange'
            emoji = '👍'
        elif score >= 4:
            color = 'yellow'
            emoji = '😐'
        else:
            color = 'red'
            emoji = '📉'
        
        return format_html(
            '<span style="background-color: {}; color: black; padding: 2px 6px; border-radius: 10px; font-size: 10px;">{} {}/10</span>',
            color, emoji, score
        )
    performance_score_badge.short_description = 'Performance'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: green; color: white; padding: 2px 6px; border-radius: 10px; font-size: 10px;">ACTIVE</span>'
            )
        else:
            return format_html(
                '<span style="background-color: red; color: white; padding: 2px 6px; border-radius: 10px; font-size: 10px;">INACTIVE</span>'
            )
    is_active_badge.short_description = 'Active'
    
    def days_remaining(self, obj):
        days = obj.days_remaining
        if days > 30:
            color = 'green'
        elif days > 7:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} days</span>',
            color, days
        )
    days_remaining.short_description = 'Days Left'
    
    def calculated_ctr(self, obj):
        return f"{obj.calculated_ctr:.2f}%"
    calculated_ctr.short_description = 'Calculated CTR'
    
    def calculated_conversion_rate(self, obj):
        return f"{obj.calculated_conversion_rate:.2f}%"
    calculated_conversion_rate.short_description = 'Calculated CR'
    
    def remaining_budget(self, obj):
        return f"KES {obj.remaining_budget:,.2f}"
    remaining_budget.short_description = 'Remaining Budget'
    
    def estimated_reach(self, obj):
        return f"{obj.estimated_reach:,}"
    estimated_reach.short_description = 'Estimated Reach'
    
    # Actions
    actions = [
        'activate_advertisements',
        'pause_advertisements', 
        'archive_advertisements',
        'duplicate_advertisements',
        'update_performance_scores'
    ]
    
    def activate_advertisements(self, request, queryset):
        """Activate selected advertisements"""
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} advertisements activated successfully.')
    activate_advertisements.short_description = "Activate selected ads"
    
    def pause_advertisements(self, request, queryset):
        """Pause selected advertisements"""
        updated = queryset.update(status='paused')
        self.message_user(request, f'{updated} advertisements paused.')
    pause_advertisements.short_description = "Pause selected ads"
    
    def archive_advertisements(self, request, queryset):
        """Archive selected advertisements"""
        updated = queryset.update(status='archived')
        self.message_user(request, f'{updated} advertisements archived.')
    archive_advertisements.short_description = "Archive selected ads"
    
    def duplicate_advertisements(self, request, queryset):
        """Duplicate selected advertisements"""
        count = 0
        for ad in queryset:
            duplicate = ad.duplicate()
            if duplicate:
                count += 1
        self.message_user(request, f'{count} advertisements duplicated successfully.')
    duplicate_advertisements.short_description = "Duplicate selected ads"
    
    def update_performance_scores(self, request, queryset):
        """Update performance scores for selected advertisements"""
        for ad in queryset:
            ad.update_performance_score()
        self.message_user(request, f'Performance scores updated for {queryset.count()} advertisements.')
    update_performance_scores.short_description = "Update performance scores"
    
    # Custom methods for change view
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(self.readonly_fields)
        if obj:  # editing an existing object
            readonly_fields.extend(['campaign_id', 'created_by'])
        return readonly_fields
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # New object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    # Custom change list view with statistics
    def changelist_view(self, request, extra_context=None):
        # Add statistics to context
        if extra_context is None:
            extra_context = {}
        
        # Calculate overall statistics
        total_ads = Advertisement.objects.count()
        active_ads = Advertisement.objects.filter(status='active').count()
        total_impressions = Advertisement.objects.aggregate(total=Sum('impressions'))['total'] or 0
        total_clicks = Advertisement.objects.aggregate(total=Sum('clicks'))['total'] or 0
        total_revenue = Advertisement.objects.aggregate(total=Sum('total_spent'))['total'] or 0
        
        # Calculate average performance
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        avg_performance = Advertisement.objects.aggregate(avg=Avg('performance_score'))['avg'] or 0
        
        stats = {
            'total_ads': total_ads,
            'active_ads': active_ads,
            'total_impressions': total_impressions,
            'total_clicks': total_clicks,
            'total_revenue': total_revenue,
            'avg_ctr': avg_ctr,
            'avg_performance': avg_performance,
        }
        
        extra_context['ad_stats'] = stats
        return super().changelist_view(request, extra_context=extra_context)
    
    # Inline for performance metrics (optional)
    class PerformanceMetricsInline(admin.TabularInline):
        model = Advertisement
        fields = ['impressions', 'clicks', 'conversions', 'click_through_rate', 'performance_score']
        readonly_fields = ['impressions', 'clicks', 'conversions', 'click_through_rate', 'performance_score']
        can_delete = False
        max_num = 1
        verbose_name = "Performance Metrics"
        verbose_name_plural = "Performance Metrics"
    
    def get_inlines(self, request, obj):
        if obj:  # Only show for existing objects
            return [self.PerformanceMetricsInline]
        return []
    
    # Custom filters
    list_filter = [
        ('ad_type', admin.AllValuesFieldListFilter),
        ('status', admin.AllValuesFieldListFilter),
        ('target_audience', admin.AllValuesFieldListFilter),
        ('bidding_strategy', admin.AllValuesFieldListFilter),
        ('location', admin.RelatedOnlyFieldListFilter),
        ('created_at', admin.DateFieldListFilter),
        ('start_date', admin.DateFieldListFilter),
        ('end_date', admin.DateFieldListFilter),
    ]
    
    # Date hierarchy
    date_hierarchy = 'created_at'
    
    # Preserve filters
    preserve_filters = True
    
    # Show full result count
    show_full_result_count = False
    
    # Custom templates for better UI
    change_list_template = 'admin/ads/advertisement/change_list.html'
    change_form_template = 'admin/ads/advertisement/change_form.html'

class AdvertisementPerformanceFilter(admin.SimpleListFilter):
    """Custom filter for advertisement performance"""
    title = 'Performance'
    parameter_name = 'performance'
    
    def lookups(self, request, model_admin):
        return (
            ('excellent', 'Excellent (8-10)'),
            ('good', 'Good (6-7.9)'),
            ('average', 'Average (4-5.9)'),
            ('poor', 'Poor (0-3.9)'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'excellent':
            return queryset.filter(performance_score__gte=8)
        elif self.value() == 'good':
            return queryset.filter(performance_score__gte=6, performance_score__lt=8)
        elif self.value() == 'average':
            return queryset.filter(performance_score__gte=4, performance_score__lt=6)
        elif self.value() == 'poor':
            return queryset.filter(performance_score__lt=4)
        return queryset

class AdvertisementBudgetFilter(admin.SimpleListFilter):
    """Custom filter for advertisement budget status"""
    title = 'Budget Status'
    parameter_name = 'budget_status'
    
    def lookups(self, request, model_admin):
        return (
            ('healthy', 'Healthy Budget'),
            ('low', 'Low Budget (< 20%)'),
            ('exhausted', 'Budget Exhausted'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'healthy':
            return queryset.filter(total_spent__lt=models.F('budget') * 0.8)
        elif self.value() == 'low':
            return queryset.filter(
                total_spent__gte=models.F('budget') * 0.8,
                total_spent__lt=models.F('budget')
            )
        elif self.value() == 'exhausted':
            return queryset.filter(total_spent__gte=models.F('budget'))
        return queryset

# Add custom filters to the admin
AdvertisementAdmin.list_filter.extend([
    AdvertisementPerformanceFilter,
    AdvertisementBudgetFilter
])