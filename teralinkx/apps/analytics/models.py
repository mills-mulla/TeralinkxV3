# apps/analytics/models.py
from django.db import models
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from core.models import TimeStampedModel

class ActiveSession(TimeStampedModel):
    """Enhanced active session management"""
    session_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey('users.ClientH', on_delete=models.CASCADE, related_name='analytics_active_sessions')
    device = models.ForeignKey(  # ADD THIS FIELD
        'users.UserDevice', 
        on_delete=models.CASCADE, 
        related_name='analytics_active_sessions',
        null=True, 
        blank=True,
        help_text="Device associated with this active session"
    )
    voucher = models.ForeignKey('packages.DispatchVoucher', on_delete=models.CASCADE, null=True, blank=True)
    location = models.ForeignKey('locations.Location', on_delete=models.CASCADE)
    is_roaming = models.BooleanField(default=False)
    
    # Network Information
    mac_address = models.CharField(max_length=17)
    ip_address = models.GenericIPAddressField()
    nas_ip_address = models.GenericIPAddressField()
    nas_identifier = models.CharField(max_length=100, blank=True)
    
    # Session Details
    start_time = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    uptime = models.DurationField(default=timedelta(0))
    
    # Usage Statistics
    download_bytes = models.BigIntegerField(default=0)
    upload_bytes = models.BigIntegerField(default=0)
    download_speed_bps = models.BigIntegerField(default=0)
    upload_speed_bps = models.BigIntegerField(default=0)
    
    # Session Quality
    packet_loss = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    latency_ms = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    # Status
    is_authenticated = models.BooleanField(default=True)
    terminate_cause = models.CharField(max_length=50, blank=True)
    terminated_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.account} - {self.mac_address} - {self.location}"
    
    @property
    def is_active(self):
        """Check if session is active"""
        return self.terminated_at is None
    
    @property
    def total_bytes(self):
        """Get total data usage"""
        return self.download_bytes + self.upload_bytes
    
    def update_usage(self, download_bytes, upload_bytes):
        """Update session usage"""
        self.download_bytes += download_bytes
        self.upload_bytes += upload_bytes
        self.last_update = timezone.now()
        self.save()
        
        # Update voucher usage if applicable
        if self.voucher:
            self.voucher.update_usage(download_bytes, upload_bytes)
        
        # Update user lifetime usage
        self.user.lifetime_data_used += download_bytes + upload_bytes
        self.user.save()
    
    def terminate(self, cause="User disconnected"):
        """Terminate session"""
        self.terminate_cause = cause
        self.terminated_at = timezone.now()
        self.save()
    
    class Meta:
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['user', 'start_time']),
            models.Index(fields=['mac_address']),
            models.Index(fields=['location']),
            models.Index(fields=['is_authenticated']),
            models.Index(fields=['start_time']),
            models.Index(fields=['device']),  # ADD THIS INDEX
        ]
        verbose_name = "Active Session"
        verbose_name_plural = "Active Sessions"

class DataUsageRecord(TimeStampedModel):
    """Comprehensive data usage analytics for business intelligence"""
    USAGE_TYPES = [
        ('web', 'Web Browsing'),
        ('streaming', 'Video Streaming'),
        ('gaming', 'Online Gaming'),
        ('download', 'File Download'),
        ('upload', 'File Upload'),
        ('voip', 'VoIP/Voice Call'),
        ('other', 'Other'),
    ]
    
    # Core Relationships
    user = models.ForeignKey('users.ClientH', on_delete=models.CASCADE, related_name='data_usage_records')
    device = models.ForeignKey('users.UserDevice', on_delete=models.SET_NULL, null=True, blank=True)
    session = models.ForeignKey(ActiveSession, on_delete=models.SET_NULL, null=True, blank=True)
    voucher = models.ForeignKey('packages.DispatchVoucher', on_delete=models.SET_NULL, null=True, blank=True)
    location = models.ForeignKey('locations.Location', on_delete=models.CASCADE)
    is_roaming = models.BooleanField(default=False)
    
    # Usage Metrics
    download_bytes = models.BigIntegerField(default=0)
    upload_bytes = models.BigIntegerField(default=0)
    total_packets = models.BigIntegerField(default=0)
    
    # Timing Information
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    
    # Classification
    usage_type = models.CharField(max_length=20, choices=USAGE_TYPES, default='other')
    protocol = models.CharField(max_length=20, blank=True, help_text="TCP/UDP/ICMP etc.")
    port = models.IntegerField(null=True, blank=True)
    
    # Quality Metrics
    average_speed_bps = models.BigIntegerField(default=0)
    peak_speed_bps = models.BigIntegerField(default=0)
    packet_loss_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    latency_ms = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    # Cost Calculation
    cost_per_mb = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Metadata
    source_ip = models.GenericIPAddressField(blank=True, null=True)
    destination_ip = models.GenericIPAddressField(blank=True, null=True)
    destination_domain = models.CharField(max_length=255, blank=True)
    user_agent = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.account} - {self.get_usage_type_display()} - {self.total_bytes} bytes"
    
    @property
    def total_bytes(self):
        return self.download_bytes + self.upload_bytes
    
    @property
    def total_megabytes(self):
        return self.total_bytes / (1024 * 1024)
    
    @property
    def average_download_speed_mbps(self):
        if self.duration and self.duration.total_seconds() > 0:
            return (self.download_bytes * 8) / (self.duration.total_seconds() * 1000000)
        return 0
    
    @property
    def is_completed(self):
        return self.end_time is not None
    
    def calculate_duration(self):
        """Calculate duration if not set"""
        if self.start_time and self.end_time and not self.duration:
            self.duration = self.end_time - self.start_time
            self.save()
    
    def calculate_cost(self):
        """Calculate usage cost"""
        if self.cost_per_mb > 0:
            total_mb = self.total_bytes / (1024 * 1024)
            self.total_cost = total_mb * self.cost_per_mb
            self.save()
    
    def get_usage_breakdown(self):
        """Get usage breakdown by type"""
        breakdown = {
            'web': 0,
            'streaming': 0,
            'gaming': 0,
            'download': 0,
            'upload': 0,
            'voip': 0,
            'other': 0,
        }
        return breakdown
    
    @classmethod
    def get_user_usage_summary(cls, user, days=30):
        """Get usage summary for a user"""
        from django.db.models import Sum, Avg, Max, Count
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        records = cls.objects.filter(user=user, start_time__gte=cutoff_date)
        
        summary = records.aggregate(
            total_download=Sum('download_bytes'),
            total_upload=Sum('upload_bytes'),
            average_speed=Avg('average_speed_bps'),
            peak_speed=Max('peak_speed_bps'),
            total_cost=Sum('total_cost'),
            session_count=Count('id')
        )
        
        summary['total_bytes'] = (summary['total_download'] or 0) + (summary['total_upload'] or 0)
        summary['days_analyzed'] = days
        
        return summary
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'start_time']),
            models.Index(fields=['device', 'start_time']),
            models.Index(fields=['voucher', 'start_time']),
            models.Index(fields=['location', 'start_time']),
            models.Index(fields=['usage_type']),
            models.Index(fields=['start_time']),
        ]
        ordering = ['-start_time']
        verbose_name = "Data Usage Record"
        verbose_name_plural = "Data Usage Records"

class DHCPLease(TimeStampedModel):
    """DHCP lease information from Mikrotik"""
    idD = models.CharField(max_length=50)
    client = models.ForeignKey('users.ClientH', on_delete=models.CASCADE, related_name='leases', null=True)
    address = models.GenericIPAddressField(blank=True, null=True)
    mac_address = models.CharField(max_length=17)
    dhcp_client_id = models.CharField(max_length=50, null=True)
    address_lists = models.TextField(blank=True)
    server = models.CharField(max_length=50)
    dhcp_option = models.TextField(blank=True)
    status = models.CharField(max_length=20)
    expires_after = models.DurationField(null=True, blank=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    age = models.DurationField(null=True, blank=True)
    active_address = models.GenericIPAddressField(blank=True, null=True)  # COMPLETED THIS LINE
    
    def __str__(self):
        return f"{self.mac_address} - {self.address}"
    
    @property
    def is_active(self):
        """Check if lease is currently active"""
        return self.status.lower() == 'bound'
    
    @property
    def expires_at(self):
        """Calculate when lease expires"""
        if self.last_seen and self.expires_after:
            return self.last_seen + self.expires_after
        return None
    
    class Meta:
        verbose_name = "DHCP Lease"
        verbose_name_plural = "DHCP Leases"


# ── Downtime & Refund Models ──────────────────────────────────────────────────

class DowntimeRecord(TimeStampedModel):
    """Records a network downtime incident."""
    start_time      = models.DateTimeField()
    end_time        = models.DateTimeField(null=True, blank=True)
    description     = models.TextField(blank=True)
    affected_area   = models.CharField(max_length=200, blank=True)
    reported_by     = models.CharField(max_length=100, blank=True)
    # Link to SLA outage if generated from finance module
    outage_event_id = models.IntegerField(null=True, blank=True, db_index=True)

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"Downtime {self.start_time.date()} — {self.duration_minutes}min"

    @property
    def duration_minutes(self):
        end = self.end_time or timezone.now()
        return int((end - self.start_time).total_seconds() / 60)


class RefundLog(TimeStampedModel):
    """Logs every refund issued to a customer."""
    REFUND_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('batch',      'Batch'),
        ('sla',        'SLA Credit'),
    ]
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('completed', 'Completed'),
        ('failed',    'Failed'),
    ]
    account          = models.CharField(max_length=100, db_index=True)
    client_username  = models.CharField(max_length=150, blank=True)
    refund_amount    = models.DecimalField(max_digits=12, decimal_places=2)
    downtime_minutes = models.IntegerField(default=0)
    refund_type      = models.CharField(max_length=20, choices=REFUND_TYPE_CHOICES, default='individual')
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    downtime_record  = models.ForeignKey(DowntimeRecord, on_delete=models.SET_NULL,
                                         null=True, blank=True, related_name='refunds')
    notes            = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Refund {self.account} KES {self.refund_amount} ({self.refund_type})"
