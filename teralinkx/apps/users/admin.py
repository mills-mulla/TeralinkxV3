# apps/users/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
import json

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import ClientH, UserDevice, UserSession

User = get_user_model()


class UserDeviceInline(admin.TabularInline):
    """Inline for viewing devices in ClientH admin"""
    model = UserDevice
    extra = 0
    readonly_fields = ('mac_address', 'device_name', 'device_type', 'status', 'last_seen', 'is_trusted', 'view_device')  # ADDED view_device
    fields = ('mac_address', 'device_name', 'device_type', 'status', 'last_seen', 'is_trusted', 'view_device')
    
    def view_device(self, obj):
        if obj.id:
            url = reverse('admin:users_userdevice_change', args=[obj.id])
            return format_html('<a href="{}">View Device</a>', url)
        return "-"
    view_device.short_description = "Actions"
    
    def has_add_permission(self, request, obj=None):
        return False


class UserSessionInline(admin.TabularInline):
    """Inline for viewing sessions in ClientH admin"""
    model = UserSession
    extra = 0
    max_num = 10
    readonly_fields = ('session_id', 'device', 'session_type', 'is_active', 'login_time', 'has_active_voucher', 'view_session')  # ADDED view_session
    fields = ('session_id', 'device', 'session_type', 'is_active', 'login_time', 'has_active_voucher', 'view_session')
    
    def view_session(self, obj):
        if obj.id:
            url = reverse('admin:users_usersession_change', args=[obj.id])
            return format_html('<a href="{}">View Session</a>', url)
        return "-"
    view_session.short_description = "Actions"
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('-login_time')
    
    def has_add_permission(self, request, obj=None):
        return False




@admin.register(ClientH)
class ClientHAdmin(admin.ModelAdmin):
    """Admin interface for ClientH model"""
    list_display = (
        'account', 
        'display_name', 
        'phone_number', 
        'account_tier', 
        'status', 
        'balance_display',
        'reward_points_display',
        'reward_tier_badge',
        'availability_status_badge',
        'active_devices_count',
        'active_sessions_count',
        'last_login',
        'last_seen',
        'view_profile'
    )
    
    list_filter = (
        'status',
        'account_tier',
        'home_location',
        'last_login'
    )
    
    search_fields = (
        'account',
        'display_name',
        'phone_number',
        'user__username',
        'user__email'
    )
    
    readonly_fields = (
        'created_display',
        'modified_display',
        'last_login',
        'last_seen',
        'last_balance_update',
        'last_location_update',
        'availability_status_badge',
        'active_devices_count',
        'active_sessions_count',
        'connected_devices_list',
        'voucher_sessions_list',
        'user_link',
        'is_eligible_for_credit_display',
        'available_credit_display',
        'profile_image_preview',
        'reward_points_display',
        'reward_tier_badge',
        'reward_stats_display'
    )
    
    fieldsets = (
        ('Client Information', {
            'fields': (
                'user_link',
                'account',
                'display_name',
                'phone_number',
                'profile_image',  
                'profile_image_preview',  
            )
        }),
        ('Account Status', {
            'fields': (
                'status',
                'account_tier',
                'balance',
                'credit_limit',
                'total_spent',
                'lifetime_data_used',
                'is_eligible_for_credit_display',
                'available_credit_display'
            )
        }),
        ('Rewards', {
            'fields': (
                'reward_points',
                'reward_tier',
                'total_points_earned',
                'total_points_redeemed',
                'reward_stats_display'
            )
        }),
        ('Security', {
            'fields': (
                'failed_login_attempts',
                'two_factor_enabled',
                'auto_renew'
            )
        }),
        ('Location', {
            'fields': (
                'home_location',
                'current_location',
                'last_location_update'
            )
        }),
        ('Voucher Information', {
            'fields': (
                'active_voucher',
                'voucher_expiry'
            )
        }),
        ('Statistics', {
            'fields': (
                'active_devices_count',
                'active_sessions_count',
                'connected_devices_list',
                'voucher_sessions_list',
                
            )
        }),
        ('Metadata', {
            'fields': (
                'created_display',
                'modified_display',
                'last_login',
                'last_seen',
                'availability_status_badge',
                'last_balance_update'
            )
        })
    )
    
    inlines = [UserDeviceInline, UserSessionInline]
    
    actions = [
        'suspend_accounts',
        'activate_accounts',
        'reset_failed_logins',
        'terminate_all_sessions',
        'update_to_premium_tier',
        'update_to_basic_tier'
    ]
    
    # Custom methods for timestamp fields
    def created_display(self, obj):
        return obj.created.strftime('%Y-%m-%d %H:%M:%S') if obj.created else "-"
    created_display.short_description = "Created"
    
    def modified_display(self, obj):
        return obj.modified.strftime('%Y-%m-%d %H:%M:%S') if obj.modified else "-"
    modified_display.short_description = "Last Modified"
    
    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return "-"
    user_link.short_description = "Django User"
    
    def profile_image_preview(self, obj):
        if obj.profile_image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px; border-radius: 5px; margin-top: 10px;" />', 
                obj.profile_image.url
            )
        return "No image"
    profile_image_preview.short_description = "Profile Image Preview"
    
    def balance_display(self, obj):
        """Display balance with color coding"""
        try:
            balance = float(obj.balance)
            color = 'green' if balance >= 0 else 'red'
            
            return format_html(
                '<span style="color: {}; font-weight: bold;">KES {:,.2f}</span>',
                color, balance
            )
        except Exception as e:
            return format_html('<span style="color: orange; font-weight: bold;">ERROR: {}</span>', str(e))

    balance_display.short_description = "Balance"
    balance_display.admin_order_field = 'balance'
    
    def reward_points_display(self, obj):
        """Display reward points with color coding"""
        points = obj.reward_points
        
        # Color based on points amount
        if points >= 1000:
            color = 'green'
        elif points >= 500:
            color = 'blue'
        elif points >= 100:
            color = 'orange'
        else:
            color = 'gray'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">🏆 {} pts</span>',
            color, points
        )
    reward_points_display.short_description = "Points"
    reward_points_display.admin_order_field = 'reward_points'
    
    def reward_tier_badge(self, obj):
        """Display reward tier with badge"""
        tier_colors = {
            'bronze': '#CD7F32',
            'silver': '#C0C0C0',
            'gold': '#FFD700',
            'platinum': '#E5E4E2'
        }
        tier_icons = {
            'bronze': '🥉',
            'silver': '🥈',
            'gold': '🥇',
            'platinum': '💎'
        }
        
        color = tier_colors.get(obj.reward_tier, 'gray')
        icon = tier_icons.get(obj.reward_tier, '🏅')
        
        return format_html(
            '<span style="color: {}; background: {}20; padding: 2px 8px; border-radius: 10px; font-weight: bold;">{} {}</span>',
            color, color, icon, obj.reward_tier.title()
        )
    reward_tier_badge.short_description = "Tier"
    reward_tier_badge.admin_order_field = 'reward_tier'
    
    def reward_stats_display(self, obj):
        """Display comprehensive reward statistics"""
        next_tier_points = obj.next_tier_points
        progress = obj.tier_progress_percentage
        
        return format_html(
            '''
            <div style="padding: 10px; background: #f5f5f5; border-radius: 5px; font-size: 12px;">
                <strong>Reward Statistics:</strong><br>
                • Current Points: <span style="color: green; font-weight: bold;">{}</span><br>
                • Total Earned: <span style="color: blue;">{}</span><br>
                • Total Redeemed: <span style="color: red;">{}</span><br>
                • Current Tier: <span style="font-weight: bold;">{}</span><br>
                • Tier Progress: <span style="color: orange;">{:.1f}%</span><br>
                • Points to Next Tier: <span style="color: purple;">{}</span>
            </div>
            ''',
            obj.reward_points,
            obj.total_points_earned,
            obj.total_points_redeemed,
            obj.reward_tier.title(),
            progress,
            next_tier_points if next_tier_points > 0 else 'Max Tier Reached'
        )
    reward_stats_display.short_description = "Reward Statistics"
    
    def active_devices_count(self, obj):
        count = obj.devices.filter(status='active').count()
        max_allowed = obj.get_max_allowed_devices()
        color = "green" if count < max_allowed else "orange" if count == max_allowed else "red"
        return format_html(
            '<span style="color: {};">{}/{} devices</span>',
            color, count, max_allowed
        )
    active_devices_count.short_description = "Active Devices"
    
    def active_sessions_count(self, obj):
        count = obj.sessions.filter(is_active=True).count()
        color = "green" if count > 0 else "gray"
        return format_html('<span style="color: {};">{} sessions</span>', color, count)
    active_sessions_count.short_description = "Active Sessions"
    
    def connected_devices_list(self, obj):
        devices = obj.connected_devices
        if devices:
            links = []
            for device in devices:
                url = reverse('admin:users_userdevice_change', args=[device.id])
                links.append(f'<a href="{url}">{device.device_name}</a>')
            return format_html(', '.join(links))
        return "No connected devices"
    connected_devices_list.short_description = "Currently Connected Devices"
    
    def voucher_sessions_list(self, obj):
        sessions = obj.get_active_voucher_sessions()
        if sessions:
            links = []
            for session in sessions:
                url = reverse('admin:users_usersession_change', args=[session.id])
                time_remaining = ""
                if session.voucher_expires:
                    remaining = session.voucher_expires - timezone.now()
                    if remaining.days > 0:
                        time_remaining = f" ({remaining.days}d remaining)"
                    else:
                        hours = remaining.seconds // 3600
                        minutes = (remaining.seconds % 3600) // 60
                        time_remaining = f" ({hours}h {minutes}m remaining)"
                
                links.append(f'<a href="{url}">{session.active_voucher} - {session.device.device_name}{time_remaining}</a>')
            return format_html('<br>'.join(links))
        return "No active voucher sessions"
    voucher_sessions_list.short_description = "Active Voucher Sessions"
    
    def session_statistics(self, obj):
        """Display session statistics"""
        try:
            stats = obj.get_session_statistics()
            
            # Format the statistics
            html = f'''
            <div style="padding: 10px; background: #f5f5f5; border-radius: 5px; font-size: 12px;">
                <strong>Session Statistics:</strong><br>
                • Total Active Sessions: {stats['total_active_sessions']}<br>
                • Unique Devices: {stats['unique_devices']}<br>
                • Unique Locations: {stats['unique_locations']}<br>
                • Voucher Sessions: {stats['voucher_sessions']}<br>
                • Owner Sessions: {stats['owner_sessions']}<br>
                • Transferred Sessions: {stats['transferred_sessions']}<br>
                • Total Data Used: {round(stats['total_data_used'] / (1024 * 1024), 2)} MB
            </div>
            '''
            
            # Handle oldest/newest sessions
            if stats['oldest_session']:
                html += f'''
                <div style="margin-top: 10px; padding: 10px; background: #e8f5e9; border-radius: 5px; font-size: 12px;">
                    <strong>Oldest Session:</strong> {stats['oldest_session'].session_id[:8]} - 
                    Started: {stats['oldest_session'].login_time.strftime('%Y-%m-%d %H:%M')}<br>
                    <strong>Newest Session:</strong> {stats['newest_session'].session_id[:8]} - 
                    Started: {stats['newest_session'].login_time.strftime('%Y-%m-%d %H:%M')}
                </div>
                '''
            
            return format_html(html)
        except Exception as e:
            return format_html(
                '<div style="padding: 10px; background: #ffebee; border-radius: 5px; color: #c62828;">'
                'Error loading session statistics: {}'
                '</div>',
                str(e)
            )

    session_statistics.short_description = "Session Statistics"
        
    def is_eligible_for_credit_display(self, obj):
        if obj.is_eligible_for_credit:
            return format_html('<span style="color: green;">✓ Eligible</span>')
        return format_html('<span style="color: gray;">✗ Not Eligible</span>')
    is_eligible_for_credit_display.short_description = "Credit Eligible"
    
    def available_credit_display(self, obj):
        credit = obj.available_credit
        return format_html('<span style="color: blue;">KES {:.2f}</span>', float(credit))
    available_credit_display.short_description = "Available Credit"
    
    def availability_status_badge(self, obj):
        status = obj.availability_status
        colors = {
            'online': 'green',
            'recently_active': 'orange', 
            'away': 'gray',
            'offline': 'red',
            'unknown': 'gray'
        }
        icons = {
            'online': '●',
            'recently_active': '◐',
            'away': '◯',
            'offline': '○',
            'unknown': '?'
        }
        color = colors.get(status, 'gray')
        icon = icons.get(status, '?')
        return format_html(
            '<span style="color: {}; background: {}20; padding: 2px 8px; border-radius: 10px;">{} {}</span>',
            color, color, icon, status.replace('_', ' ').title()
        )
    availability_status_badge.short_description = "Availability"
    availability_status_badge.admin_order_field = 'last_seen'
    
    def view_profile(self, obj):
        url = reverse('admin:users_clienth_change', args=[obj.id])
        return format_html('<a href="{}" class="button">View Profile</a>', url)
    view_profile.short_description = "Actions"
    
    def suspend_accounts(self, request, queryset):
        updated = queryset.update(status='suspended')
        self.message_user(request, f"{updated} account(s) suspended.")
    suspend_accounts.short_description = "Suspend selected accounts"
    
    def activate_accounts(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f"{updated} account(s) activated.")
    activate_accounts.short_description = "Activate selected accounts"
    
    def reset_failed_logins(self, request, queryset):
        updated = queryset.update(failed_login_attempts=0)
        self.message_user(request, f"Reset failed login attempts for {updated} account(s).")
    reset_failed_logins.short_description = "Reset failed login attempts"
    
    def terminate_all_sessions(self, request, queryset):
        total_terminated = 0
        for client in queryset:
            terminated = client.terminate_all_sessions(reason="Admin action")
            total_terminated += terminated
        self.message_user(request, f"Terminated {total_terminated} session(s) for {queryset.count()} account(s).")
    terminate_all_sessions.short_description = "Terminate all sessions"
    
    def update_to_premium_tier(self, request, queryset):
        updated = queryset.update(account_tier='premium')
        self.message_user(request, f"{updated} account(s) upgraded to Premium tier.")
    update_to_premium_tier.short_description = "Upgrade to Premium tier"
    
    def update_to_basic_tier(self, request, queryset):
        updated = queryset.update(account_tier='basic')
        self.message_user(request, f"{updated} account(s) downgraded to Basic tier.")
    update_to_basic_tier.short_description = "Downgrade to Basic tier"


@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    """Admin interface for UserDevice model"""
    list_display = (
        'mac_address',
        'device_name',
        'owner_link',
        'device_type',
        'status_badge',
        'is_trusted_badge',
        'is_online_badge',
        'has_active_voucher_badge',
        'total_connections',
        'last_seen',
        'view_device'
    )
    
    list_filter = (
        'status',
        'device_type',
        'device_platform',
        'is_trusted',
        'user__account_tier',
        'last_seen'
    )
    
    search_fields = (
        'mac_address',
        'device_name',
        'device_model',
        'device_manufacturer',
        'user__account',
        'user__display_name',
        'user__phone_number'
    )
    
    readonly_fields = (
        'created_display',  
        'modified_display',  
        'total_connections',
        'is_online_badge',
        'has_active_voucher_badge',
        'active_voucher_session_link',
        'concurrent_sessions_count',
        'can_create_session_badge',
        'previous_owners_display',
        'connection_statistics',
        'current_session_link',
        'view_sessions',
        'owner_link',  
        'device_identification_display', 
    )
    
    fieldsets = (
        ('Device Information', {
            'fields': (
                'user',
                'mac_address',
                'device_name',
                'device_type',
                'device_platform',
                'device_model',
                'device_manufacturer'
            )
        }),
        ('Status & Configuration', {
            'fields': (
                'status',
                'is_trusted',
                'auto_connect',
                'max_concurrent_sessions'
            )
        }),
        ('Location', {
            'fields': (
                'last_seen_location',
                'favorite_location'
            )
        }),
        ('Activity', {
            'fields': (
                'last_seen',
                'total_connections',
                'is_online_badge',
                'current_session_link',
                'concurrent_sessions_count',
                'can_create_session_badge'
            )
        }),
        ('Vouchers', {
            'fields': (
                'has_active_voucher_badge',
                'active_voucher_session_link'
            )
        }),
        ('History', {
            'fields': (
                'previous_owners_display',
                'device_identification'
            )
        }),
        ('Statistics', {
            'fields': (
                'connection_statistics',
                'view_sessions'
            )
        }),
        ('Metadata', {
            'fields': (
                'created_display',  
                'modified_display'  
            )
        })
    )
    
    actions = [
        'trust_devices',
        'untrust_devices',
        'block_devices',
        'unblock_devices',
        'transfer_devices'
    ]
    
    # ADD THESE CUSTOM METHODS FOR TIMESTAMP FIELDS:
    def created_display(self, obj):
        return obj.created.strftime('%Y-%m-%d %H:%M:%S') if obj.created else "-"
    created_display.short_description = "Created"
    
    def modified_display(self, obj):
        return obj.modified.strftime('%Y-%m-%d %H:%M:%S') if obj.modified else "-"
    modified_display.short_description = "Last Modified"
    
    def owner_link(self, obj):
        if obj.user:
            url = reverse('admin:users_clienth_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.account)
        return "-"
    owner_link.short_description = "Owner"
    owner_link.admin_order_field = 'user__account'
    
    def status_badge(self, obj):
        colors = {
            'active': 'green',
            'inactive': 'gray',
            'suspended': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; background: {}20; padding: 2px 8px; border-radius: 10px;">{}</span>',
            color, color, obj.get_status_display()
        )
    status_badge.short_description = "Status"
    
    def is_trusted_badge(self, obj):
        if obj.is_trusted:
            return format_html(
                '<span style="color: green; background: #e8f5e9; padding: 2px 8px; border-radius: 10px;">✓ Trusted</span>'
            )
        return format_html(
            '<span style="color: gray; background: #f5f5f5; padding: 2px 8px; border-radius: 10px;">✗ Not Trusted</span>'
        )
    is_trusted_badge.short_description = "Trusted"
    
    def is_online_badge(self, obj):
        if obj.is_online:
            return format_html(
                '<span style="color: green; background: #e8f5e9; padding: 2px 8px; border-radius: 10px; animation: pulse 2s infinite;">● Online</span>'
            )
        return format_html(
            '<span style="color: gray; background: #f5f5f5; padding: 2px 8px; border-radius: 10px;">● Offline</span>'
        )
    is_online_badge.short_description = "Online Status"
    
    def has_active_voucher_badge(self, obj):
        if obj.has_active_voucher:
            return format_html(
                '<span style="color: green; background: #e8f5e9; padding: 2px 8px; border-radius: 10px;">✓ Voucher</span>'
            )
        return format_html(
            '<span style="color: gray; background: #f5f5f5; padding: 2px 8px; border-radius: 10px;">✗ No Voucher</span>'
        )
    has_active_voucher_badge.short_description = "Voucher"
    
    def active_voucher_session_link(self, obj):
        session = obj.active_voucher_session
        if session:
            url = reverse('admin:users_usersession_change', args=[session.id])
            time_remaining = ""
            if session.voucher_expires:
                remaining = session.voucher_expires - timezone.now()
                if remaining.days > 0:
                    time_remaining = f" ({remaining.days}d remaining)"
                else:
                    hours = remaining.seconds // 3600
                    minutes = (remaining.seconds % 3600) // 60
                    time_remaining = f" ({hours}h {minutes}m remaining)"
            
            return format_html(
                '<a href="{}"><span style="color: blue;">{} - {}</span>{}</a>', 
                url, 
                session.active_voucher,
                session.device.device_name,
                time_remaining
            )
        return "-"
    active_voucher_session_link.short_description = "Active Voucher Session"
    
    def current_session_link(self, obj):
        session = obj.current_session
        if session:
            url = reverse('admin:users_usersession_change', args=[session.id])
            duration = session.duration
            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60
            
            duration_str = ""
            if duration.days > 0:
                duration_str = f" ({duration.days}d {hours}h)"
            elif hours > 0:
                duration_str = f" ({hours}h {minutes}m)"
            else:
                duration_str = f" ({minutes}m)"
            
            return format_html(
                '<a href="{}"><span style="color: {};">{}</span>{}</a>', 
                url,
                "green" if session.is_active else "gray",
                session.session_type.title(),
                duration_str
            )
        return "No active session"
    current_session_link.short_description = "Current Session"
    
    def can_create_session_badge(self, obj):
        if obj.can_create_session:
            return format_html(
                '<span style="color: green; background: #e8f5e9; padding: 2px 8px; border-radius: 10px;">✓ Can Create ({}/{})</span>',
                obj.concurrent_sessions_count, obj.max_concurrent_sessions
            )
        return format_html(
            '<span style="color: red; background: #ffebee; padding: 2px 8px; border-radius: 10px;">✗ Limit Reached ({}/{})</span>',
            obj.concurrent_sessions_count, obj.max_concurrent_sessions
        )
    can_create_session_badge.short_description = "Session Limit"
    
    def previous_owners_display(self, obj):
        if obj.previous_owners:
            owners_html = []
            for owner in obj.previous_owners:
                try:
                    client = ClientH.objects.get(id=owner['user_id'])
                    url = reverse('admin:users_clienth_change', args=[client.id])
                    from_date = owner['from'][:10] if 'from' in owner else 'Unknown'
                    to_date = owner['to'][:10] if 'to' in owner else 'Unknown'
                    reason = owner.get('reason', 'Unknown')
                    owners_html.append(
                        f'<a href="{url}">{client.account}</a> ({from_date} to {to_date}) - {reason}'
                    )
                except ClientH.DoesNotExist:
                    owners_html.append(f'User {owner.get("user_id", "Unknown")} - {owner.get("reason", "Unknown")}')
            return format_html('<br>'.join(owners_html))
        return "No previous owners"
    previous_owners_display.short_description = "Previous Owners"
    
    def device_identification_display(self, obj):
        if obj.device_identification:
            formatted = json.dumps(obj.device_identification, indent=2)
            return format_html(
                '<pre style="background: #f5f5f5; padding: 10px; border-radius: 5px; max-height: 200px; overflow: auto;">{}</pre>', 
                formatted
            )
        return "No identification data"
    device_identification_display.short_description = "Device Identification"
    
    def connection_statistics(self, obj):
        stats = obj.get_connection_statistics(days=30)
        return format_html(
            '''
            <div style="padding: 10px; background: #f5f5f5; border-radius= 5px; font-size: 12px;">
                <strong>30-Day Statistics:</strong><br>
                • Total Sessions: {}<br>
                • Average Duration: {}<br>
                • Unique Locations: {}<br>
                • Voucher Sessions: {}<br>
                • Data Used: {} MB<br>
                • Total Connections: {}
            </div>
            ''',
            stats['total_sessions'],
            str(stats['average_duration']).split('.')[0],
            stats['unique_locations'],
            stats['voucher_sessions'],
            round(stats['total_data_used'] / (1024 * 1024), 2),
            obj.total_connections
        )
    connection_statistics.short_description = "Connection Statistics"
    
    def view_sessions(self, obj):
        url = reverse('admin:users_usersession_changelist') + f'?device__id__exact={obj.id}'
        count = obj.sessions.count()
        return format_html('<a href="{}">View All Sessions ({})</a>', url, count)
    view_sessions.short_description = "Sessions"
    
    def view_device(self, obj):
        url = reverse('admin:users_userdevice_change', args=[obj.id])
        return format_html('<a href="{}" class="button">View</a>', url)
    view_device.short_description = "Actions"
    
    def trust_devices(self, request, queryset):
        updated = queryset.update(is_trusted=True)
        self.message_user(request, f"{updated} device(s) marked as trusted.")
    trust_devices.short_description = "Mark as trusted"
    
    def untrust_devices(self, request, queryset):
        updated = queryset.update(is_trusted=False)
        self.message_user(request, f"{updated} device(s) marked as untrusted.")
    untrust_devices.short_description = "Mark as untrusted"
    
    def block_devices(self, request, queryset):
        total_terminated = 0
        for device in queryset:
            terminated = device.block_device(reason="Admin action")
            total_terminated += terminated
        self.message_user(request, f"Blocked {queryset.count()} device(s), terminated {total_terminated} session(s).")
    block_devices.short_description = "Block selected devices"
    
    def unblock_devices(self, request, queryset):
        for device in queryset:
            device.unblock_device(reason="Admin request")
        self.message_user(request, f"Unblocked {queryset.count()} device(s).")
    unblock_devices.short_description = "Unblock selected devices"
    
    def transfer_devices(self, request, queryset):
        from django.http import HttpResponseRedirect
        
        device_ids = list(queryset.values_list('id', flat=True))
        request.session['transfer_device_ids'] = device_ids
        request.session['transfer_device_count'] = len(device_ids)
        
        return HttpResponseRedirect(reverse('admin:users_clienth_changelist') + '?transfer=select')
    transfer_devices.short_description = "Transfer to another user"


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """Admin interface for UserSession model"""
    list_display = (
        'session_id_short',
        'user_link',
        'device_link',
        'session_type_badge',
        'is_active_badge',
        'is_owner_badge',
        'has_active_voucher_badge',
        'duration_display',
        'login_time',
        'last_activity',
        'view_session'
    )
    
    list_filter = (
        'is_active',
        'session_type',
        'is_owner',
        'was_transferred',
        'location',
        'login_time'
    )
    
    search_fields = (
        'session_id',
        'user__account',
        'user__display_name',
        'user__phone_number',
        'device__mac_address',
        'device__device_name',
        'active_voucher',
        'ip_address'
    )
    
    readonly_fields = (
        'created_display',  
        'modified_display',  
        'duration_display',
        'is_expired_badge',
        'has_active_voucher_badge',
        'voucher_time_remaining_display',
        'session_summary',
        'request_metadata_display',
        'user_link',  
        'device_link',  
        'data_used_mb',
        'login_time',  
        'last_activity',

    )
    
    fieldsets = (
        ('Session Information', {
            'fields': (
                'session_id',
                'user',
                'device',
                'session_type',
                'is_active',
                'is_owner',
                'was_transferred'
            )
        }),
        ('Network Details', {
            'fields': (
                'ip_address',
                'location'
            )
        }),
        ('Voucher Information', {
            'fields': (
                'active_voucher',
                'voucher_activated',
                'voucher_expires',
                'has_active_voucher_badge',
                'voucher_time_remaining_display'
            )
        }),
        ('Timing', {
            'fields': (
                'duration_display',
                'auto_logout_minutes',
                'is_expired_badge'
            )
        }),
        ('Usage', {
            'fields': (
                'data_used',
                'data_used_mb'
            )
        }),
        ('Request Details', {
            'fields': (
                'request_metadata_display',
            )
        }),
        ('Summary', {
            'fields': (
                'session_summary',
            )
        }),
        ('Metadata', {
            'fields': (
                'created_display',  
                'modified_display',
                'login_time',  
                'last_activity'
            )
        })
    )
    
    actions = [
        'terminate_sessions',
        'extend_sessions',
        'activate_test_voucher',
        'deactivate_vouchers',
        'refresh_sessions'
    ]
    
    # ADD THESE CUSTOM METHODS FOR TIMESTAMP FIELDS:
    def created_display(self, obj):
        return obj.created.strftime('%Y-%m-%d %H:%M:%S') if obj.created else "-"
    created_display.short_description = "Created"
    
    def modified_display(self, obj):
        return obj.modified.strftime('%Y-%m-%d %H:%M:%S') if obj.modified else "-"
    modified_display.short_description = "Last Modified"
    
    def session_id_short(self, obj):
        return format_html('<code>{}</code>', obj.session_id[:12] + "...")
    session_id_short.short_description = "Session ID"
    session_id_short.admin_order_field = 'session_id'
    
    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:users_clienth_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.account)
        return "-"
    user_link.short_description = "Client"
    
    def device_link(self, obj):
        if obj.device:
            url = reverse('admin:users_userdevice_change', args=[obj.device.id])
            return format_html('<a href="{}">{}</a>', url, obj.device.device_name)
        return "-"
    device_link.short_description = "Device"
    
    def session_type_badge(self, obj):
        colors = {
            'web': 'blue',
            'network': 'green',
            'voucher': 'orange'
        }
        color = colors.get(obj.session_type, 'gray')
        return format_html(
            '<span style="color: {}; background: {}20; padding: 2px 8px; border-radius: 10px;">{}</span>',
            color, color, obj.get_session_type_display()
        )
    session_type_badge.short_description = "Type"
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="color: green; background: #e8f5e9; padding: 2px 8px; border-radius: 10px;">● Active</span>'
            )
        return format_html(
            '<span style="color: red; background: #ffebee; padding: 2px 8px; border-radius: 10px;">● Terminated</span>'
        )
    is_active_badge.short_description = "Status"
    
    def is_owner_badge(self, obj):
        if obj.is_owner:
            return format_html(
                '<span style="color: green; background: #e8f5e9; padding: 2px 8px; border-radius: 10px;">✓ Owner</span>'
            )
        return format_html(
            '<span style="color: blue; background: #e3f2fd; padding: 2px 8px; border-radius: 10px;">✗ Borrower</span>'
        )
    is_owner_badge.short_description = "Ownership"
    
    def has_active_voucher_badge(self, obj):
        if obj.has_active_voucher:
            return format_html(
                '<span style="color: green; background: #e8f5e9; padding: 2px 8px; border-radius: 10px;">✓ Voucher</span>'
            )
        return format_html(
            '<span style="color: gray; background: #f5f5f5; padding: 2px 8px; border-radius: 10px;">✗ No Voucher</span>'
        )
    has_active_voucher_badge.short_description = "Voucher"
    
    def duration_display(self, obj):
        duration = obj.duration
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        seconds = duration.seconds % 60
        
        if duration.days > 0:
            return f"{duration.days}d {hours}h"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    duration_display.short_description = "Duration"
    duration_display.admin_order_field = 'login_time'
    
    def voucher_time_remaining_display(self, obj):
        if obj.has_active_voucher:
            remaining = obj.voucher_time_remaining
            hours = remaining.seconds // 3600
            minutes = (remaining.seconds % 3600) // 60
            
            color = "green"
            if remaining.days == 0 and hours < 1:
                color = "orange"
            if remaining.days == 0 and hours == 0 and minutes < 5:
                color = "red"
            
            if remaining.days > 0:
                return format_html(
                    '<span style="color: {};">{}d {}h {}m remaining</span>',
                    color, remaining.days, hours, minutes
                )
            elif hours > 0:
                return format_html('<span style="color: {};">{}h {}m remaining</span>', color, hours, minutes)
            else:
                return format_html('<span style="color: {};">{}m remaining</span>', color, minutes)
        return "No active voucher"
    voucher_time_remaining_display.short_description = "Time Remaining"
    
    def is_expired_badge(self, obj):
        if obj.is_expired:
            return format_html(
                '<span style="color: red; background: #ffebee; padding: 2px 8px; border-radius: 10px;">✓ EXPIRED</span>'
            )
        return format_html(
            '<span style="color: green; background: #e8f5e9; padding: 2px 8px; border-radius: 10px;">✗ Active</span>'
        )
    is_expired_badge.short_description = "Expired"
    
    def data_used_mb(self, obj):
        mb = obj.data_used / (1024 * 1024)
        if mb > 1024:
            return f"{mb/1024:.2f} GB"
        return f"{mb:.2f} MB"
    data_used_mb.short_description = "Data Used"
    
    def request_metadata_display(self, obj):
        if obj.request_metadata:
            formatted = json.dumps(obj.request_metadata, indent=2)
            return format_html(
                '<pre style="background: #f5f5f5; padding: 10px; border-radius: 5px; max-height: 200px; overflow: auto; font-size: 11px; color: black;">{}</pre>', 
                formatted
            )
        return "No metadata"
    request_metadata_display.short_description = "Request Metadata"
    
    def session_summary(self, obj):
        summary = obj.get_session_summary()
        return format_html(
            '''
            <div style="padding: 10px; background: #f5f5f5; border-radius: 5px; font-size: 12px; color: black;">
                <strong>Session Summary:</strong><br>
                • ID: {}<br>
                • Device: {}<br>
                • Location: {}<br>
                • IP: {}<br>
                • Type: {}<br>
                • Owner: {}<br>
                • Transferred: {}<br>
                • Active Voucher: {}<br>
                • Data Used: {}<br>
                • Auto Logout: {} minutes
            </div>
            ''',
            summary['session_id'][:20] + "...",
            summary['device'],
            summary['location'],
            summary['ip_address'],
            summary['session_type'],
            "Yes" if summary['is_owner'] else "No (borrowed)",
            "Yes" if summary['was_transferred'] else "No",
            summary['active_voucher'] or "None",
            self.data_used_mb(obj),
            summary['auto_logout_minutes']
        )
    session_summary.short_description = "Session Summary"
    
    def view_session(self, obj):
        url = reverse('admin:users_usersession_change', args=[obj.id])
        return format_html('<a href="{}" class="button">View</a>', url)
    view_session.short_description = "Actions"
    
    def terminate_sessions(self, request, queryset):
        for session in queryset:
            session.terminate(reason="Admin action")
        self.message_user(request, f"Terminated {queryset.count()} session(s).")
    terminate_sessions.short_description = "Terminate selected sessions"
    
    def extend_sessions(self, request, queryset):
        for session in queryset:
            if session.voucher_expires:
                session.voucher_expires = session.voucher_expires + timedelta(hours=1)
                session.save()
        self.message_user(request, f"Extended {queryset.count()} session(s) by 1 hour.")
    extend_sessions.short_description = "Extend voucher by 1 hour"
    
    def activate_test_voucher(self, request, queryset):
        for session in queryset:
            session.activate_voucher(
                "TEST_VOUCHER",
                timezone.now() + timedelta(hours=1),
                {'auto_logout': 60}
            )
        self.message_user(request, f"Activated test voucher for {queryset.count()} session(s).")
    activate_test_voucher.short_description = "Activate test voucher (1 hour)"