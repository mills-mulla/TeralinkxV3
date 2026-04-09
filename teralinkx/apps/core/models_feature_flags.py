"""
Feature Flag Model for Gradual Rollouts
Enables/disables features with percentage-based rollout
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import hashlib


class FeatureFlag(models.Model):
    """
    Feature flag for gradual rollouts and A/B testing
    """
    name = models.CharField(
        max_length=100, 
        unique=True,
        help_text="Feature identifier (e.g., 'use_timescaledb_payments')"
    )
    description = models.TextField(blank=True)
    enabled = models.BooleanField(
        default=False,
        help_text="Master switch - if False, feature is disabled for everyone"
    )
    rollout_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage of requests that should use this feature (0-100)"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, blank=True)
    
    # Rollout tracking
    last_enabled_at = models.DateTimeField(null=True, blank=True)
    last_disabled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Feature Flag"
        verbose_name_plural = "Feature Flags"
        ordering = ['name']
    
    def __str__(self):
        status = "ON" if self.enabled else "OFF"
        return f"{self.name} ({status} - {self.rollout_percentage}%)"
    
    def save(self, *args, **kwargs):
        """Track enable/disable timestamps"""
        if self.pk:
            old = FeatureFlag.objects.get(pk=self.pk)
            if old.enabled != self.enabled:
                if self.enabled:
                    self.last_enabled_at = timezone.now()
                else:
                    self.last_disabled_at = timezone.now()
        super().save(*args, **kwargs)
    
    @classmethod
    def is_enabled(cls, feature_name, identifier=None):
        """
        Check if feature is enabled for a given identifier
        
        Args:
            feature_name: Name of the feature flag
            identifier: Optional identifier for consistent hashing (user_id, request_id, etc.)
        
        Returns:
            bool: True if feature should be enabled
        """
        try:
            flag = cls.objects.get(name=feature_name)
        except cls.DoesNotExist:
            return False
        
        # Master switch
        if not flag.enabled:
            return False
        
        # 100% rollout
        if flag.rollout_percentage >= 100:
            return True
        
        # 0% rollout
        if flag.rollout_percentage <= 0:
            return False
        
        # Percentage-based rollout with consistent hashing
        if identifier:
            # Use consistent hashing to ensure same identifier always gets same result
            hash_value = int(hashlib.md5(f"{feature_name}:{identifier}".encode()).hexdigest(), 16)
            return (hash_value % 100) < flag.rollout_percentage
        else:
            # Random rollout if no identifier provided
            import random
            return random.randint(0, 99) < flag.rollout_percentage
    
    @classmethod
    def enable(cls, feature_name, rollout_percentage=100):
        """Enable a feature flag"""
        flag, created = cls.objects.get_or_create(
            name=feature_name,
            defaults={'enabled': True, 'rollout_percentage': rollout_percentage}
        )
        if not created:
            flag.enabled = True
            flag.rollout_percentage = rollout_percentage
            flag.save()
        return flag
    
    @classmethod
    def disable(cls, feature_name):
        """Disable a feature flag"""
        try:
            flag = cls.objects.get(name=feature_name)
            flag.enabled = False
            flag.save()
            return flag
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def set_rollout(cls, feature_name, percentage):
        """Set rollout percentage for a feature"""
        try:
            flag = cls.objects.get(name=feature_name)
            flag.rollout_percentage = max(0, min(100, percentage))
            flag.save()
            return flag
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def get_all_enabled(cls):
        """Get all enabled feature flags"""
        return cls.objects.filter(enabled=True)
