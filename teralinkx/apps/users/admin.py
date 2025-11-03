from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import ClientH, UserDevice

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
            'fields': ('two_factor_enabled', 'security_notifications', 'failed_login_attempts')
        }),
        ('Preferences', {
            'fields': ('language', 'timezone', 'marketing_emails', 'auto_renew')
        }),
    )

class UserAdmin(BaseUserAdmin):
    """Enhanced User admin with ClientH profile"""
    inlines = (ClientHInline,)
    list_display = ('username', 'email', 'get_account', 'get_account_tier', 'get_status', 'is_staff', 'last_login')
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
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

@admin.register(ClientH)
class ClientHAdmin(admin.ModelAdmin):
    list_display = ('account', 'user', 'display_name', 'account_tier_badge', 'status_badge', 'balance', 'available_credit', 'home_location', 'is_online')
    list_filter = ('account_tier', 'status', 'home_location', 'two_factor_enabled', 'created_at')
    search_fields = ('account', 'user__username', 'user__email', 'display_name', 'phone_number')
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'last_balance_update', 'last_location_update', 'available_credit', 'is_eligible_for_credit')
    raw_id_fields = ('user', 'home_location', 'current_location')
    
    fieldsets = (
        ('User Account', {
            'fields': ('user', 'account', 'display_name', 'phone_number', 'date_of_birth', 'profile_image')
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
            'fields': (
                'failed_login_attempts', 
                'account_locked_until',
                'two_factor_enabled', 
                'security_notifications'
            )
        }),
        ('Preferences', {
            'fields': ('language', 'timezone', 'marketing_emails', 'auto_renew')
        }),
        ('Network Information', {
            'fields': ('current_ip_address', 'current_mac_address', 'active_voucher', 'voucher_expiry'),
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
    
    def is_online(self, obj):
        """Check if user has recent activity"""
        if obj.last_login:
            return (timezone.now() - obj.last_login) < timedelta(minutes=30)
        return False
    is_online.boolean = True
    is_online.short_description = 'Online'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'home_location', 'current_location')
    
    def get_devices_count(self, obj):
        return obj.devices.count()
    get_devices_count.short_description = 'Devices'
    
    def get_active_devices_count(self, obj):
        return obj.devices.filter(status='active').count()
    get_active_devices_count.short_description = 'Active Devices'
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(self.readonly_fields)
        if obj:  # editing an existing object
            readonly_fields.extend(['user', 'account'])
        return readonly_fields
    
    actions = ['activate_users', 'suspend_users', 'ban_users', 'reset_login_attempts']
    
    def activate_users(self, request, queryset):
        updated = queryset.update(status='active', account_locked_until=None, failed_login_attempts=0)
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
        updated = queryset.update(failed_login_attempts=0, account_locked_until=None)
        self.message_user(request, f'{updated} users login attempts reset.')
    reset_login_attempts.short_description = "Reset login attempts"

@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ('device_name', 'user', 'mac_address', 'device_type', 'status_badge', 'is_online', 'is_primary', 'is_trusted', 'last_seen')
    list_filter = ('device_type', 'device_platform', 'status', 'is_primary', 'is_trusted', 'auto_connect', 'created_at')
    search_fields = ('device_name', 'mac_address', 'user__account', 'user__user__username', 'device_model', 'device_manufacturer')
    readonly_fields = ('created_at', 'updated_at', 'first_seen', 'last_seen', 'total_connections', 'is_online')
    raw_id_fields = ('user', 'last_seen_location', 'favorite_location', 'dhcp_lease')
    
    fieldsets = (
        ('Device Identity', {
            'fields': ('user', 'mac_address', 'device_name', 'device_type', 'device_platform', 'device_model', 'device_manufacturer')
        }),
        ('Network Information', {
            'fields': ('ip_address', 'bound_ip', 'dhcp_lease')
        }),
        ('Security & Trust', {
            'fields': ('is_primary', 'is_trusted', 'trust_level', 'requires_approval', 'status')
        }),
        ('Activity Tracking', {
            'fields': ('first_seen', 'last_seen', 'last_seen_ip', 'last_seen_location', 'total_connections')
        }),
        ('Usage Statistics', {
            'fields': ('total_data_used', 'average_session_duration', 'favorite_location'),
            'classes': ('collapse',)
        }),
        ('Configuration', {
            'fields': ('auto_connect', 'quality_of_service')
        }),
        ('Metadata', {
            'fields': ('user_agent', 'client_identifier', 'notes'),
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
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 
            'user__user',
            'last_seen_location',
            'favorite_location',
            'dhcp_lease'
        )
    
    def user_account(self, obj):
        return obj.user.account
    user_account.short_description = 'Account'
    
    def user_display_name(self, obj):
        return obj.user.display_name or obj.user.user.username
    user_display_name.short_description = 'User Name'
    
    actions = ['activate_devices', 'suspend_devices', 'mark_as_trusted', 'mark_as_untrusted', 'set_as_primary']
    
    def activate_devices(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} devices activated.')
    activate_devices.short_description = "Activate selected devices"
    
    def suspend_devices(self, request, queryset):
        updated = queryset.update(status='suspended')
        self.message_user(request, f'{updated} devices suspended.')
    suspend_devices.short_description = "Suspend selected devices"
    
    def mark_as_trusted(self, request, queryset):
        updated = queryset.update(is_trusted=True, trust_level=3)
        self.message_user(request, f'{updated} devices marked as trusted.')
    mark_as_trusted.short_description = "Mark as trusted"
    
    def mark_as_untrusted(self, request, queryset):
        updated = queryset.update(is_trusted=False, trust_level=1)
        self.message_user(request, f'{updated} devices marked as untrusted.')
    mark_as_untrusted.short_description = "Mark as untrusted"
    
    def set_as_primary(self, request, queryset):
        # First, unset primary for all devices of these users
        from django.db.models import Q
        user_ids = queryset.values_list('user_id', flat=True).distinct()
        UserDevice.objects.filter(user_id__in=user_ids).update(is_primary=False)
        
        # Then set selected devices as primary
        updated = queryset.update(is_primary=True)
        self.message_user(request, f'{updated} devices set as primary.')
    set_as_primary.short_description = "Set as primary device"

# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)