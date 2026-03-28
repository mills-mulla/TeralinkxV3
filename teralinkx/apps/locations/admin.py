# apps/locations/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Location
import json

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = [
        'code', 
        'name', 
        'location_type', 
        'city', 
        'is_active',
        'is_central',
        'is_online',
        'max_concurrent_users',
        'current_user_count',
        'capacity_percentage_display',
        'roaming_status',
        'maintenance_mode',
        'created_display'
    ]
    
    list_filter = [
        'location_type',
        'is_active',
        'is_central',
        'is_online',
        'maintenance_mode',
        'allow_roaming_in',
        'allow_roaming_out',
        'offline_operation_enabled',
        'city'
    ]
    
    search_fields = [
        'code',
        'name', 
        'node_id',
        'city',
        'address',
        'nas_identifier',
        'description'
    ]
    
    readonly_fields = [
        'created_display',
        'modified_display',
        'roaming_locations_list',
        'capacity_percentage_display',
        'is_operational_display',
        'is_overloaded_display',
        'offline_duration_display',
        'router_config_preview'
    ]
    
    fieldsets = (
        ('Core Information', {
            'fields': (
                'code', 
                'name', 
                'location_type',
                'is_active',
                'description',
                'priority'
            )
        }),
        ('Multi-Location Node Identity', {
            'fields': (
                'node_id',
                'is_central',
                'central_api_url',
                'sync_api_key'
            )
        }),
        ('Physical Location', {
            'fields': (
                'address',
                'city',
                'coordinates'
            )
        }),
        ('Network Configuration', {
            'fields': (
                'router_config',
                'router_config_preview',
                'router_ip',
                'nas_identifier'
            )
        }),
        ('Connectivity & Health', {
            'fields': (
                'is_online',
                'last_seen_online',
                'health_check_interval',
                'offline_duration_display'
            )
        }),
        ('Capacity & Performance', {
            'fields': (
                'max_concurrent_users',
                'current_user_count',
                'capacity_percentage_display',
                'bandwidth_limit_mbps',
                'is_operational_display',
                'is_overloaded_display'
            )
        }),
        ('Operational Status', {
            'fields': (
                'maintenance_mode',
                'maintenance_message'
            )
        }),
        ('Roaming Configuration', {
            'fields': (
                'allow_roaming_in',
                'allow_roaming_out', 
                'roaming_price_multiplier',
                'max_roaming_locations',
                'roaming_time_restrictions',
                'roaming_locations_list'
            )
        }),
        ('Offline Operation', {
            'fields': (
                'offline_operation_enabled',
                'offline_credit_limit'
            )
        }),
        ('Metadata', {
            'fields': (
                'created_display',
                'modified_display'
            ),
            'classes': ('collapse',)
        })
    )
    
    actions = [
        'activate_locations',
        'deactivate_locations',
        'enable_roaming',
        'disable_roaming'
    ]
    
    def created_display(self, obj):
        """Format created_at date"""
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")
    created_display.short_description = 'Created'
    
    def modified_display(self, obj):
        """Format modified_at date"""
        return obj.modified_at.strftime("%Y-%m-%d %H:%M:%S")
    modified_display.short_description = 'Last Modified'
    
    def roaming_status(self, obj):
        """Display roaming status with colored indicators"""
        if obj.allow_roaming_in and obj.allow_roaming_out:
            color = 'green'
            text = 'Full Roaming'
        elif obj.allow_roaming_in:
            color = 'orange'
            text = 'Incoming Only'
        elif obj.allow_roaming_out:
            color = 'blue' 
            text = 'Outgoing Only'
        else:
            color = 'red'
            text = 'No Roaming'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            text
        )
    roaming_status.short_description = 'Roaming Status'
    
    def roaming_locations_list(self, obj):
        """Display list of available roaming locations"""
        roaming_locs = obj.get_roaming_locations()
        if not roaming_locs:
            return "No roaming locations available"
        
        locations_list = []
        for loc in roaming_locs:
            locations_list.append(f"• {loc.name} ({loc.code}) - {loc.get_location_type_display()}")
        
        return format_html("<br>".join(locations_list))
    roaming_locations_list.short_description = 'Available Roaming Locations'
    
    def activate_locations(self, request, queryset):
        """Admin action to activate selected locations"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} locations activated successfully.')
    activate_locations.short_description = "Activate selected locations"
    
    def deactivate_locations(self, request, queryset):
        """Admin action to deactivate selected locations"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} locations deactivated successfully.')
    deactivate_locations.short_description = "Deactivate selected locations"
    
    def enable_roaming(self, request, queryset):
        """Admin action to enable roaming for selected locations"""
        updated = queryset.update(allow_roaming_in=True, allow_roaming_out=True)
        self.message_user(request, f'Roaming enabled for {updated} locations.')
    enable_roaming.short_description = "Enable roaming for selected locations"
    
    def disable_roaming(self, request, queryset):
        """Admin action to disable roaming for selected locations"""
        updated = queryset.update(allow_roaming_in=False, allow_roaming_out=False)
        self.message_user(request, f'Roaming disabled for {updated} locations.')
    def capacity_percentage_display(self, obj):
        """Display capacity percentage with color coding"""
        percentage = obj.capacity_percentage
        if percentage > 90:
            color = 'red'
        elif percentage > 75:
            color = 'orange'
        else:
            color = 'green'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color,
            percentage
        )
    capacity_percentage_display.short_description = 'Capacity %'
    
    def is_operational_display(self, obj):
        """Display operational status"""
        if obj.is_operational:
            return format_html('<span style="color: green;">✓ Operational</span>')
        return format_html('<span style="color: red;">✗ Not Operational</span>')
    is_operational_display.short_description = 'Operational'
    
    def is_overloaded_display(self, obj):
        """Display overload status"""
        if obj.is_overloaded:
            return format_html('<span style="color: red;">⚠ Overloaded</span>')
        return format_html('<span style="color: green;">✓ Normal</span>')
    is_overloaded_display.short_description = 'Load Status'
    
    def offline_duration_display(self, obj):
        """Display offline duration if applicable"""
        duration = obj.get_offline_duration()
        if duration:
            hours = duration.total_seconds() / 3600
            return f"{hours:.1f} hours"
        return "Online"
    offline_duration_display.short_description = 'Offline Duration'
    
    def router_config_preview(self, obj):
        """Display router configuration preview"""
        config = obj.get_router_config()
        return format_html(
            '<pre style="background: #f5f5f5; padding: 10px; border-radius: 5px; max-height: 200px; overflow: auto;">{}</pre>',
            json.dumps(config, indent=2)
        )
    router_config_preview.short_description = 'Router Config Preview'