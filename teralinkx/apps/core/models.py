# apps/core/models.py
from django.db import models


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
        
