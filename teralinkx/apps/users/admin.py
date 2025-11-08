from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import ClientH, UserDevice, UserSession  # Added UserSession

class ClientHInline(admin.StackedInline):
    """Inline admin for ClientH profile"""
    model = ClientH
    can_delete = False
    verbose_name_plural = 'Client Profile'
    fk_name = 'user'
    fieldsets = (
        ('Account Information', {
            'fields': ('account', 'account_tier', 'status', 'balance', 'credit_limit')
        }),
        ('Location Information', {
            'fields': ('home_location', 'current_location', 'last_location_update')
        }),
        ('Security Settings', {
            'fields': ('two_factor_enabled', 'failed_login_attempts')  # Removed security_notifications
        }),
        ('Preferences', {
            'fields': ('auto_renew',)  # Removed language, timezone, marketing_emails
        }),
    )

class UserAdmin(BaseUserAdmin):
    """Enhanced User admin with ClientH profile"""
    inlines = (ClientHInline,)
    list_display = ('username', 'email', 'get_account', 'get_account_tier', 'get_status', 'is_staff', 'last_login', 'get_active_sessions')
    list_select_related = ('client_profile',)
    
    def get_account(self, instance):
        return instance.client_profile.account if hasattr(instance, 'client_profile') else 'N/A'
    get_account.short_description = 'Account'
    
    def get_account_tier(self, instance):
        if hasattr(instance, 'client_profile'):
            return instance.client_profile.get_account_tier_display()
        return 'N/A'
    get_account_tier.short_description = 'Account Tier'
    
    def get_status(self, instance):
        if hasattr(instance, 'client_profile'):
            status = instance.client_profile.status
            colors = {
                'active': 'green',
                'suspended': 'orange',
                'inactive': 'gray',
                'banned': 'red'
            }
            color = colors.get(status, 'gray')
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color, status.upper()
            )
        return 'N/A'
    get_status.short_description = 'Status'
    
    def get_active_sessions(self, instance):
        if hasattr(instance, 'client_profile'):
            return instance.client_profile.active_sessions.count()
        return 0
    get_active_sessions.short_description = 'Active Sessions'
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

@admin.register(ClientH)
class ClientHAdmin(admin.ModelAdmin):
    list_display = ('account', 'user', 'display_name', 'account_tier_badge', 'status_badge', 'balance', 'available_credit', 'active_sessions_count', 'connected_devices_count', 'home_location')
    list_filter = ('account_tier', 'status', 'home_location', 'two_factor_enabled', 'created_at')
    search_fields = ('account', 'user__username', 'user__email', 'display_name', 'phone_number')
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'last_balance_update', 'last_location_update', 'available_credit', 'is_eligible_for_credit', 'current_ip_address', 'current_mac_address')
    raw_id_fields = ('user', 'home_location', 'current_location')
    
    fieldsets = (
        ('User Account', {
            'fields': ('user', 'account', 'display_name', 'phone_number', 'profile_image')  # Removed date_of_birth
        }),
        ('Account Tier & Status', {
            'fields': ('account_tier', 'status')
        }),
        ('Financial Information', {
            'fields': ('balance', 'credit_limit', 'available_credit', 'is_eligible_for_credit', 'total_spent', 'lifetime_data_used')
        }),
        ('Location Information', {
            'fields': ('home_location', 'current_location', 'last_location_update')
        }),
        ('Security Settings', {
            'fields': ('failed_login_attempts', 'two_factor_enabled')  # Removed account_locked_until, security_notifications
        }),
        ('Preferences', {
            'fields': ('auto_renew',)  # Removed language, timezone, marketing_emails
        }),
        ('Network Information', {
            'fields': ('active_voucher', 'voucher_expiry'),  # Removed current_ip_address, current_mac_address
            'classes': ('collapse',)
        }),
        ('Current Session Info (Read-only)', {
            'fields': ('current_ip_address', 'current_mac_address'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('last_login', 'last_balance_update', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def account_tier_badge(self, obj):
        colors = {
            'basic': 'blue',
            'premium': 'purple',
            'business': 'orange',
            'enterprise': 'green'
        }
        color = colors.get(obj.account_tier, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            color, obj.get_account_tier_display().upper()
        )
    account_tier_badge.short_description = 'Tier'
    
    def status_badge(self, obj):
        colors = {
            'active': 'green',
            'suspended': 'orange',
            'inactive': 'gray',
            'banned': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            color, obj.status.upper()
        )
    status_badge.short_description = 'Status'
    
    def available_credit(self, obj):
        return f"KES {obj.available_credit:,.2f}"
    available_credit.short_description = 'Available Credit'
    
    def active_sessions_count(self, obj):
        return obj.active_sessions.count()
    active_sessions_count.short_description = 'Active Sessions'
    
    def connected_devices_count(self, obj):
        return obj.connected_devices.count()
    connected_devices_count.short_description = 'Connected Devices'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'home_location', 'current_location')
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(self.readonly_fields)
        if obj:
            readonly_fields.extend(['user', 'account'])
        return readonly_fields
    
    actions = ['activate_users', 'suspend_users', 'ban_users', 'reset_login_attempts', 'terminate_all_sessions']
    
    def activate_users(self, request, queryset):
        updated = queryset.update(status='active', failed_login_attempts=0)
        self.message_user(request, f'{updated} users activated successfully.')
    activate_users.short_description = "Activate selected users"
    
    def suspend_users(self, request, queryset):
        updated = queryset.update(status='suspended')
        self.message_user(request, f'{updated} users suspended.')
    suspend_users.short_description = "Suspend selected users"
    
    def ban_users(self, request, queryset):
        updated = queryset.update(status='banned')
        self.message_user(request, f'{updated} users banned.')
    ban_users.short_description = "Ban selected users"
    
    def reset_login_attempts(self, request, queryset):
        updated = queryset.update(failed_login_attempts=0)
        self.message_user(request, f'{updated} users login attempts reset.')
    reset_login_attempts.short_description = "Reset login attempts"
    
    def terminate_all_sessions(self, request, queryset):
        for client in queryset:
            client.terminate_all_sessions("Admin action")
        self.message_user(request, f'Sessions terminated for {queryset.count()} users.')
    terminate_all_sessions.short_description = "Terminate all sessions"

@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ('device_name', 'user', 'mac_address', 'device_type', 'status_badge', 'is_online', 'is_trusted', 'current_session_info', 'last_seen')
    list_filter = ('device_type', 'device_platform', 'status', 'is_trusted', 'auto_connect', 'created_at')
    search_fields = ('device_name', 'mac_address', 'user__account', 'user__user__username', 'device_model', 'device_manufacturer')
    readonly_fields = ('created_at', 'updated_at', 'last_seen', 'total_connections', 'is_online', 'current_session')
    raw_id_fields = ('user', 'last_seen_location', 'favorite_location')
    
    fieldsets = (
        ('Device Identity', {
            'fields': ('user', 'mac_address', 'device_name', 'device_type', 'device_platform', 'device_model', 'device_manufacturer')
        }),
        ('Security & Trust', {
            'fields': ('is_trusted', 'status')
        }),
        ('Activity Tracking', {
            'fields': ('last_seen', 'last_seen_location', 'total_connections', 'favorite_location')
        }),
        ('Configuration', {
            'fields': ('auto_connect',)
        }),
        ('Current Session (Read-only)', {
            'fields': ('current_session',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'active': 'green',
            'inactive': 'gray',
            'suspended': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            color, obj.status.upper()
        )
    status_badge.short_description = 'Status'
    
    def is_online(self, obj):
        return obj.is_online
    is_online.boolean = True
    is_online.short_description = 'Online'
    
    def current_session_info(self, obj):
        session = obj.current_session
        if session:
            return format_html(
                '{}<br><small>IP: {}</small>',
                session.location or 'Unknown',
                session.ip_address
            )
        return 'No active session'
    current_session_info.short_description = 'Current Session'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 
            'user__user',
            'last_seen_location',
            'favorite_location'
        )
    
    actions = ['activate_devices', 'suspend_devices', 'mark_as_trusted', 'mark_as_untrusted', 'terminate_sessions']
    
    def activate_devices(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} devices activated.')
    activate_devices.short_description = "Activate selected devices"
    
    def suspend_devices(self, request, queryset):
        updated = queryset.update(status='suspended')
        self.message_user(request, f'{updated} devices suspended.')
    suspend_devices.short_description = "Suspend selected devices"
    
    def mark_as_trusted(self, request, queryset):
        updated = queryset.update(is_trusted=True)
        self.message_user(request, f'{updated} devices marked as trusted.')
    mark_as_trusted.short_description = "Mark as trusted"
    
    def mark_as_untrusted(self, request, queryset):
        updated = queryset.update(is_trusted=False)
        self.message_user(request, f'{updated} devices marked as untrusted.')
    mark_as_untrusted.short_description = "Mark as untrusted"
    
    def terminate_sessions(self, request, queryset):
        for device in queryset:
            session = device.current_session
            if session:
                session.terminate("Admin action")
        self.message_user(request, f'Sessions terminated for {queryset.count()} devices.')
    terminate_sessions.short_description = "Terminate active sessions"

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id_short', 'user_account', 'device_name', 'ip_address', 'location', 'login_time', 'last_activity', 'duration', 'is_active_badge')
    list_filter = ('is_active', 'location', 'login_time')
    search_fields = ('session_id', 'user__account', 'device__device_name', 'ip_address')
    readonly_fields = ('session_id', 'login_time', 'last_activity', 'duration')
    
    def session_id_short(self, obj):
        return obj.session_id[:8] + '...'
    session_id_short.short_description = 'Session ID'
    
    def user_account(self, obj):
        return obj.user.account
    user_account.short_description = 'Account'
    
    def device_name(self, obj):
        return obj.device.device_name
    device_name.short_description = 'Device'
    
    def duration(self, obj):
        return obj.duration
    duration.short_description = 'Duration'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">● Active</span>')
        return format_html('<span style="color: red;">● Inactive</span>')
    is_active_badge.short_description = 'Status'
    
    actions = ['terminate_sessions']
    
    def terminate_sessions(self, request, queryset):
        for session in queryset:
            session.terminate("Admin action")
        self.message_user(request, f'{queryset.count()} sessions terminated.')

# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)