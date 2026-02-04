# apps/notifications/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Notification, NotificationTemplate


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for Notification model with announcement support"""
    list_display = [
        'title',
        'notification_type_badge',
        'scope_badge',
        'priority_badge',
        'recipient_info',
        'status_badges',
        'expires_info',
        'created_at'
    ]
    
    list_filter = [
        'notification_type',
        'scope',
        'priority',
        'is_persistent',
        'is_sent',
        'is_read',
        'is_archived',
        ('expires_at', admin.DateFieldListFilter),
        'created_at'
    ]
    
    search_fields = [
        'title',
        'message',
        'user__username',
        'client__name'
    ]
    
    readonly_fields = [
        'correlation_id',
        'created_at',
        'updated_at',
        'pusher_channel',
        'pusher_event'
    ]
    
    filter_horizontal = ['target_locations', 'target_packages']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ('title', 'message', 'short_message', 'notification_type', 'priority')
        }),
        ('Recipients & Scope', {
            'fields': ('scope', 'user', 'client', 'is_broadcast', 'target_audience')
        }),
        ('Delivery Settings', {
            'fields': ('channels', 'is_persistent', 'auto_dismiss_seconds', 'scheduled_for', 'expires_at')
        }),
        ('Action & Context', {
            'fields': ('action_url', 'action_text', 'context_data', 'client_context')
        }),
        ('UI Settings', {
            'fields': ('icon', 'badge', 'vibration_pattern')
        }),
        ('Status', {
            'fields': ('is_sent', 'is_read', 'is_archived'),
            'classes': ('collapse',)
        }),
        ('System Fields', {
            'fields': ('correlation_id', 'pusher_channel', 'pusher_event', 'source', 'template_id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    ]
    
    actions = ['mark_as_sent', 'mark_as_read', 'create_announcement', 'send_notification']
    
    def notification_type_badge(self, obj):
        colors = {
            'system': 'blue',
            'billing': 'green',
            'security': 'red',
            'promotional': 'purple',
            'maintenance': 'orange',
            'usage': 'yellow',
            'voucher': 'indigo',
            'announcement': 'pink',
        }
        color = colors.get(obj.notification_type, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            color, obj.get_notification_type_display()
        )
    notification_type_badge.short_description = 'Type'
    
    def scope_badge(self, obj):
        colors = {'user': '#10b981', 'client': '#3b82f6', 'global': '#8b5cf6'}
        color = colors.get(obj.scope, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 8px; font-size: 10px;">{}</span>',
            color, obj.get_scope_display().upper()
        )
    scope_badge.short_description = 'Scope'
    
    def priority_badge(self, obj):
        colors = {'low': '#6b7280', 'medium': '#f59e0b', 'high': '#ef4444', 'urgent': '#dc2626'}
        color = colors.get(obj.priority, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 8px; font-size: 10px;">{}</span>',
            color, obj.priority.upper()
        )
    priority_badge.short_description = 'Priority'
    
    def recipient_info(self, obj):
        if obj.scope == 'global':
            return format_html('<strong>🌍 Global</strong>')
        elif obj.user:
            return format_html('👤 {}', obj.user.username)
        elif obj.client:
            return format_html('🏢 {}', obj.client.name)
        return '❓ Unknown'
    recipient_info.short_description = 'Recipient'
    
    def status_badges(self, obj):
        badges = []
        if obj.is_sent:
            badges.append('<span style="background-color: #10b981; color: white; padding: 1px 4px; border-radius: 4px; font-size: 9px;">SENT</span>')
        if obj.is_read:
            badges.append('<span style="background-color: #3b82f6; color: white; padding: 1px 4px; border-radius: 4px; font-size: 9px;">READ</span>')
        if obj.is_persistent:
            badges.append('<span style="background-color: #8b5cf6; color: white; padding: 1px 4px; border-radius: 4px; font-size: 9px;">PERSIST</span>')
        if obj.is_expired:
            badges.append('<span style="background-color: #ef4444; color: white; padding: 1px 4px; border-radius: 4px; font-size: 9px;">EXPIRED</span>')
        return format_html(' '.join(badges)) if badges else '—'
    status_badges.short_description = 'Status'
    
    def expires_info(self, obj):
        if obj.expires_at:
            if obj.is_expired:
                return format_html('<span style="color: #ef4444;">⏰ Expired</span>')
            else:
                return format_html('<span style="color: #f59e0b;">⏰ {}</span>', obj.expires_at.strftime('%m/%d %H:%M'))
        return '♾️ Never'
    expires_info.short_description = 'Expires'
    
    def mark_as_sent(self, request, queryset):
        updated = queryset.update(is_sent=True, sent_at=timezone.now())
        self.message_user(request, f'{updated} notifications marked as sent.')
    mark_as_sent.short_description = 'Mark selected as sent'
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True, read_at=timezone.now())
        self.message_user(request, f'{updated} notifications marked as read.')
    mark_as_read.short_description = 'Mark selected as read'
    
    def create_announcement(self, request, queryset):
        """Quick action to create announcements"""
        for notification in queryset:
            Notification.objects.create(
                title=f"📢 {notification.title}",
                message=notification.message,
                notification_type='announcement',
                scope='global',
                priority='medium',
                channels=['in_app', 'pusher'],
                is_persistent=True,
                expires_at=timezone.now() + timezone.timedelta(days=7)
            )
        self.message_user(request, f'{queryset.count()} announcements created.')
    create_announcement.short_description = 'Convert to global announcements'
    
    def send_notification(self, request, queryset):
        sent_count = 0
        for notification in queryset:
            if notification.deliver():
                sent_count += 1
        self.message_user(request, f'{sent_count} notifications sent successfully.')
    send_notification.short_description = 'Send selected notifications'


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    """Admin interface for NotificationTemplate model"""
    list_display = [
        'name',
        'template_type_badge',
        'notification_type_badge',
        'active_status',
        'persistence_info',
        'created_at'
    ]
    
    list_filter = [
        'template_type',
        'notification_type',
        'is_active',
        'default_persistent'
    ]
    
    search_fields = [
        'name',
        'subject',
        'message_template'
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at'
    ]
    
    fieldsets = [
        ('Template Information', {
            'fields': ('name', 'template_type', 'notification_type', 'is_active')
        }),
        ('Content Templates', {
            'fields': ('subject', 'message_template', 'short_template', 'pusher_template')
        }),
        ('Default Settings', {
            'fields': ('default_priority', 'default_channels', 'default_persistent', 'default_auto_dismiss')
        }),
        ('UI Defaults', {
            'fields': ('default_icon', 'default_badge')
        }),
        ('Variables', {
            'fields': ('available_variables',)
        })
    ]
    
    def template_type_badge(self, obj):
        colors = {
            'email': '#ef4444',
            'sms': '#10b981',
            'push': '#3b82f6',
            'in_app': '#8b5cf6',
            'pusher': '#f59e0b',
            'alert': '#ec4899'
        }
        color = colors.get(obj.template_type, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 8px; font-size: 10px;">{}</span>',
            color, obj.get_template_type_display()
        )
    template_type_badge.short_description = 'Type'
    
    def notification_type_badge(self, obj):
        colors = {
            'system': 'blue',
            'billing': 'green',
            'security': 'red',
            'promotional': 'purple',
            'maintenance': 'orange',
            'usage': 'yellow',
            'voucher': 'indigo',
            'announcement': 'pink',
        }
        color = colors.get(obj.notification_type, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            color, obj.get_notification_type_display()
        )
    notification_type_badge.short_description = 'For'
    
    def active_status(self, obj):
        if obj.is_active:
            return format_html('<span style="color: #10b981;">✅ Active</span>')
        return format_html('<span style="color: #ef4444;">❌ Inactive</span>')
    active_status.short_description = 'Status'
    
    def persistence_info(self, obj):
        if obj.default_persistent:
            return format_html('<span style="color: #8b5cf6;">📌 Persistent</span>')
        return format_html('<span style="color: #f59e0b;">⚡ Alert</span>')
    persistence_info.short_description = 'Default Mode'