# apps/security/models.py
from django.db import models
from django.utils import timezone
from datetime import timedelta
import uuid
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

from core.models import TimeStampedModel

User = get_user_model()

import random
from django.conf import settings

class PhoneOTP(models.Model):
    """
    Model for storing phone number OTPs
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20, db_index=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(db_index=True)
    is_used = models.BooleanField(default=False, db_index=True)
    attempt_count = models.IntegerField(default=0)
    purpose = models.CharField(
        max_length=20,
        choices=[
            ('signup', 'Sign Up'),
            ('login', 'Login'),
            ('reset', 'Password Reset'),
            ('verify', 'Phone Verification')
        ],
        default='login'
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['phone_number', 'is_used', 'expires_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.phone_number} - {self.otp}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def increment_attempt(self):
        self.attempt_count += 1
        self.save()
    
    def mark_used(self):
        self.is_used = True
        self.save()
    
    @classmethod
    def cleanup_expired(cls):
        """Clean up expired OTPs"""
        cls.objects.filter(expires_at__lt=timezone.now()).delete()


class VerificationSession(models.Model):
    """
    Model for tracking verification sessions
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20)
    session_token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_completed = models.BooleanField(default=False)
    next_step = models.CharField(
        max_length=20,
        choices=[
            ('otp_sent', 'OTP Sent'),
            ('otp_verified', 'OTP Verified'),
            ('password_required', 'Password Required'),
            ('completed', 'Completed')
        ],
        default='otp_sent'
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['session_token']),
            models.Index(fields=['phone_number', 'is_completed']),
        ]
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def get_remaining_time(self):
        if self.is_expired():
            return 0
        return (self.expires_at - timezone.now()).seconds

        
class AuthSession(TimeStampedModel):
    """
    Authentication session tracking
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20, db_index=True)
    session_token = models.CharField(max_length=100, unique=True, db_index=True)
    auth_token = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(db_index=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('otp_sent', 'OTP Sent'),
            ('otp_verified', 'OTP Verified'),
            ('password_verified', 'Password Verified'),
            ('authenticated', 'Authenticated'),
            ('expired', 'Expired'),
            ('failed', 'Failed')
        ],
        default='pending'
    )
    auth_method = models.CharField(
        max_length=20,
        choices=[
            ('otp', 'OTP'),
            ('password', 'Password')
        ],
        default='otp'
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Foreign key to user after authentication
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='auth_sessions'
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['phone_number', 'status', 'expires_at']),
            models.Index(fields=['session_token', 'status']),
            models.Index(fields=['auth_token']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.phone_number} - {self.status} - {self.auth_method}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def mark_authenticated(self, user=None, auth_token=None):
        """Mark session as authenticated"""
        self.status = 'authenticated'
        if user:
            self.user = user
        if auth_token:
            self.auth_token = auth_token
        self.save()
    
    def mark_failed(self, reason="Authentication failed"):
        """Mark session as failed"""
        self.status = 'failed'
        self.save()
        
        # Log the failure
        SecurityLog.objects.create(
            action_type='login_failed',
            action_category='authentication',
            description=f"Authentication failed for {self.phone_number}: {reason}",
            severity='medium',
            ip_address=self.ip_address,
            details={
                'phone_number': self.phone_number,
                'auth_method': self.auth_method,
                'reason': reason,
                'session_id': str(self.id)
            }
        )

class SecurityLog(TimeStampedModel):
    """Comprehensive security audit trail with threat detection"""
    SEVERITY_LEVELS = [
        ('info', 'Information'),
        ('low', 'Low'),
        ('medium', 'Medium'), 
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    ACTION_CATEGORIES = [
        ('authentication', 'Authentication'),
        ('authorization', 'Authorization'),
        ('device_management', 'Device Management'),
        ('network_access', 'Network Access'),
        ('financial', 'Financial'),
        ('system', 'System Events'),
        ('compliance', 'Compliance'),
    ]
    
    ACTION_TYPES = [
        # Authentication
        ('login_success', 'Login Successful'),
        ('login_failed', 'Login Failed'),
        ('logout', 'Logout'),
        ('password_change', 'Password Changed'),
        ('password_reset', 'Password Reset'),
        ('two_factor_enabled', '2FA Enabled'),
        ('two_factor_disabled', '2FA Disabled'),
        
        # Authorization
        ('permission_granted', 'Permission Granted'),
        ('permission_revoked', 'Permission Revoked'),
        ('role_changed', 'Role Changed'),
        
        # Device Management
        ('device_registered', 'Device Registered'),
        ('device_connected', 'Device Connected'),
        ('device_disconnected', 'Device Disconnected'),
        ('device_blocked', 'Device Blocked'),
        ('device_unblocked', 'Device Unblocked'),
        ('device_trusted', 'Device Trusted'),
        ('device_untrusted', 'Device Untrusted'),
        
        # Network Access
        ('voucher_activated', 'Voucher Activated'),
        ('voucher_expired', 'Voucher Expired'),
        ('roaming_started', 'Roaming Started'),
        ('roaming_ended', 'Roaming Ended'),
        ('access_denied', 'Access Denied'),
        ('suspicious_activity', 'Suspicious Activity'),
        
        # Financial
        ('payment_success', 'Payment Successful'),
        ('payment_failed', 'Payment Failed'),
        ('refund_issued', 'Refund Issued'),
        ('balance_adjusted', 'Balance Adjusted'),
        
        # System
        ('system_startup', 'System Startup'),
        ('system_shutdown', 'System Shutdown'),
        ('configuration_change', 'Configuration Changed'),
        ('maintenance_mode', 'Maintenance Mode Toggled'),
    ]
    
    # Core Information
    user = models.ForeignKey('users.ClientH', on_delete=models.CASCADE, null=True, blank=True, related_name='security_logs')
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    action_category = models.CharField(max_length=20, choices=ACTION_CATEGORIES)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='info')
    
    # Source Information
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    location = models.ForeignKey('locations.Location', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Context & Details
    details = models.JSONField(default=dict)
    correlation_id = models.UUIDField(default=uuid.uuid4, editable=False)
    session_id = models.CharField(max_length=100, blank=True)
    
    # Threat Intelligence
    is_suspicious = models.BooleanField(default=False)
    threat_score = models.IntegerField(default=0, help_text="0-100 threat score")
    reviewed = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_logs')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    # Resolution
    resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_logs')
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution = models.TextField(blank=True)
    
    def __str__(self):
        user_info = self.user.account if self.user else 'System'
        return f"{self.get_action_type_display()} - {user_info} - {self.created_at}"
    
    def calculate_threat_score(self):
        """Calculate threat score based on event patterns"""
        score = 0
        
        # Failed login attempts
        if self.action_type == 'login_failed':
            score += 20
            
            # Check for multiple recent failures
            recent_failures = SecurityLog.objects.filter(
                user=self.user,
                action_type='login_failed',
                created_at__gte=timezone.now() - timedelta(minutes=30)
            ).count()
            score += min(recent_failures * 10, 50)
        
        # Suspicious location changes
        if self.action_type in ['login_success', 'device_connected']:
            if self.user and self.location != self.user.home_location:
                score += 15
        
        # Device anomalies
        if self.action_type == 'device_connected':
            if self.user and not self.user.devices.filter(mac_address=self.details.get('mac_address')).exists():
                score += 25
        
        self.threat_score = min(score, 100)
        self.is_suspicious = self.threat_score >= 30
        self.save()
    
    def mark_as_reviewed(self, reviewer, notes=""):
        """Mark log entry as reviewed"""
        self.reviewed = True
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.review_notes = notes
        self.save()
    
    def mark_as_resolved(self, resolver, resolution=""):
        """Mark log entry as resolved"""
        self.resolved = True
        self.resolved_by = resolver
        self.resolved_at = timezone.now()
        self.resolution = resolution
        self.save()
    
    @classmethod
    def get_security_dashboard_stats(cls, days=7):
        """Get security statistics for dashboard"""
        from django.db.models import Count, Q
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        logs = cls.objects.filter(created_at__gte=cutoff_date)
        
        stats = {
            'total_events': logs.count(),
            'suspicious_events': logs.filter(is_suspicious=True).count(),
            'critical_events': logs.filter(severity='critical').count(),
            'unresolved_events': logs.filter(resolved=False, severity__in=['high', 'critical']).count(),
            'top_categories': logs.values('action_category').annotate(count=Count('id')).order_by('-count')[:5],
            'threat_trend': cls.get_threat_trend(days),
        }
        
        return stats
    
    @classmethod
    def get_threat_trend(cls, days=7):
        """Get threat trend data"""
        from django.db.models import Count
        
        trend_data = []
        for i in range(days):
            date = timezone.now() - timedelta(days=days - i - 1)
            next_date = date + timedelta(days=1)
            
            count = cls.objects.filter(
                created_at__gte=date,
                created_at__lt=next_date,
                is_suspicious=True
            ).count()
            
            trend_data.append({
                'date': date.date(),
                'count': count
            })
        
        return trend_data
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action_type']),
            models.Index(fields=['severity']),
            models.Index(fields=['is_suspicious']),
            models.Index(fields=['resolved']),
            models.Index(fields=['created_at']),
            models.Index(fields=['correlation_id']),
        ]
        ordering = ['-created_at']
        verbose_name = "Security Log"
        verbose_name_plural = "Security Logs"


class ISPEquipment(TimeStampedModel):
    """Network Equipment Model for ISP Operations"""
    
    EQUIPMENT_TYPES = [
        ('core_router', 'Core Router'),
        ('access_router', 'Access Router'),
        ('bras', 'BRAS/BNG'),
        ('olt', 'OLT'),
        ('switch', 'Switch'),
        ('wireless_ap', 'Wireless AP'),
        ('firewall', 'Firewall'),
        ('dns_server', 'DNS Server'),
        ('radius_server', 'RADIUS Server'),
        ('nms', 'Network Management Server'),
    ]
    
    VENDORS = [
        ('mikrotik', 'MikroTik'),
        ('cisco', 'Cisco'),
        ('juniper', 'Juniper'),
        ('huawei', 'Huawei'),
        ('zte', 'ZTE'),
        ('ubiquiti', 'Ubiquiti'),
        ('cambium', 'Cambium'),
        ('mimosa', 'Mimosa'),
        ('ruckus', 'Ruckus'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('production', 'Production'),
        ('maintenance', 'Maintenance'),
        ('backup', 'Backup/Spare'),
        ('offline', 'Offline'),
        ('decommissioned', 'Decommissioned'),
    ]
    
    # Core Identification
    name = models.CharField(max_length=100, unique=True, help_text="Device hostname")
    equipment_type = models.CharField(max_length=20, choices=EQUIPMENT_TYPES)
    vendor = models.CharField(max_length=20, choices=VENDORS)
    model = models.CharField(max_length=100, help_text="Model name")
    
    # Network Configuration
    management_ip = models.GenericIPAddressField(unique=True, help_text="Management IP")
    public_ip = models.GenericIPAddressField(blank=True, null=True, help_text="Public facing IP")
    ssh_port = models.IntegerField(default=22, validators=[MinValueValidator(1), MaxValueValidator(65535)])
    api_port = models.IntegerField(default=8728, validators=[MinValueValidator(1), MaxValueValidator(65535)])
    
    # Authentication
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=255)
    enable_password = models.CharField(max_length=255, blank=True)
    
    # ISP Location & POP
    pop = models.ForeignKey(
        'locations.Location', 
        on_delete=models.CASCADE,
        related_name='network_equipment',
        help_text="Point of Presence"
    )
    rack_position = models.CharField(max_length=20, blank=True, help_text="e.g., RACK-1-U12")
    
    # ISP Specific Fields
    role = models.CharField(
        max_length=20,
        choices=[
            ('core', 'Core Network'),
            ('aggregation', 'Aggregation'),
            ('access', 'Access Network'),
            ('backhaul', 'Backhaul'),
            ('customer_facing', 'Customer Facing'),
            ('management', 'Management'),
        ],
        default='access'
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='production')
    
    # Capacity & Usage
    max_capacity = models.IntegerField(default=0, help_text="Max user capacity")
    current_users = models.IntegerField(default=0, help_text="Current active users")
    uplink_speed = models.CharField(max_length=20, blank=True, help_text="e.g., 1G, 10G")
    
    # Maintenance
    last_backup = models.DateTimeField(null=True, blank=True)
    firmware_version = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "ISP Equipment"
        verbose_name_plural = "ISP Equipment"
        ordering = ['pop', 'role', 'name']
        indexes = [
            models.Index(fields=['pop', 'status']),
            models.Index(fields=['equipment_type', 'role']),
            models.Index(fields=['management_ip']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.pop.name})"
    
    @property
    def is_core_device(self):
        return self.role == 'core'
    
    @property
    def is_access_device(self):
        return self.role == 'access'
    
    @property
    def utilization_percentage(self):
        """Calculate user utilization percentage"""
        if self.max_capacity > 0:
            return (self.current_users / self.max_capacity) * 100
        return 0
    
    @property
    def needs_attention(self):
        """Check if device needs attention"""
        high_utilization = self.utilization_percentage > 85
        return self.status in ['maintenance', 'offline'] or high_utilization


class ISPEquipmentLog(TimeStampedModel):
    """ISP Equipment Management Log"""
    
    ACTION_TYPES = [
        ('config_backup', 'Configuration Backup'),
        ('config_change', 'Configuration Change'),
        ('firmware_update', 'Firmware Update'),
        ('maintenance', 'Maintenance'),
        ('reboot', 'Device Reboot'),
        ('troubleshoot', 'Troubleshooting'),
        ('user_sync', 'User Database Sync'),
        ('hotspot_config', 'Hotspot Configuration'),
    ]
    
    equipment = models.ForeignKey(
        ISPEquipment, 
        on_delete=models.CASCADE,
        related_name='logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    successful = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "ISP Equipment Log"
        verbose_name_plural = "ISP Equipment Logs"
    
    def __str__(self):
        status = "✓" if self.successful else "✗"
        return f"{status} {self.get_action_display()} - {self.equipment.name}"