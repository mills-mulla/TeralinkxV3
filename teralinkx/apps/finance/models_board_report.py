# apps/finance/models_board_report.py
from django.db import models
from django.utils import timezone
from datetime import timedelta
from core.models import TimeStampedModel


class BoardReport(TimeStampedModel):
    """Automated monthly board report"""
    
    REPORT_STATUS = [
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('approved', 'Approved'),
        ('distributed', 'Distributed')
    ]
    
    # Report Period
    report_month = models.DateField(db_index=True)
    report_year = models.IntegerField()
    
    # Report Sections (JSON data)
    financial_performance = models.JSONField(default=dict)
    customer_metrics = models.JSONField(default=dict)
    operational_metrics = models.JSONField(default=dict)
    risk_register = models.JSONField(default=dict)
    cash_flow_forecast = models.JSONField(default=dict)
    
    # Narrative Sections
    executive_summary = models.TextField(blank=True)
    key_highlights = models.JSONField(default=list)
    challenges = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    
    # Workflow
    status = models.CharField(max_length=20, choices=REPORT_STATUS, default='draft')
    generated_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_reports')
    reviewed_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_reports')
    approved_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_reports')
    
    reviewed_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    distributed_at = models.DateTimeField(null=True, blank=True)
    
    # Export Files
    pdf_file = models.FileField(upload_to='board_reports/pdf/', null=True, blank=True)
    pptx_file = models.FileField(upload_to='board_reports/pptx/', null=True, blank=True)
    
    # Metadata
    generation_time_seconds = models.IntegerField(default=0)
    
    class Meta:
        app_label = 'finance'
        ordering = ['-report_year', '-report_month']
        unique_together = ['report_year', 'report_month']
    
    def __str__(self):
        return f"Board Report - {self.report_month.strftime('%B %Y')}"
    
    @property
    def report_period_display(self):
        """Get formatted report period"""
        return self.report_month.strftime('%B %Y')
    
    @classmethod
    def get_latest(cls):
        """Get the latest board report"""
        return cls.objects.first()
    
    @classmethod
    def get_for_month(cls, year, month):
        """Get report for specific month"""
        return cls.objects.filter(report_year=year, report_month__month=month).first()
    
    def mark_reviewed(self, user):
        """Mark report as reviewed"""
        self.status = 'review'
        self.reviewed_by = user
        self.reviewed_at = timezone.now()
        self.save()
    
    def mark_approved(self, user):
        """Mark report as approved"""
        self.status = 'approved'
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save()
    
    def mark_distributed(self):
        """Mark report as distributed"""
        self.status = 'distributed'
        self.distributed_at = timezone.now()
        self.save()
