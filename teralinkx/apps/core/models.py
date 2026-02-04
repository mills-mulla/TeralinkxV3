# apps/core/models.py
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """Abstract base model with created/updated timestamps"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class StatusTrackedModel(models.Model):
    """Abstract base model for status tracking"""
    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUS_SUSPENDED = 'suspended'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_INACTIVE, 'Inactive'),
        (STATUS_SUSPENDED, 'Suspended'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    
    class Meta:
        abstract = True
        
class NetworkDetectionLog(models.Model):
    """Log network detection requests for security auditing"""
    
    client_ip = models.GenericIPAddressField(null=True, blank=True)
    client_mac = models.CharField(max_length=17, null=True, blank=True)
    hotspot_name = models.CharField(max_length=100, null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    session_fingerprint = models.CharField(max_length=64, db_index=True)
    is_captive_portal = models.BooleanField(default=False)
    detected_at = models.DateTimeField(default=timezone.now)
    request_path = models.CharField(max_length=200)
    request_method = models.CharField(max_length=10)
    
    def __str__(self):
        return f"{self.client_ip} - {self.hotspot_name} - {self.detected_at}"
    
    class Meta:
        app_label = 'core'
        db_table = 'network_detection_logs'
        indexes = [
            models.Index(fields=['client_ip', 'detected_at']),
            models.Index(fields=['session_fingerprint']),
            models.Index(fields=['detected_at']),
        ]