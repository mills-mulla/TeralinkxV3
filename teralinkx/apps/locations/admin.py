from django.contrib import admin
from django.utils import timezone
from .models import Location, RoamingPolicy

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'location_type', 'pricing_tier', 'is_online', 'current_user_count', 'max_concurrent_users')
    list_filter = ('location_type', 'pricing_tier', 'is_online', 'created_at')
    search_fields = ('id', 'name', 'address')
    readonly_fields = ('created_at', 'updated_at', 'current_user_count', 'last_health_check')
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'location_type', 'timezone')
        }),
        ('Address & Coordinates', {
            'fields': ('address', 'coordinates')
        }),
        ('Network Configuration', {
            'fields': ('network_config',),
            'classes': ('collapse',)
        }),
        ('Business Configuration', {
            'fields': ('business_hours', 'pricing_tier')
        }),
        ('Status & Capacity', {
            'fields': ('max_concurrent_users', 'current_user_count', 'is_online', 'last_health_check')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_available_packages(self, obj):
        packages = obj.get_available_packages()
        return ", ".join([p.name for p in packages[:3]]) + ("..." if packages.count() > 3 else "")
    get_available_packages.short_description = 'Available Packages'

@admin.register(RoamingPolicy)
class RoamingPolicyAdmin(admin.ModelAdmin):
    list_display = ('home_location', 'visiting_location', 'allowed', 'requires_approval', 'speed_limit_mbps', 'billing_rate_multiplier', 'is_active', 'priority')
    list_filter = ('allowed', 'requires_approval', 'auto_approve', 'is_active', 'home_location', 'visiting_location')
    search_fields = ('home_location__name', 'visiting_location__name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Policy Definition', {
            'fields': ('home_location', 'visiting_location', 'priority', 'is_active')
        }),
        ('Access Rules', {
            'fields': ('allowed', 'requires_approval', 'auto_approve')
        }),
        ('Service Limitations', {
            'fields': ('speed_limit_mbps', 'session_time_limit', 'daily_data_limit_mb')
        }),
        ('Pricing', {
            'fields': ('billing_rate_multiplier', 'surcharge_fixed')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Prevent creating policies with same home and visiting locations
        return True
    
    def save_model(self, request, obj, form, change):
        if obj.home_location == obj.visiting_location:
            from django.contrib import messages
            messages.error(request, "Home and visiting locations cannot be the same")
            return
        super().save_model(request, obj, form, change)