# analytics/models.py additions
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class ABTestExperiment(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('completed', 'Completed')
    ], default='draft')
    control_group_size = models.IntegerField(default=50)
    variant_group_size = models.IntegerField(default=50)
    metric_to_track = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        db_table = 'ab_test_experiments'

class ABTestVariant(models.Model):
    experiment = models.ForeignKey(ABTestExperiment, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100)
    description = models.TextField()
    config = models.JSONField()
    participants = models.IntegerField(default=0)
    conversions = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        db_table = 'ab_test_variants'

class CustomerHealthScore(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    health_score = models.IntegerField(default=0)  # 0-100
    engagement_score = models.IntegerField(default=0)
    satisfaction_score = models.IntegerField(default=0)
    usage_score = models.IntegerField(default=0)
    payment_score = models.IntegerField(default=0)
    last_calculated = models.DateTimeField(auto_now=True)
    risk_level = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ])
    
    class Meta:
        db_table = 'customer_health_scores'

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100)
    resource_type = models.CharField(max_length=100)
    resource_id = models.IntegerField(null=True)
    changes = models.JSONField(null=True)
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_logs'
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['resource_type', 'resource_id']),
        ]

class DataQualityCheck(models.Model):
    check_name = models.CharField(max_length=200)
    table_name = models.CharField(max_length=100)
    check_type = models.CharField(max_length=50, choices=[
        ('completeness', 'Completeness'),
        ('accuracy', 'Accuracy'),
        ('consistency', 'Consistency'),
        ('timeliness', 'Timeliness')
    ])
    status = models.CharField(max_length=20, choices=[
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('warning', 'Warning')
    ])
    score = models.DecimalField(max_digits=5, decimal_places=2)
    details = models.JSONField()
    checked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'data_quality_checks'
