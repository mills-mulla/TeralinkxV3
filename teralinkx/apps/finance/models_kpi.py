# apps/finance/models_kpi.py
from django.db import models
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal


class KPISnapshot(models.Model):
    """Pre-computed KPI values, refreshed every 5 minutes"""
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # MRR Metrics
    mrr_current = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    mrr_last_month = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    mrr_target = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    mrr_growth_pct = models.FloatField(default=0)
    
    # Customer Metrics
    active_customers = models.IntegerField(default=0)
    active_customers_last_month = models.IntegerField(default=0)
    churn_rate_30d = models.FloatField(default=0)
    new_customers_30d = models.IntegerField(default=0)
    
    # Financial Metrics
    cash_position = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cash_position_30d_ago = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    outstanding_receivables = models.JSONField(default=dict)  # Aging buckets
    total_receivables = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Network Metrics
    network_uptime_7d = models.FloatField(default=100.0)
    
    # Revenue at Risk
    revenue_at_risk = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    high_risk_customers = models.IntegerField(default=0)
    
    # Performance Tracking
    computed_in_ms = models.IntegerField(default=0)
    
    class Meta:
        app_label = 'finance'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
        ]
    
    def __str__(self):
        return f"KPI Snapshot - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def age_seconds(self):
        """Get age of snapshot in seconds"""
        return (timezone.now() - self.timestamp).total_seconds()
    
    @property
    def is_stale(self):
        """Check if snapshot is older than 10 minutes"""
        return self.age_seconds > 600
    
    @classmethod
    def get_latest(cls):
        """Get the latest snapshot"""
        return cls.objects.first()
    
    @classmethod
    def cleanup_old_snapshots(cls, hours=24):
        """Delete snapshots older than specified hours"""
        cutoff = timezone.now() - timedelta(hours=hours)
        deleted_count = cls.objects.filter(timestamp__lt=cutoff).delete()[0]
        return deleted_count


class WeeklySummary(models.Model):
    """Auto-generated weekly summary for executives"""
    week_start = models.DateField(db_index=True)
    week_end = models.DateField()
    generated_at = models.DateTimeField(auto_now_add=True)
    
    # Top Wins
    top_wins = models.JSONField(default=list)
    
    # Top Risks
    top_risks = models.JSONField(default=list)
    
    # Budget Status
    budget_status = models.CharField(max_length=20, choices=[
        ('on_track', 'On Track'),
        ('at_risk', 'At Risk'),
        ('over_budget', 'Over Budget')
    ], default='on_track')
    budget_summary = models.JSONField(default=dict)
    
    # Churn Risk
    churn_risk_summary = models.JSONField(default=dict)
    
    # Key Metrics
    weekly_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    weekly_new_customers = models.IntegerField(default=0)
    weekly_churned_customers = models.IntegerField(default=0)
    
    class Meta:
        app_label = 'finance'
        ordering = ['-week_start']
        unique_together = ['week_start', 'week_end']
    
    def __str__(self):
        return f"Weekly Summary - {self.week_start} to {self.week_end}"
    
    @classmethod
    def get_latest(cls):
        """Get the latest weekly summary"""
        return cls.objects.first()
