from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import SecurityLog

@admin.register(SecurityLog)
class SecurityLogAdmin(admin.ModelAdmin):
    list_display = ('action_type', 'user_display', 'severity_badge', 'ip_address', 'location', 'created_at', 'is_suspicious', 'resolved')
    list_filter = ('severity', 'action_category', 'is_suspicious', 'resolved', 'reviewed', 'created_at')
    search_fields = ('user__account', 'ip_address', 'description', 'correlation_id')
    readonly_fields = ('created_at', 'updated_at', 'correlation_id', 'threat_score')
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
            'fields': ('is_suspicious', 'threat_score', 'reviewed', 'reviewed_by', 'reviewed_at', 'review_notes')
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
    
    def threat_level(self, obj):
        if obj.threat_score >= 80:
            return format_html('<span style="color: red;">🔴 Critical</span>')
        elif obj.threat_score >= 60:
            return format_html('<span style="color: orange;">🟠 High</span>')
        elif obj.threat_score >= 30:
            return format_html('<span style="color: yellow;">🟡 Medium</span>')
        else:
            return format_html('<span style="color: green;">🟢 Low</span>')
    threat_level.short_description = 'Threat Level'
    
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