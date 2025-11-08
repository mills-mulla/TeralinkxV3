from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
import uuid

from core.models import TimeStampedModel

User = get_user_model()

class LocationSyncLog(TimeStampedModel):
    """Comprehensive location data synchronization tracking"""
    SYNC_TYPES = [
        ('vouchers', 'Vouchers'),
        ('users', 'Users'), 
        ('sessions', 'Sessions'),
        ('transactions', 'Transactions'),
        ('packages', 'Packages'),
        ('devices', 'Devices'),
        ('network_config', 'Network Configuration'),
        ('full', 'Full Sync'),
    ]
    
    SYNC_DIRECTIONS = [
        ('upload', 'Upload to Central'),
        ('download', 'Download from Central'),
        ('bidirectional', 'Bidirectional'),
    ]
    
    SYNC_STATUS = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('success', 'Success'),
        ('partial_success', 'Partial Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Sync Configuration
    location = models.ForeignKey('locations.Location', on_delete=models.CASCADE, related_name='sync_logs')
    sync_type = models.CharField(max_length=20, choices=SYNC_TYPES)
    sync_direction = models.CharField(max_length=15, choices=SYNC_DIRECTIONS, default='bidirectional')
    
    # Status Tracking
    status = models.CharField(max_length=20, choices=SYNC_STATUS, default='pending')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Performance Metrics
    records_processed = models.IntegerField(default=0)
    records_synced = models.IntegerField(default=0)
    records_failed = models.IntegerField(default=0)
    total_size_bytes = models.BigIntegerField(default=0)
    duration_seconds = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Error Handling
    error_count = models.IntegerField(default=0)
    last_error = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    
    # Data Integrity
    checksum = models.CharField(max_length=64, blank=True, help_text="Data integrity checksum")
    data_version = models.CharField(max_length=50, blank=True, help_text="Data version identifier")
    
    # Detailed Results
    details = models.JSONField(default=dict)
    error_details = models.JSONField(default=dict, help_text="Detailed error information")
    
    # Manual Override
    is_manual = models.BooleanField(default=False)
    initiated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='initiated_syncs')
    
    def __str__(self):
        return f"{self.location} - {self.sync_type} - {self.status}"
    
    @property
    def is_completed(self):
        """Check if sync is completed"""
        return self.status in ['success', 'partial_success', 'failed', 'cancelled']
    
    @property
    def success_rate(self):
        """Calculate sync success rate"""
        if self.records_processed == 0:
            return 0
        return (self.records_synced / self.records_processed) * 100
    
    @property
    def sync_duration(self):
        """Calculate sync duration"""
        if self.completed_at and self.started_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def start_sync(self):
        """Start synchronization process"""
        self.status = 'in_progress'
        self.started_at = timezone.now()
        self.save()
    
    def complete_sync(self, success=True, error_message="", details=None):
        """Complete synchronization process"""
        self.status = 'success' if success else 'failed'
        self.completed_at = timezone.now()
        
        if self.started_at and self.completed_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
        
        if error_message:
            self.last_error = error_message
            self.error_count += 1
        
        if details:
            self.details = details
        
        self.save()
        
        # Log sync completion
        if success:
            from security.models import SecurityLog
            SecurityLog.objects.create(
                action_type='sync_completed',
                action_category='system',
                description=f"Sync {self.sync_type} completed for {self.location}",
                severity='info',
                details={
                    'sync_id': str(self.id),
                    'location': str(self.location),
                    'sync_type': self.sync_type,
                    'records_processed': self.records_processed,
                    'records_synced': self.records_synced,
                    'duration_seconds': self.duration_seconds
                }
            )
        else:
            from security.models import SecurityLog
            SecurityLog.objects.create(
                action_type='sync_failed',
                action_category='system',
                description=f"Sync {self.sync_type} failed for {self.location}",
                severity='high',
                details={
                    'sync_id': str(self.id),
                    'location': str(self.location),
                    'sync_type': self.sync_type,
                    'error_message': error_message,
                    'retry_count': self.retry_count
                }
            )
    
    def record_progress(self, processed, synced, failed=0):
        """Record sync progress"""
        self.records_processed = processed
        self.records_synced = synced
        self.records_failed = failed
        
        if failed > 0:
            self.error_count = failed
            self.status = 'partial_success'
        
        self.save()
    
    def can_retry(self):
        """Check if sync can be retried"""
        return self.retry_count < self.max_retries and self.status in ['failed', 'partial_success']
    
    def retry_sync(self):
        """Retry failed synchronization"""
        if not self.can_retry():
            return False
        
        self.retry_count += 1
        self.status = 'pending'
        self.last_error = ""
        self.save()
        
        return True
    
    @classmethod
    def get_sync_statistics(cls, location, days=7):
        """Get sync statistics for location"""
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Count, Avg, Sum
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        syncs = cls.objects.filter(location=location, started_at__gte=cutoff_date)
        
        stats = syncs.aggregate(
            total_syncs=Count('id'),
            successful_syncs=Count('id', filter=models.Q(status='success')),
            failed_syncs=Count('id', filter=models.Q(status='failed')),
            average_duration=Avg('duration_seconds'),
            total_records=Sum('records_synced')
        )
        
        # Add success rate
        if stats['total_syncs'] > 0:
            stats['success_rate'] = (stats['successful_syncs'] / stats['total_syncs']) * 100
        else:
            stats['success_rate'] = 0
        
        # Add recent activity
        recent_activity = syncs.values('sync_type').annotate(
            count=Count('id'),
            last_sync=models.Max('started_at')
        ).order_by('-last_sync')
        
        stats['recent_activity'] = list(recent_activity)
        
        return stats
    
    class Meta:
        indexes = [
            models.Index(fields=['location', 'started_at']),
            models.Index(fields=['sync_type']),
            models.Index(fields=['status']),
            models.Index(fields=['started_at']),
            models.Index(fields=['completed_at']),
        ]
        ordering = ['-started_at']
        verbose_name = "Location Sync Log"
        verbose_name_plural = "Location Sync Logs"

class SyncConfiguration(TimeStampedModel):
    """Configuration for synchronization settings"""
    location = models.OneToOneField('locations.Location', on_delete=models.CASCADE, related_name='sync_config')
    
    # Sync Intervals
    voucher_sync_interval = models.IntegerField(default=5, help_text="Voucher sync interval in minutes")
    user_sync_interval = models.IntegerField(default=10, help_text="User sync interval in minutes")
    session_sync_interval = models.IntegerField(default=2, help_text="Session sync interval in minutes")
    transaction_sync_interval = models.IntegerField(default=15, help_text="Transaction sync interval in minutes")
    
    # Data Retention
    keep_sync_logs_days = models.IntegerField(default=30, help_text="Days to keep sync logs")
    max_sync_retries = models.IntegerField(default=3, help_text="Maximum sync retry attempts")
    
    # Bandwidth Limits
    max_sync_size_mb = models.IntegerField(default=50, help_text="Maximum sync payload size in MB")
    sync_batch_size = models.IntegerField(default=100, help_text="Records per sync batch")
    
    # Network Settings
    sync_endpoint = models.URLField(help_text="Central server sync endpoint")
    api_key = models.CharField(max_length=255, blank=True, help_text="API key for authentication")
    timeout_seconds = models.IntegerField(default=30, help_text="Sync request timeout")
    
    # Features
    auto_sync_enabled = models.BooleanField(default=True)
    compression_enabled = models.BooleanField(default=True)
    encryption_enabled = models.BooleanField(default=True)
    
    # Conflict Resolution
    conflict_resolution = models.CharField(max_length=20, choices=[
        ('central_wins', 'Central Wins'),
        ('local_wins', 'Local Wins'),
        ('newer_wins', 'Newer Wins'),
        ('manual', 'Manual Resolution'),
    ], default='newer_wins')
    
    def __str__(self):
        return f"Sync Config - {self.location}"
    
    class Meta:
        verbose_name = "Sync Configuration"
        verbose_name_plural = "Sync Configurations"

class DataChangeLog(TimeStampedModel):
    """Track data changes for incremental synchronization"""
    CHANGE_TYPES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    ]
    
    MODEL_TYPES = [
        ('voucher', 'Voucher'),
        ('user', 'User'),
        ('session', 'Session'),
        ('transaction', 'Transaction'),
        ('device', 'Device'),
        ('package', 'Package'),
    ]
    
    # Change Information
    location = models.ForeignKey('locations.Location', on_delete=models.CASCADE, related_name='data_changes')
    model_type = models.CharField(max_length=20, choices=MODEL_TYPES)
    change_type = models.CharField(max_length=10, choices=CHANGE_TYPES)
    object_id = models.CharField(max_length=100, help_text="ID of the changed object")
    
    # Change Data
    old_data = models.JSONField(null=True, blank=True, help_text="Data before change")
    new_data = models.JSONField(null=True, blank=True, help_text="Data after change")
    changed_fields = models.JSONField(default=list, help_text="List of changed field names")
    
    # Sync Status
    is_synced = models.BooleanField(default=False)
    synced_at = models.DateTimeField(null=True, blank=True)
    sync_attempts = models.IntegerField(default=0)
    
    # Metadata
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    change_reason = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return f"{self.model_type} {self.change_type} - {self.object_id}"
    
    @property
    def needs_sync(self):
        """Check if change needs to be synced"""
        return not self.is_synced
    
    def mark_as_synced(self):
        """Mark change as synced"""
        self.is_synced = True
        self.synced_at = timezone.now()
        self.save()
    
    def record_sync_attempt(self):
        """Record sync attempt"""
        self.sync_attempts += 1
        self.save()
    
    class Meta:
        indexes = [
            models.Index(fields=['location', 'is_synced']),
            models.Index(fields=['model_type', 'change_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_synced']),
        ]
        ordering = ['-created_at']
        verbose_name = "Data Change Log"
        verbose_name_plural = "Data Change Logs"