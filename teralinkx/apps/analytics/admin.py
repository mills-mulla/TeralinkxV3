from django.contrib import admin
from django.utils import timezone
from .models import ActiveSession, DataUsageRecord, DHCPLease

@admin.register(ActiveSession)
class ActiveSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'mac_address', 'location', 'start_time', 'is_active', 'total_bytes')
    list_filter = ('is_authenticated', 'is_roaming', 'location', 'start_time')
    search_fields = ('user__account', 'mac_address', 'session_id', 'ip_address')
    readonly_fields = ('created_at', 'updated_at', 'uptime', 'last_update')
    fieldsets = (
        ('Session Information', {
            'fields': ('session_id', 'user', 'voucher', 'location', 'is_roaming')
        }),
        ('Network Information', {
            'fields': ('mac_address', 'ip_address', 'nas_ip_address', 'nas_identifier')
        }),
        ('Session Details', {
            'fields': ('start_time', 'last_update', 'uptime')
        }),
        ('Usage Statistics', {
            'fields': ('download_bytes', 'upload_bytes', 'download_speed_bps', 'upload_speed_bps')
        }),
        ('Session Quality', {
            'fields': ('packet_loss', 'latency_ms')
        }),
        ('Status', {
            'fields': ('is_authenticated', 'terminate_cause', 'terminated_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_active(self, obj):
        return obj.is_active
    is_active.boolean = True
    
    def total_bytes(self, obj):
        return f"{obj.total_bytes:,} bytes"
    total_bytes.short_description = 'Total Data'

@admin.register(DataUsageRecord)
class DataUsageRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'usage_type', 'start_time', 'total_bytes', 'duration', 'location')
    list_filter = ('usage_type', 'is_roaming', 'location', 'start_time')
    search_fields = ('user__account', 'device__name', 'destination_domain')
    readonly_fields = ('created_at', 'updated_at', 'total_bytes', 'total_megabytes')
    date_hierarchy = 'start_time'
    
    fieldsets = (
        ('Core Relationships', {
            'fields': ('user', 'device', 'session', 'voucher', 'location', 'is_roaming')
        }),
        ('Usage Metrics', {
            'fields': ('download_bytes', 'upload_bytes', 'total_packets')
        }),
        ('Timing Information', {
            'fields': ('start_time', 'end_time', 'duration')
        }),
        ('Classification', {
            'fields': ('usage_type', 'protocol', 'port')
        }),
        ('Quality Metrics', {
            'fields': ('average_speed_bps', 'peak_speed_bps', 'packet_loss_rate', 'latency_ms')
        }),
        ('Cost Calculation', {
            'fields': ('cost_per_mb', 'total_cost')
        }),
        ('Metadata', {
            'fields': ('source_ip', 'destination_ip', 'destination_domain', 'user_agent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_bytes(self, obj):
        return f"{obj.total_bytes:,} bytes"
    total_bytes.short_description = 'Total Data'

@admin.register(DHCPLease)
class DHCPLeaseAdmin(admin.ModelAdmin):
    list_display = ('mac_address', 'address', 'client', 'server', 'status', 'last_seen')
    list_filter = ('status', 'server', 'last_seen')
    search_fields = ('mac_address', 'address', 'client__account', 'dhcp_client_id')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Lease Information', {
            'fields': ('idD', 'client', 'address', 'mac_address', 'dhcp_client_id')
        }),
        ('Server Details', {
            'fields': ('server', 'dhcp_option', 'address_lists')
        }),
        ('Status & Timing', {
            'fields': ('status', 'expires_after', 'last_seen', 'age')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )