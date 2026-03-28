from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import LocationSyncLog, SyncConfiguration, DataChangeLog

@admin.register(LocationSyncLog)
class LocationSyncLogAdmin(admin.ModelAdmin):
    list_display = ('location', 'sync_type', 'sync_direction', 'status_badge', 'records_processed', 'records_synced', 'records_failed', 'success_rate', 'duration', 'is_manual', 'retry_count', 'started_at')
    list_filter = ('sync_type', 'sync_direction', 'status', 'is_manual', 'started_at', 'location')
    search_fields = ('location__name', 'location__id', 'last_error')
    readonly_fields = ('created_at', 'updated_at', 'started_at', 'completed_at', 'duration_seconds', 'success_rate')
    date_hierarchy = 'started_at'
    
    fieldsets = (
        ('Sync Configuration', {
            'fields': ('location', 'sync_type', 'sync_direction', 'is_manual', 'initiated_by')
        }),
        ('Status Tracking', {
            'fields': ('status', 'started_at', 'completed_at', 'duration_seconds')
        }),
        ('Performance Metrics', {
            'fields': ('records_processed', 'records_synced', 'records_failed', 'total_size_bytes', 'success_rate')
        }),
        ('Error Handling', {
            'fields': ('error_count', 'last_error', 'retry_count', 'max_retries'),
            'classes': ('collapse',)
        }),
        ('Data Integrity', {
            'fields': ('checksum', 'data_version'),
            'classes': ('collapse',)
        }),
        ('Detailed Results', {
            'fields': ('details', 'error_details'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'pending': 'gray',
            'in_progress': 'blue',
            'success': 'green',
            'partial_success': 'orange',
            'failed': 'red',
            'cancelled': 'darkgray',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            color, obj.get_status_display().upper()
        )
    status_badge.short_description = 'Status'
    
    def success_rate(self, obj):
        rate = obj.success_rate
        color = 'green' if rate >= 90 else 'orange' if rate >= 70 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, rate
        )
    success_rate.short_description = 'Success Rate'
    
    def duration(self, obj):
        if obj.duration_seconds:
            return f"{obj.duration_seconds}s"
        return "N/A"
    duration.short_description = 'Duration'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('location', 'initiated_by')
    
    actions = ['retry_failed_syncs', 'cancel_pending_syncs']
    
    def retry_failed_syncs(self, request, queryset):
        count = 0
        for sync in queryset:
            if sync.retry_sync():
                count += 1
        self.message_user(request, f'{count} syncs queued for retry.')
    retry_failed_syncs.short_description = "Retry selected failed syncs"
    
    def cancel_pending_syncs(self, request, queryset):
        pending_syncs = queryset.filter(status__in=['pending', 'in_progress'])
        updated = pending_syncs.update(status='cancelled', completed_at=timezone.now())
        self.message_user(request, f'{updated} syncs cancelled.')
    cancel_pending_syncs.short_description = "Cancel selected pending syncs"
    
    def changelist_view(self, request, extra_context=None):
        # Add sync statistics to context
        if extra_context is None:
            extra_context = {}
        
        from django.utils import timezone
        from datetime import timedelta
        
        # Get recent sync stats
        recent_syncs = LocationSyncLog.objects.filter(
            started_at__gte=timezone.now() - timedelta(days=1)
        )
        
        stats = {
            'total_syncs': recent_syncs.count(),
            'successful_syncs': recent_syncs.filter(status='success').count(),
            'failed_syncs': recent_syncs.filter(status='failed').count(),
            'average_duration': recent_syncs.aggregate(avg=models.Avg('duration_seconds'))['avg'] or 0,
        }
        
        extra_context['sync_stats'] = stats
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(SyncConfiguration)
class SyncConfigurationAdmin(admin.ModelAdmin):
    list_display = ('location', 'auto_sync_enabled', 'sync_endpoint', 'max_sync_retries', 'compression_enabled', 'encryption_enabled', 'updated_at')
    list_filter = ('auto_sync_enabled', 'compression_enabled', 'encryption_enabled', 'conflict_resolution')
    search_fields = ('location__name', 'location__id', 'sync_endpoint')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Location', {
            'fields': ('location',)
        }),
        ('Sync Intervals (minutes)', {
            'fields': (
                'voucher_sync_interval',
                'user_sync_interval', 
                'session_sync_interval',
                'transaction_sync_interval'
            )
        }),
        ('Data Retention', {
            'fields': ('keep_sync_logs_days', 'max_sync_retries')
        }),
        ('Bandwidth Limits', {
            'fields': ('max_sync_size_mb', 'sync_batch_size')
        }),
        ('Network Settings', {
            'fields': ('sync_endpoint', 'api_key', 'timeout_seconds')
        }),
        ('Features', {
            'fields': ('auto_sync_enabled', 'compression_enabled', 'encryption_enabled')
        }),
        ('Conflict Resolution', {
            'fields': ('conflict_resolution',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('location',)
        return self.readonly_fields

@admin.register(DataChangeLog)
class DataChangeLogAdmin(admin.ModelAdmin):
    list_display = ('model_type', 'change_type', 'location', 'object_id', 'is_synced', 'sync_attempts', 'changed_by', 'created_at')
    list_filter = ('model_type', 'change_type', 'is_synced', 'location', 'created_at', 'changed_by')
    search_fields = ('object_id', 'location__name', 'change_reason')
    readonly_fields = ('created_at', 'updated_at', 'synced_at')
    
    fieldsets = (
        ('Change Information', {
            'fields': ('location', 'model_type', 'change_type', 'object_id')
        }),
        ('Change Data', {
            'fields': ('old_data', 'new_data', 'changed_fields'),
            'classes': ('collapse',)
        }),
        ('Sync Status', {
            'fields': ('is_synced', 'synced_at', 'sync_attempts')
        }),
        ('Metadata', {
            'fields': ('changed_by', 'change_reason'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('location', 'changed_by')
    
    actions = ['mark_as_synced', 'mark_as_unsynced']
    
    def mark_as_synced(self, request, queryset):
        for change_log in queryset:
            change_log.mark_as_synced()
        self.message_user(request, f'{queryset.count()} changes marked as synced.')
    mark_as_synced.short_description = "Mark selected as synced"
    
    def mark_as_unsynced(self, request, queryset):
        updated = queryset.update(is_synced=False, synced_at=None)
        self.message_user(request, f'{updated} changes marked as unsynced.')
    mark_as_unsynced.short_description = "Mark selected as unsynced"