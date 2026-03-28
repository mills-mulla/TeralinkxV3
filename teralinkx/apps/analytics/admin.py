from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import ActiveSession, DataUsageRecord, DHCPLease

@admin.register(ActiveSession)
class ActiveSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'device', 'mac_address', 'ip_address', 'location', 'voucher', 'is_roaming', 'start_time', 'last_update', 'is_active', 'total_bytes', 'uptime_display')
    list_filter = ('is_authenticated', 'is_roaming', 'location', 'start_time')
    search_fields = ('user__account', 'mac_address', 'session_id', 'ip_address', 'nas_identifier')
    readonly_fields = ('created_at', 'updated_at', 'uptime', 'last_update', 'total_bytes_display', 'session_quality_display')
    fieldsets = (
        ('Session Information', {
            'fields': ('session_id', 'user', 'device', 'voucher', 'location', 'is_roaming')
        }),
        ('Network Information', {
            'fields': ('mac_address', 'ip_address', 'nas_ip_address', 'nas_identifier')
        }),
        ('Session Details', {
            'fields': ('start_time', 'last_update', 'uptime', 'is_authenticated')
        }),
        ('Usage Statistics', {
            'fields': ('download_bytes', 'upload_bytes', 'download_speed_bps', 'upload_speed_bps', 'total_bytes_display')
        }),
        ('Session Quality', {
            'fields': ('packet_loss', 'latency_ms', 'session_quality_display')
        }),
        ('Status', {
            'fields': ('terminate_cause', 'terminated_at')
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
    
    def uptime_display(self, obj):
        """Display uptime in human readable format"""
        if obj.uptime:
            total_seconds = obj.uptime.total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
        return "0h 0m"
    uptime_display.short_description = 'Uptime'
    
    def total_bytes_display(self, obj):
        """Display total bytes in human readable format"""
        total = obj.total_bytes
        if total < 1024:
            return f"{total} B"
        elif total < 1024 * 1024:
            return f"{total / 1024:.2f} KB"
        elif total < 1024 * 1024 * 1024:
            return f"{total / (1024 * 1024):.2f} MB"
        else:
            return f"{total / (1024 * 1024 * 1024):.2f} GB"
    total_bytes_display.short_description = 'Total Data Used'
    
    def session_quality_display(self, obj):
        """Display session quality metrics"""
        return format_html(
            '<div style="font-size: 11px;">'
            'Loss: {:.2f}% | Latency: {:.2f}ms'
            '</div>',
            obj.packet_loss,
            obj.latency_ms
        )
    session_quality_display.short_description = 'Quality Metrics'

@admin.register(DataUsageRecord)
class DataUsageRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'device', 'usage_type', 'protocol', 'start_time', 'end_time', 'duration', 'total_bytes', 'average_speed_bps', 'location', 'is_roaming')
    list_filter = ('usage_type', 'protocol', 'is_roaming', 'location', 'start_time')
    search_fields = ('user__account', 'device__device_name', 'destination_domain', 'source_ip', 'destination_ip')
    readonly_fields = ('created_at', 'updated_at', 'total_bytes', 'total_megabytes', 'average_download_speed_display', 'cost_display')
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
    
    def average_download_speed_display(self, obj):
        """Display average download speed in Mbps"""
        speed_mbps = obj.average_download_speed_mbps
        return f"{speed_mbps:.2f} Mbps"
    average_download_speed_display.short_description = 'Avg Speed'
    
    def cost_display(self, obj):
        """Display total cost"""
        return f"KES {obj.total_cost:.2f}"
    cost_display.short_description = 'Cost'

@admin.register(DHCPLease)
class DHCPLeaseAdmin(admin.ModelAdmin):
    list_display = ('mac_address', 'address', 'active_address', 'client', 'server', 'status', 'dhcp_client_id', 'expires_after', 'last_seen', 'age')
    list_filter = ('status', 'server', 'last_seen')
    search_fields = ('mac_address', 'address', 'active_address', 'client__account', 'dhcp_client_id')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Lease Information', {
            'fields': ('idD', 'client', 'address', 'active_address', 'mac_address', 'dhcp_client_id')
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