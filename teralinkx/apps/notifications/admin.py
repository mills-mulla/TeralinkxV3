# apps/notifications/admin.py
from django.contrib import admin
from .models import Notification, NotificationTemplate


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for Notification model"""
    list_display = [
        'title',
        'notification_type',
        'scope',
        'priority',
        'user',
        'client',
        'is_persistent',
        'is_sent',
        'is_read',
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
        'updated_at'
    ]
    
    filter_horizontal = ['target_locations', 'target_packages']


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    """Admin interface for NotificationTemplate model"""
    list_display = [
        'name',
        'template_type',
        'notification_type',
        'is_active',
        'default_persistent',
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