from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import SecurityLog, PhoneOTP, VerificationSession, AuthSession, ISPEquipment, ISPEquipmentLog

@admin.register(SecurityLog)
class SecurityLogAdmin(admin.ModelAdmin):
    list_display = ('action_type', 'action_category', 'user_display', 'severity_badge', 'ip_address', 'location', 'is_suspicious', 'threat_score', 'reviewed', 'resolved', 'created_at')
    list_filter = ('severity', 'action_category', 'action_type', 'is_suspicious', 'reviewed', 'resolved', 'created_at', 'location')
    search_fields = ('user__account', 'ip_address', 'description', 'correlation_id', 'session_id')
    readonly_fields = ('created_at', 'updated_at', 'correlation_id', 'threat_score', 'threat_level_display')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Core Information', {
            'fields': ('user', 'action_type', 'action_category', 'description', 'severity')
        }),
        ('Source Information', {
            'fields': ('ip_address', 'user_agent', 'location')
        }),
        ('Context & Details', {
            'fields': ('details', 'correlation_id', 'session_id'),
            'classes': ('collapse',)
        }),
        ('Threat Intelligence', {
            'fields': ('is_suspicious', 'threat_score', 'threat_level_display', 'reviewed', 'reviewed_by', 'reviewed_at', 'review_notes')
        }),
        ('Resolution', {
            'fields': ('resolved', 'resolved_by', 'resolved_at', 'resolution')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_display(self, obj):
        if obj.user:
            return obj.user.account
        return 'System'
    user_display.short_description = 'User'
    
    def severity_badge(self, obj):
        colors = {
            'info': 'blue',
            'low': 'green', 
            'medium': 'orange',
            'high': 'red',
            'critical': 'purple',
        }
        color = colors.get(obj.severity, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            color, obj.get_severity_display().upper()
        )
    severity_badge.short_description = 'Severity'
    
    def threat_level_display(self, obj):
        """Display threat level with color coding"""
        if obj.threat_score >= 80:
            return format_html('<span style="color: red;">🔴 Critical</span>')
        elif obj.threat_score >= 60:
            return format_html('<span style="color: orange;">🟠 High</span>')
        elif obj.threat_score >= 30:
            return format_html('<span style="color: yellow;">🟡 Medium</span>')
        else:
            return format_html('<span style="color: green;">🟢 Low</span>')
    threat_level_display.short_description = 'Threat Level'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'location', 'reviewed_by', 'resolved_by')
    
    def has_add_permission(self, request):
        # Security logs should only be created by the system, not manually
        return False
    
    def has_change_permission(self, request, obj=None):
        # Allow changes only for review and resolution fields
        return True
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(self.readonly_fields)
        if obj:  # editing an existing object
            readonly_fields.extend(['user', 'action_type', 'action_category', 'ip_address', 'details', 'correlation_id'])
        return readonly_fields
    
    actions = ['mark_as_reviewed', 'mark_as_resolved', 'calculate_threat_scores']
    
    def mark_as_reviewed(self, request, queryset):
        for log in queryset:
            log.mark_as_reviewed(request.user, "Bulk review from admin")
        self.message_user(request, f'{queryset.count()} logs marked as reviewed.')
    mark_as_reviewed.short_description = "Mark selected logs as reviewed"
    
    def mark_as_resolved(self, request, queryset):
        for log in queryset:
            log.mark_as_resolved(request.user, "Bulk resolution from admin")
        self.message_user(request, f'{queryset.count()} logs marked as resolved.')
    mark_as_resolved.short_description = "Mark selected logs as resolved"
    
    def calculate_threat_scores(self, request, queryset):
        for log in queryset:
            log.calculate_threat_score()
        self.message_user(request, f'Threat scores calculated for {queryset.count()} logs.')
    calculate_threat_scores.short_description = "Recalculate threat scores"
    
    def changelist_view(self, request, extra_context=None):
        # Add security dashboard stats to context
        if extra_context is None:
            extra_context = {}
        
        extra_context['security_stats'] = SecurityLog.get_security_dashboard_stats(days=7)
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(PhoneOTP)
class PhoneOTPAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'otp', 'purpose', 'created_at', 'expires_at', 'is_used', 'is_expired_display', 'attempt_count')
    list_filter = ('purpose', 'is_used', 'created_at', 'expires_at')
    search_fields = ('phone_number', 'otp')
    readonly_fields = ('id', 'created_at', 'is_expired_display')
    
    fieldsets = (
        ('OTP Information', {
            'fields': ('phone_number', 'otp', 'purpose')
        }),
        ('Status', {
            'fields': ('is_used', 'attempt_count')
        }),
        ('Timing', {
            'fields': ('created_at', 'expires_at', 'is_expired_display')
        }),
        ('System', {
            'fields': ('id',),
            'classes': ('collapse',)
        })
    )
    
    def is_expired_display(self, obj):
        if obj.is_expired():
            return format_html('<span style="color: red;">✓ Expired</span>')
        return format_html('<span style="color: green;">✗ Valid</span>')
    is_expired_display.short_description = 'Expired'
    
    def has_add_permission(self, request):
        return False  # OTPs should only be created by the system


@admin.register(VerificationSession)
class VerificationSessionAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'session_token', 'next_step', 'is_completed', 'created_at', 'expires_at', 'remaining_time_display')
    list_filter = ('next_step', 'is_completed', 'created_at')
    search_fields = ('phone_number', 'session_token')
    readonly_fields = ('id', 'created_at', 'remaining_time_display')
    
    fieldsets = (
        ('Session Information', {
            'fields': ('phone_number', 'session_token', 'next_step', 'is_completed')
        }),
        ('Timing', {
            'fields': ('created_at', 'expires_at', 'remaining_time_display')
        }),
        ('System', {
            'fields': ('id',),
            'classes': ('collapse',)
        })
    )
    
    def remaining_time_display(self, obj):
        remaining = obj.get_remaining_time()
        if remaining > 0:
            return f"{remaining} seconds"
        return "Expired"
    remaining_time_display.short_description = 'Time Remaining'


@admin.register(AuthSession)
class AuthSessionAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'session_token', 'status', 'auth_method', 'user', 'ip_address', 'created_at', 'expires_at')
    list_filter = ('status', 'auth_method', 'created_at')
    search_fields = ('phone_number', 'session_token', 'auth_token', 'ip_address')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Session Information', {
            'fields': ('phone_number', 'session_token', 'auth_token', 'status', 'auth_method')
        }),
        ('User & Network', {
            'fields': ('user', 'ip_address', 'user_agent')
        }),
        ('Timing', {
            'fields': ('created_at', 'expires_at')
        }),
        ('System', {
            'fields': ('id', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(ISPEquipment)
class ISPEquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'equipment_type', 'vendor', 'model', 'pop', 'role', 'status', 'management_ip', 'utilization_display', 'needs_attention_display')
    list_filter = ('equipment_type', 'vendor', 'role', 'status', 'pop')
    search_fields = ('name', 'model', 'management_ip', 'public_ip')
    readonly_fields = ('created_at', 'updated_at', 'utilization_display', 'needs_attention_display')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'equipment_type', 'vendor', 'model')
        }),
        ('Network Configuration', {
            'fields': ('management_ip', 'public_ip', 'ssh_port', 'api_port')
        }),
        ('Authentication', {
            'fields': ('username', 'password', 'enable_password'),
            'classes': ('collapse',)
        }),
        ('Location & Role', {
            'fields': ('pop', 'rack_position', 'role', 'status')
        }),
        ('Capacity & Performance', {
            'fields': ('max_capacity', 'current_users', 'uplink_speed', 'utilization_display')
        }),
        ('Maintenance', {
            'fields': ('last_backup', 'firmware_version', 'notes')
        }),
        ('Status', {
            'fields': ('needs_attention_display',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def utilization_display(self, obj):
        percentage = obj.utilization_percentage
        if percentage > 85:
            color = 'red'
        elif percentage > 70:
            color = 'orange'
        else:
            color = 'green'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, percentage
        )
    utilization_display.short_description = 'Utilization'
    
    def needs_attention_display(self, obj):
        if obj.needs_attention:
            return format_html('<span style="color: red;">⚠ Needs Attention</span>')
        return format_html('<span style="color: green;">✓ OK</span>')
    needs_attention_display.short_description = 'Status'


@admin.register(ISPEquipmentLog)
class ISPEquipmentLogAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'action', 'user', 'successful', 'created_at')
    list_filter = ('action', 'successful', 'created_at', 'equipment__equipment_type')
    search_fields = ('equipment__name', 'description', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Log Information', {
            'fields': ('equipment', 'action', 'user', 'successful')
        }),
        ('Details', {
            'fields': ('description',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )