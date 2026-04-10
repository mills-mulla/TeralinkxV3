"""
Cash Flow Forecast Models
Stores multi-scenario cash flow predictions using Prophet.
"""
from django.db import models
from django.utils import timezone
from core.models import TimeStampedModel


class CashFlowForecast(TimeStampedModel):
    """
    Cash flow forecast with multiple scenarios (optimistic/base/conservative).
    Generated daily using Prophet time series forecasting.
    """
    
    SCENARIO_CHOICES = [
        ('optimistic', 'Optimistic (P10)'),
        ('base', 'Base Case (P50)'),
        ('conservative', 'Conservative (P90)'),
    ]
    
    FORECAST_TYPE_CHOICES = [
        ('revenue', 'Revenue Forecast'),
        ('expense', 'Expense Forecast'),
        ('net_cash_flow', 'Net Cash Flow'),
        ('cash_position', 'Cash Position'),
    ]
    
    # Forecast metadata
    forecast_date = models.DateField(
        help_text="Date this forecast was generated"
    )
    forecast_type = models.CharField(
        max_length=20,
        choices=FORECAST_TYPE_CHOICES
    )
    scenario = models.CharField(
        max_length=20,
        choices=SCENARIO_CHOICES,
        default='base'
    )
    
    # Forecast period
    period_start = models.DateField()
    period_end = models.DateField()
    horizon_days = models.IntegerField(
        help_text="Forecast horizon in days (30/90/180)"
    )
    
    # Forecast data (time series)
    forecast_data = models.JSONField(
        help_text="Daily forecast values: [{date, value, lower_bound, upper_bound}]"
    )
    
    # Summary metrics
    total_forecasted = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Total forecasted amount for period"
    )
    average_daily = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Average daily amount"
    )
    
    # Model performance
    model_accuracy = models.FloatField(
        null=True,
        blank=True,
        help_text="Model accuracy on historical data (MAPE)"
    )
    confidence_interval = models.FloatField(
        default=0.95,
        help_text="Confidence interval (0.80, 0.95)"
    )
    
    # Training data
    training_data_size = models.IntegerField(
        help_text="Number of historical data points used"
    )
    training_period_days = models.IntegerField(
        default=365,
        help_text="Historical period used for training (days)"
    )
    
    # Seasonality detected
    has_weekly_seasonality = models.BooleanField(default=False)
    has_monthly_seasonality = models.BooleanField(default=False)
    has_yearly_seasonality = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Most recent forecast for this type/scenario"
    )
    
    class Meta:
        app_label = 'finance'
        verbose_name = "Cash Flow Forecast"
        verbose_name_plural = "Cash Flow Forecasts"
        ordering = ['-forecast_date', 'forecast_type', 'scenario']
        indexes = [
            models.Index(fields=['forecast_date', 'forecast_type', 'scenario']),
            models.Index(fields=['is_active', 'forecast_type']),
            models.Index(fields=['period_start', 'period_end']),
        ]
        unique_together = ['forecast_date', 'forecast_type', 'scenario', 'horizon_days']
    
    def __str__(self):
        return f"{self.get_forecast_type_display()} - {self.get_scenario_display()} ({self.forecast_date})"
    
    @classmethod
    def get_latest_forecast(cls, forecast_type, scenario='base', horizon_days=90):
        """Get the most recent forecast"""
        return cls.objects.filter(
            forecast_type=forecast_type,
            scenario=scenario,
            horizon_days=horizon_days,
            is_active=True
        ).order_by('-forecast_date').first()
    
    @classmethod
    def deactivate_old_forecasts(cls, forecast_type, scenario, horizon_days):
        """Deactivate old forecasts when generating new one"""
        cls.objects.filter(
            forecast_type=forecast_type,
            scenario=scenario,
            horizon_days=horizon_days,
            is_active=True
        ).update(is_active=False)
    
    def get_forecast_for_date(self, target_date):
        """Get forecast value for specific date"""
        target_str = target_date.strftime('%Y-%m-%d')
        
        for item in self.forecast_data:
            if item['date'] == target_str:
                return {
                    'value': item['value'],
                    'lower_bound': item.get('lower_bound'),
                    'upper_bound': item.get('upper_bound'),
                }
        
        return None
    
    def get_summary_stats(self):
        """Get summary statistics for forecast"""
        values = [item['value'] for item in self.forecast_data]
        
        return {
            'total': self.total_forecasted,
            'average': self.average_daily,
            'min': min(values) if values else 0,
            'max': max(values) if values else 0,
            'data_points': len(values),
        }


class CashFlowAlert(TimeStampedModel):
    """
    Alerts for cash flow anomalies and thresholds.
    """
    
    ALERT_TYPE_CHOICES = [
        ('low_cash_position', 'Low Cash Position'),
        ('unusual_expense', 'Unusual Expense Forecast'),
        ('revenue_decline', 'Revenue Decline Forecast'),
        ('negative_cash_flow', 'Negative Cash Flow'),
        ('threshold_breach', 'Threshold Breach'),
    ]
    
    SEVERITY_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
        ('false_positive', 'False Positive'),
    ]
    
    # Alert details
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Related forecast
    forecast = models.ForeignKey(
        CashFlowForecast,
        on_delete=models.CASCADE,
        related_name='alerts',
        null=True,
        blank=True
    )
    
    # Alert data
    alert_date = models.DateField()
    threshold_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )
    actual_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Message
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Actions
    recommended_action = models.TextField(blank=True)
    acknowledged_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_alerts'
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    
    class Meta:
        app_label = 'finance'
        verbose_name = "Cash Flow Alert"
        verbose_name_plural = "Cash Flow Alerts"
        ordering = ['-alert_date', '-severity']
        indexes = [
            models.Index(fields=['alert_type', 'status']),
            models.Index(fields=['severity', 'status']),
            models.Index(fields=['alert_date']),
        ]
    
    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.get_severity_display()} ({self.alert_date})"
    
    def acknowledge(self, user):
        """Acknowledge alert"""
        self.status = 'acknowledged'
        self.acknowledged_by = user
        self.acknowledged_at = timezone.now()
        self.save()
    
    def resolve(self, notes=''):
        """Resolve alert"""
        self.status = 'resolved'
        self.resolution_notes = notes
        self.save()
    
    def mark_false_positive(self, notes=''):
        """Mark as false positive"""
        self.status = 'false_positive'
        self.resolution_notes = notes
        self.save()
    
    @classmethod
    def get_active_alerts(cls):
        """Get all active alerts"""
        return cls.objects.filter(status='active').order_by('-severity', '-alert_date')
    
    @classmethod
    def get_critical_alerts(cls):
        """Get critical active alerts"""
        return cls.objects.filter(
            status='active',
            severity='critical'
        ).order_by('-alert_date')
