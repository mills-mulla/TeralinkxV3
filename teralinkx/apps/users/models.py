# apps/users/models.py
from django.db import models
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
import uuid

from core.models import TimeStampedModel

User = get_user_model()


class ClientH(TimeStampedModel):
    """
    Enterprise client management system with session-based device tracking.
    
    This model represents a client account with enhanced features for ISP management,
    including financial tracking, location management, and device session handling.
    """
    
    ACCOUNT_TIERS = [
        ('basic', 'Basic'),
        ('premium', 'Premium'), 
        ('business', 'Business'),
        ('enterprise', 'Enterprise'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('inactive', 'Inactive'),
        ('banned', 'Banned'),
    ]
    
    # Core Identity
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='client_profile',
        help_text="Django User account linked to this client"
    )
    account = models.CharField(
        max_length=15, 
        unique=True,
        help_text="Unique client account identifier"
    )
    
    # Personalization
    display_name = models.CharField(
        max_length=100, 
        blank=True,
        help_text="User-friendly display name"
    )
    phone_number = models.CharField(
        max_length=20, 
        blank=True,
        help_text="Primary contact phone number"
    )
    
    # Account Management
    account_tier = models.CharField(
        max_length=20, 
        choices=ACCOUNT_TIERS, 
        default='basic',
        help_text="Service tier determining features and limits"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='active',
        help_text="Current account status"
    )
    
    # Financials
    balance = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Current account balance"
    )
    credit_limit = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Maximum credit allowance"
    )
    total_spent = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        help_text="Lifetime total spending"
    )
    lifetime_data_used = models.BigIntegerField(
        default=0,
        help_text="Total data consumed in bytes"
    )
    
    # Location & Roaming
    home_location = models.ForeignKey(
        'locations.Location', 
        on_delete=models.PROTECT, 
        related_name='home_users',
        help_text="Primary registered location"
    )
    current_location = models.ForeignKey(
        'locations.Location', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='current_users',
        help_text="Current active location"
    )
    last_location_update = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When location was last updated"
    )
    
    # Security
    failed_login_attempts = models.IntegerField(
        default=0,
        help_text="Count of consecutive failed login attempts"
    )
    two_factor_enabled = models.BooleanField(
        default=False,
        help_text="Whether 2FA is enabled for this account"
    )
    
    # Preferences
    auto_renew = models.BooleanField(
        default=False,
        help_text="Auto-renew packages when expired"
    )
    
    # Network Information
    active_voucher = models.CharField(
        max_length=50, 
        blank=True,
        help_text="Currently active voucher code"
    )
    voucher_expiry = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Expiration time of active voucher"
    )
    
    # Metadata
    last_login = models.DateTimeField(
        auto_now=True,
        help_text="Last login time across all devices"
    )
    last_balance_update = models.DateTimeField(
        auto_now=True,
        help_text="When balance was last updated"
    )
    profile_image = models.ImageField(
        upload_to='profile_images/', 
        blank=True, 
        null=True,
        help_text="User profile picture"
    )

    def __str__(self):
        """String representation of the client"""
        return f"{self.display_name or self.user.username} ({self.account})"

    

    @property
    def is_eligible_for_credit(self):
        """Check if user is eligible for credit purchases based on tier"""
        return self.account_tier in ['premium', 'business', 'enterprise'] and self.credit_limit > 0
    
    @property
    def available_credit(self):
        """Calculate available credit (balance + credit limit)"""
        return max(0, self.credit_limit + self.balance)
    
    @property
    def current_ip_address(self):
        """Get current IP from the most recent active session"""
        recent_session = self.active_sessions.order_by('-last_activity').first()
        return recent_session.ip_address if recent_session else None
    
    @property
    def current_mac_address(self):
        """Get MAC address from the most recent active session"""
        recent_session = self.active_sessions.order_by('-last_activity').first()
        return recent_session.device.mac_address if recent_session else None
    
    @property
    def active_sessions(self):
        """Get all currently active sessions"""
        return self.sessions.filter(is_active=True)
    
    @property
    def connected_devices(self):
        """Get all currently connected devices (with active sessions)"""
        device_ids = self.sessions.filter(
            is_active=True
        ).values_list('device_id', flat=True)
        
        return self.devices.filter(id__in=device_ids)
    
    @property
    def devices_with_vouchers(self):
        """Get devices with active vouchers"""
        from django.db.models import Subquery, OuterRef, Exists
        
        # Find devices with active voucher sessions
        active_voucher_sessions = UserSession.objects.filter(
            device=OuterRef('pk'),
            is_active=True,
            active_voucher__isnull=False,
            voucher_expires__gt=timezone.now()
        )
        
        return self.devices.annotate(
            has_active_voucher=Exists(active_voucher_sessions)
        ).filter(has_active_voucher=True)
    
    def get_active_voucher_sessions(self):
        """Get all active voucher sessions"""
        return self.sessions.filter(
            is_active=True,
            active_voucher__isnull=False,
            voucher_expires__gt=timezone.now()
        )
    
    def can_add_device(self, device_mac=None):
        """
        Check if user can add more devices.
        If device_mac provided, check if already owned.
        """
        # Check if device already belongs to user
        if device_mac:
            if self.devices.filter(mac_address=device_mac).exists():
                return True, "Device already owned"
        
        # Check device limits
        active_devices = self.devices.filter(status='active').count()
        max_allowed = self.get_max_allowed_devices()
        
        if active_devices >= max_allowed:
            return False, f"Device limit reached ({active_devices}/{max_allowed})"
        
        return True, "Can add device"
    
    def update_network_presence(self, device_mac, ip_address, location):
        """
        Update network presence for a specific device.
        
        Args:
            device_mac (str): MAC address of the device
            ip_address (str): Current IP address
            location (Location): Current location object
            
        Returns:
            tuple: (device, session) objects
        """
        # Get or create the device
        device, device_created = UserDevice.objects.get_or_create(
            mac_address=device_mac,
            defaults={
                'user': self,
                'device_name': f"{self.display_name}'s Device",
                'device_type': 'other'
            }
        )
        
        # Update device presence
        device.update_presence(ip_address=ip_address, location=location)
        
        # Create or update session
        session, session_created = UserSession.objects.get_or_create(
            user=self,
            device=device,
            is_active=True,
            defaults={
                'session_id': uuid.uuid4(),
                'ip_address': ip_address,
                'location': location,
                'session_type': 'network'
            }
        )
        
        if not session_created:
            session.ip_address = ip_address
            session.location = location
            session.save()
        
        # Update client's current location
        self.current_location = location
        self.last_location_update = timezone.now()
        self.save()
        
        return device, session
    
    def get_active_voucher(self):
        """Get currently active voucher object if available"""
        if self.active_voucher:
            try:
                from packages.models import DispatchVoucher
                return DispatchVoucher.objects.get(
                    voucher_code=self.active_voucher,
                    status='active'
                )
            except DispatchVoucher.DoesNotExist:
                return None
        return None
    
    def get_active_devices(self):
        """Get all active devices (not suspended)"""
        return self.devices.filter(status='active')
    
    def get_max_allowed_devices(self):
        """Get maximum allowed devices based on account tier"""
        tier_limits = {
            'basic': 5,
            'premium': 10,
            'business': 25,
            'enterprise': 50
        }
        return tier_limits.get(self.account_tier, 3)
    
    def terminate_all_sessions(self, reason="System logout"):
        """Terminate all active sessions for this client"""
        sessions_terminated = self.active_sessions.update(is_active=False)
        
        # Log the action
        from security.models import SecurityLog
        SecurityLog.objects.create(
            user=self,
            action_type='sessions_terminated',
            description=f"All active sessions terminated: {reason}",
            severity='medium',
            details={
                'sessions_terminated': sessions_terminated,
                'reason': reason
            }
        )
        
        return sessions_terminated
    
    def get_session_statistics(self):
        """Get comprehensive session statistics"""
        active_sessions = self.active_sessions
        
        from django.db.models import Sum
        return {
            'total_active_sessions': active_sessions.count(),
            'unique_locations': active_sessions.values('location').distinct().count(),
            'unique_devices': active_sessions.values('device').distinct().count(),
            'voucher_sessions': active_sessions.filter(active_voucher__isnull=False).exclude(active_voucher='').count(),
            'owner_sessions': active_sessions.filter(is_owner=True).count(),
            'transferred_sessions': active_sessions.filter(was_transferred=True).count(),
            'oldest_session': active_sessions.order_by('login_time').first(),
            'newest_session': active_sessions.order_by('-login_time').first(),
            'total_data_used': active_sessions.aggregate(total=Sum('data_used'))['total'] or 0,
        }
        
    class Meta:
        indexes = [
            models.Index(fields=['account']),
            models.Index(fields=['status']),
            models.Index(fields=['account_tier']),
            models.Index(fields=['home_location']),
            models.Index(fields=['current_location']),
            models.Index(fields=['balance']),
            models.Index(fields=['last_login']),
        ]
        verbose_name = "Client"
        verbose_name_plural = "Clients"


class UserDevice(TimeStampedModel):
    """
    Device management system for tracking client devices.
    
    This model represents physical devices owned by clients, storing permanent
    device identity and configuration information.
    """
    
    DEVICE_TYPES = [
        ('phone', 'Smartphone'),
        ('laptop', 'Laptop'),
        ('tablet', 'Tablet'),
        ('desktop', 'Desktop'),
        ('iot', 'IoT Device'),
        ('gaming', 'Gaming Console'),
        ('tv', 'Smart TV'),
        ('other', 'Other'),
    ]
    
    DEVICE_PLATFORMS = [
        ('windows', 'Windows'),
        ('macos', 'macOS'),
        ('linux', 'Linux'),
        ('android', 'Android'),
        ('ios', 'iOS'),
        ('other', 'Other OS'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]
    
    # Core Identity
    user = models.ForeignKey(
        ClientH, 
        on_delete=models.CASCADE, 
        related_name='devices',
        help_text="Client account that owns this device"
    )
    mac_address = models.CharField(
        max_length=17, 
        unique=False,
        db_index=True,
        help_text="Unique hardware MAC address"
    )
    device_name = models.CharField(
        max_length=100,
        help_text="User-friendly device name"
    )
    device_type = models.CharField(
        max_length=20, 
        choices=DEVICE_TYPES, 
        default='other',
        help_text="Type of device"
    )
    device_platform = models.CharField(
        max_length=20, 
        choices=DEVICE_PLATFORMS, 
        default='other',
        help_text="Operating system platform"
    )
    device_model = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Device model information"
    )
    device_manufacturer = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Device manufacturer"
    )
    
    # Security & Status
    is_trusted = models.BooleanField(
        default=False,
        help_text="Whether device is trusted for auto-connection"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='active',
        help_text="Current device status"
    )
    
    # Activity Tracking
    last_seen = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Last time device was seen online"
    )
    last_seen_location = models.ForeignKey(
        'locations.Location', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Last known location of device"
    )
    total_connections = models.IntegerField(
        default=0,
        help_text="Total number of connections made"
    )
    favorite_location = models.ForeignKey(
        'locations.Location', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='favorite_devices',
        help_text="Most frequently used location"
    )
    
    previous_owners = models.JSONField(
        default=list,
        blank=True,
        help_text="History of previous owners [{'user_id': X, 'from': 'date', 'to': 'date'}]"
    )
    
    device_identification = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional device identification (browser, OS version, etc.)"
    )
    
    # Configuration
    auto_connect = models.BooleanField(
        default=True,
        help_text="Automatically connect when in range"
    )
    
    max_concurrent_sessions = models.IntegerField(
        default=1,
        help_text="Maximum concurrent sessions allowed"
    )

    created = models.DateTimeField(
        auto_now_add=True,
        help_text="When the device was first created/registered",
        null=True,  
        blank=True,
    )

    def __str__(self):
        """String representation of the device"""
        return f"{self.device_name} ({self.mac_address})"
    
    @property
    def is_online(self):
        """Check if device is currently online based on last seen time"""
        if not self.last_seen:
            return False
        return timezone.now() - self.last_seen < timedelta(minutes=5)
    
    @property
    def current_session(self):
        """Get current active session for this device"""
        return self.sessions.filter(is_active=True).first()
    
    @property
    def has_active_voucher(self):
        """Check if device has active voucher in any session"""
        return self.sessions.filter(
            is_active=True,
            active_voucher__isnull=False,
            voucher_expires__gt=timezone.now()
        ).exists()
    
    @property
    def active_voucher_session(self):
        """Get active voucher session if exists"""
        return self.sessions.filter(
            is_active=True,
            active_voucher__isnull=False,
            voucher_expires__gt=timezone.now()
        ).first()
    
    @property
    def concurrent_sessions_count(self):
        """Get number of concurrent active sessions"""
        return self.sessions.filter(is_active=True).count()
    
    @property
    def can_create_session(self):
        """Check if device can create new session"""
        return self.concurrent_sessions_count < self.max_concurrent_sessions
    
    def update_presence(self, ip_address=None, location=None):
        """
        Update device presence information and create activity log.
        
        Args:
            ip_address (str, optional): Current IP address
            location (Location, optional): Current location
        """
        self.last_seen = timezone.now()
        self.total_connections += 1
        
        if location:
            self.last_seen_location = location
            
        self.save()
        
        # Log device activity
        from security.models import SecurityLog
        SecurityLog.objects.create(
            user=self.user,
            action_type='device_connected',
            description=f"Device {self.device_name} connected",
            severity='low',
            details={
                'device_id': str(self.id),
                'mac_address': self.mac_address,
                'ip_address': ip_address,
                'location': str(location) if location else None,
                'total_connections': self.total_connections
            }
        )
    
    def transfer_to_user(self, new_user, reason="Device transfer"):
        """
        Transfer device to new user with history tracking.
        
        Args:
            new_user (ClientH): New owner
            reason (str): Reason for transfer
        
        Returns:
            bool: Success status
        """
        old_user = self.user
        
        # Record previous owner
        self.previous_owners.append({
            'user_id': old_user.id,
            'account': old_user.account,
            'from': self.created.isoformat(),
            'to': timezone.now().isoformat(),
            'reason': reason
        })
        
        # Transfer device
        self.user = new_user
        self.device_name = f"{new_user.display_name}'s Device"
        self.is_trusted = False  # Reset trust on transfer
        self.save()
        
        # Terminate old user's sessions
        terminated = self.sessions.filter(
            user=old_user,
            is_active=True
        ).update(is_active=False)
        
        # Log the transfer
        from security.models import SecurityLog
        SecurityLog.objects.create(
            user=old_user,
            action_type='device_transferred_out',
            description=f"Device {self.mac_address} transferred to {new_user.account}",
            severity='medium',
            details={
                'new_owner': new_user.account,
                'device_mac': self.mac_address,
                'terminated_sessions': terminated,
                'reason': reason
            }
        )
        
        SecurityLog.objects.create(
            user=new_user,
            action_type='device_transferred_in',
            description=f"Received device {self.mac_address} from {old_user.account}",
            severity='medium',
            details={
                'previous_owner': old_user.account,
                'device_mac': self.mac_address,
                'reason': reason
            }
        )
        
        return True
    
    def block_device(self, reason="Security concern"):
        """Block this device from network access"""
        old_status = self.status
        self.status = 'suspended'
        self.is_trusted = False
        self.save()
        
        # Terminate any active sessions
        terminated = self.sessions.filter(is_active=True).update(is_active=False)
        
        from security.models import SecurityLog
        SecurityLog.objects.create(
            user=self.user,
            action_type='device_blocked',
            description=f"Device {self.device_name} blocked: {reason}",
            severity='high',
            details={
                'device_id': str(self.id),
                'mac_address': self.mac_address,
                'old_status': old_status,
                'new_status': self.status,
                'terminated_sessions': terminated,
                'reason': reason,
            }
        )
        
        return terminated
    
    def unblock_device(self, reason="User request"):
        """Unblock this device and allow network access"""
        old_status = self.status
        self.status = 'active'
        self.save()
        
        from security.models import SecurityLog
        SecurityLog.objects.create(
            user=self.user,
            action_type='device_unblocked',
            description=f"Device {self.device_name} unblocked: {reason}",
            severity='medium',
            details={
                'device_id': str(self.id),
                'mac_address': self.mac_address,
                'old_status': old_status,
                'new_status': self.status,
                'reason': reason,
            }
        )
    
    def get_connection_statistics(self, days=30):
        """
        Get connection statistics for the device over a specified period.
        
        Args:
            days (int): Number of days to analyze
            
        Returns:
            dict: Connection statistics
        """
        from_date = timezone.now() - timedelta(days=days)
        sessions = self.sessions.filter(login_time__gte=from_date)
        
        from django.db.models import Sum
        return {
            'total_sessions': sessions.count(),
            'average_duration': self._calculate_average_duration(sessions),
            'unique_locations': sessions.values('location').distinct().count(),
            'most_frequent_location': self._get_most_frequent_location(sessions),
            'total_data_used': sessions.aggregate(total=Sum('data_used'))['total'] or 0,
            'voucher_sessions': sessions.filter(active_voucher__isnull=False).count(),
        }
    
    def _calculate_average_duration(self, sessions):
        """Calculate average session duration"""
        if not sessions:
            return timedelta(0)
        
        total_duration = sum(
            (s.last_activity - s.login_time for s in sessions if s.last_activity),
            timedelta(0)
        )
        return total_duration / len(sessions)
    
    def _get_most_frequent_location(self, sessions):
        """Get the most frequently used location"""
        from django.db.models import Count
        location_count = sessions.values('location').annotate(count=Count('location')).order_by('-count').first()
        return location_count['location'] if location_count else None

    class Meta:
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['mac_address']),
            models.Index(fields=['last_seen']),
            models.Index(fields=['device_type']),
            models.Index(fields=['device_platform']),
            models.Index(fields=['favorite_location']),
            models.Index(fields=['is_trusted']),
        ]
        ordering = ['-last_seen']
        verbose_name = "User Device"
        verbose_name_plural = "User Devices"
        constraints = [
            models.UniqueConstraint(
                fields=['mac_address', 'user'],
                name='unique_device_per_user',
                condition=models.Q(status='active')
            )
        ]


class UserSession(TimeStampedModel):
    """
    Session management system for tracking active device connections.
    
    This model represents temporary connection sessions for devices,
    tracking real-time network presence and activity.
    """
    
    # Core fields
    user = models.ForeignKey(
        ClientH, 
        on_delete=models.CASCADE, 
        related_name='sessions',
        help_text="Client account for this session"
    )
    device = models.ForeignKey(
        UserDevice, 
        on_delete=models.CASCADE, 
        related_name='sessions',
        help_text="Device associated with this session"
    )
    session_id = models.CharField(
        max_length=100, 
        unique=True,
        help_text="Unique session identifier"
    )
    ip_address = models.GenericIPAddressField(
        help_text="Current IP address for this session"
    )
    location = models.ForeignKey(
        'locations.Location', 
        on_delete=models.SET_NULL, 
        null=True,
        help_text="Current location for this session"
    )
    login_time = models.DateTimeField(
        auto_now_add=True,
        help_text="When the session started"
    )
    last_activity = models.DateTimeField(
        auto_now=True,
        help_text="Last activity timestamp"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the session is currently active"
    )
    
    
    session_type = models.CharField(
        max_length=20,
        choices=[
            ('web', 'Web Authentication'),
            ('network', 'Network Connection'),
            ('voucher', 'Voucher Active'),
        ],
        default='network',
        help_text="Type of session"
    )
    
    is_owner = models.BooleanField(
        default=True,
        help_text="Is this user the device owner? (False for borrowed devices)"
    )
    
    was_transferred = models.BooleanField(
        default=False,
        help_text="Was device transferred during this session?"
    )
    
    request_metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional request metadata"
    )
    
    active_voucher = models.CharField(
        max_length=50,
        blank=True,
        help_text="Active voucher code for this session"
    )
    
    voucher_activated = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When voucher was activated for this session"
    )
    
    voucher_expires = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When active voucher expires"
    )
    
    auto_logout_minutes = models.IntegerField(
        default=1440,  # 24 hours
        help_text="Auto logout after X minutes (0 = never)"
    )
    
    data_used = models.BigIntegerField(
        default=0,
        help_text="Data used during this session (bytes)"
    )
    user_agent = models.TextField(
        blank=True,
        default='',
        help_text="User agent string from the connection"
    )

    def __str__(self):
        """String representation of the session"""
        return f"{self.user.account} - {self.device.device_name} - {self.session_id[:8]}"
    
    @property
    def duration(self):
        """Calculate current session duration"""
        if not self.is_active:
            return self.last_activity - self.login_time
        return timezone.now() - self.login_time
    
    @property
    def is_expired(self):
        """Check if session has expired (based on auto_logout_minutes)"""
        if self.auto_logout_minutes == 0:
            return False
        return self.duration > timedelta(minutes=self.auto_logout_minutes)
    
    @property
    def has_active_voucher(self):
        """Check if session has active voucher"""
        return bool(
            self.active_voucher and 
            self.voucher_expires and 
            self.voucher_expires > timezone.now()
        )
    
    @property
    def voucher_time_remaining(self):
        """Get remaining voucher time"""
        if not self.has_active_voucher:
            return timedelta(0)
        return self.voucher_expires - timezone.now()
    
    def refresh_activity(self):
        """Update last activity timestamp"""
        self.last_activity = timezone.now()
        self.save()
    
    def activate_voucher(self, voucher_code, expires_at, voucher_data=None):
        """Activate voucher for this session"""
        self.active_voucher = voucher_code
        self.voucher_activated = timezone.now()
        self.voucher_expires = expires_at
        self.session_type = 'voucher'
        
        if voucher_data:
            if 'auto_logout' in voucher_data:
                self.auto_logout_minutes = voucher_data['auto_logout']
        
        self.save()
        
        # Log voucher activation
        from security.models import SecurityLog
        SecurityLog.objects.create(
            user=self.user,
            action_type='voucher_activated',
            description=f"Voucher {voucher_code} activated for session",
            severity='info',
            ip_address=self.ip_address,
            details={
                'session_id': self.session_id,
                'voucher_code': voucher_code,
                'expires_at': expires_at.isoformat(),
                'device_mac': self.device.mac_address
            }
        )
    
    def deactivate_voucher(self, reason="Expired or cancelled"):
        """Deactivate voucher for this session"""
        old_voucher = self.active_voucher
        self.active_voucher = ''
        self.voucher_activated = None
        self.voucher_expires = None
        self.session_type = 'network'
        self.save()
        
        # Log voucher deactivation
        from security.models import SecurityLog
        SecurityLog.objects.create(
            user=self.user,
            action_type='voucher_expired',
            description=f"Voucher {old_voucher} deactivated: {reason}",
            severity='info',
            ip_address=self.ip_address,
            details={
                'session_id': self.session_id,
                'old_voucher': old_voucher,
                'reason': reason,
                'device_mac': self.device.mac_address
            }
        )
    
    def terminate(self, reason="User logout"):
        """Terminate this session"""
        self.is_active = False
        
        # Deactivate voucher if active
        if self.has_active_voucher:
            self.deactivate_voucher(f"Session terminated: {reason}")
        
        self.save()
        
        # Log session termination
        from security.models import SecurityLog
        SecurityLog.objects.create(
            user=self.user,
            action_type='session_terminated',
            description=f"Session terminated for {self.device.device_name}: {reason}",
            severity='low',
            details={
                'session_id': self.session_id,
                'device_id': str(self.device.id),
                'duration': str(self.duration),
                'reason': reason,
                'had_voucher': bool(self.active_voucher)
            }
        )
    
    def update_data_usage(self, bytes_used):
        """Update data usage for this session"""
        self.data_used += bytes_used
        self.save()
        
        # Update client lifetime data
        self.user.lifetime_data_used += bytes_used
        self.user.save()
    
    def get_session_summary(self):
        """Get comprehensive session summary"""
        return {
            'session_id': self.session_id,
            'device': str(self.device),
            'duration': str(self.duration),
            'location': str(self.location) if self.location else 'Unknown',
            'ip_address': self.ip_address,
            'is_active': self.is_active,
            'login_time': self.login_time.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'session_type': self.session_type,
            'is_owner': self.is_owner,
            'was_transferred': self.was_transferred,
            'has_active_voucher': self.has_active_voucher,
            'active_voucher': self.active_voucher,
            'voucher_expires': self.voucher_expires.isoformat() if self.voucher_expires else None,
            'voucher_time_remaining': str(self.voucher_time_remaining) if self.has_active_voucher else '00:00:00',
            'data_used': self.data_used,
            'auto_logout_minutes': self.auto_logout_minutes,
        }

    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['device', 'is_active']),
            models.Index(fields=['session_id']),
            models.Index(fields=['login_time']),
            models.Index(fields=['last_activity']),
            models.Index(fields=['is_active']),
            models.Index(fields=['session_type']),
            models.Index(fields=['is_owner']),
            models.Index(fields=['active_voucher']),
            models.Index(fields=['voucher_expires']),
        ]
        ordering = ['-last_activity']
        verbose_name = "User Session"
        verbose_name_plural = "User Sessions"