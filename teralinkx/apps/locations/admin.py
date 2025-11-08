# apps/locations/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Location

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = [
        'code', 
        'name', 
        'location_type', 
        'city', 
        'is_active',
        'max_concurrent_users',
        'roaming_status',
        'created_display'
    ]
    
    list_filter = [
        'location_type',
        'is_active',
        'allow_roaming_in',
        'allow_roaming_out',
        'city'
    ]
    
    search_fields = [
        'code',
        'name', 
        'city',
        'address',
        'nas_identifier'
    ]
    
    readonly_fields = [
        'created_display',
        'modified_display',
        'roaming_locations_list'
    ]
    
    fieldsets = (
        ('Core Information', {
            'fields': (
                'code', 
                'name', 
                'location_type',
                'is_active'
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
                'router_ip',
                'nas_identifier',
                'max_concurrent_users'
            )
        }),
        ('Roaming Settings', {
            'fields': (
                'allow_roaming_in',
                'allow_roaming_out', 
                'roaming_price_multiplier',
                'roaming_locations_list'
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
    disable_roaming.short_description = "Disable roaming for selected locations"