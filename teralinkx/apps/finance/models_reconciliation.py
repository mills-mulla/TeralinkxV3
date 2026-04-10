"""
Reconciliation Models
Automated payment reconciliation with confidence scoring.
"""
from django.db import models
from django.utils import timezone
from core.models import TimeStampedModel


class ReconciliationJob(TimeStampedModel):
    """
    Reconciliation job tracking for batch processing.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    # Job metadata
    job_id = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Processing details
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    processing_duration = models.DurationField(null=True, blank=True)
    
    # Data scope
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Results
    total_items = models.IntegerField(default=0)
    matched_items = models.IntegerField(default=0)
    unmatched_items = models.IntegerField(default=0)
    review_items = models.IntegerField(default=0)
    
    # Performance metrics
    auto_match_rate = models.FloatField(
        null=True,
        blank=True,
        help_text="Percentage of items auto-matched"
    )
    average_confidence = models.FloatField(
        null=True,
        blank=True,
        help_text="Average confidence score"
    )
    
    # Error tracking
    error_message = models.TextField(blank=True)
    
    # User
    initiated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    class Meta:
        app_label = 'finance'
        verbose_name = "Reconciliation Job"
        verbose_name_plural = "Reconciliation Jobs"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['job_id']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"Job {self.job_id} - {self.status}"
    
    def start_processing(self):
        """Mark job as processing"""
        self.status = 'processing'
        self.started_at = timezone.now()
        self.save()
    
    def complete(self):
        """Mark job as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if self.started_at:
            self.processing_duration = self.completed_at - self.started_at
        
        # Calculate metrics
        if self.total_items > 0:
            self.auto_match_rate = (self.matched_items / self.total_items) * 100
        
        self.save()
    
    def fail(self, error_message):
        """Mark job as failed"""
        self.status = 'failed'
        self.error_message = error_message
        self.completed_at = timezone.now()
        self.save()


class ReconciliationMatch(TimeStampedModel):
    """
    Individual reconciliation match with confidence scoring.
    """
    
    MATCH_ACTION_CHOICES = [
        ('auto', 'Auto-Matched'),
        ('review', 'Needs Review'),
        ('manual', 'Manual Match'),
        ('rejected', 'Rejected'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('matched', 'Matched'),
        ('unmatched', 'Unmatched'),
        ('reviewed', 'Reviewed'),
    ]
    
    # Job reference
    job = models.ForeignKey(
        ReconciliationJob,
        on_delete=models.CASCADE,
        related_name='matches'
    )
    
    # Source data (bank statement/external)
    source_reference = models.CharField(max_length=200)
    source_amount = models.DecimalField(max_digits=15, decimal_places=2)
    source_date = models.DateField()
    source_customer_info = models.CharField(
        max_length=200,
        blank=True,
        help_text="Customer name/phone from source"
    )
    source_description = models.TextField(blank=True)
    
    # Matched transaction (using transaction_id which is unique)
    transaction_id_ref = models.CharField(
        max_length=255,
        blank=True,
        help_text="Transaction ID reference"
    )
    
    # Matching details
    match_action = models.CharField(
        max_length=20,
        choices=MATCH_ACTION_CHOICES,
        default='review'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Confidence scoring
    confidence_score = models.FloatField(
        help_text="Overall confidence (0-1)"
    )
    amount_match_score = models.FloatField(
        help_text="Amount matching score (0-1)"
    )
    customer_match_score = models.FloatField(
        help_text="Customer matching score (0-1)"
    )
    date_match_score = models.FloatField(
        help_text="Date proximity score (0-1)"
    )
    
    # Match explanation
    match_factors = models.JSONField(
        default=dict,
        help_text="Detailed matching factors"
    )
    
    # Review tracking
    reviewed_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_matches'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    class Meta:
        app_label = 'finance'
        verbose_name = "Reconciliation Match"
        verbose_name_plural = "Reconciliation Matches"
        ordering = ['-confidence_score', '-created_at']
        indexes = [
            models.Index(fields=['job', 'match_action']),
            models.Index(fields=['status', 'confidence_score']),
            models.Index(fields=['source_reference']),
        ]
    
    def __str__(self):
        return f"{self.source_reference} - {self.confidence_score:.2f}"
    
    @property
    def transaction(self):
        """Get related transaction"""
        if self.transaction_id_ref:
            from finance.models import PaymentTransaction
            try:
                return PaymentTransaction.objects.get(transaction_id=self.transaction_id_ref)
            except PaymentTransaction.DoesNotExist:
                return None
        return None
    
    @property
    def needs_review(self):
        """Check if match needs manual review"""
        return self.match_action == 'review'
    
    @property
    def is_auto_matched(self):
        """Check if auto-matched"""
        return self.match_action == 'auto'
    
    def approve_match(self, user):
        """Approve match after review"""
        self.status = 'matched'
        self.match_action = 'manual'
        self.reviewed_by = user
        self.reviewed_at = timezone.now()
        self.save()
    
    def reject_match(self, user, notes=''):
        """Reject match"""
        self.status = 'unmatched'
        self.match_action = 'rejected'
        self.reviewed_by = user
        self.reviewed_at = timezone.now()
        self.review_notes = notes
        self.transaction_id_ref = ''
        self.save()
    
    @classmethod
    def get_review_queue(cls, job=None):
        """Get items needing review"""
        queryset = cls.objects.filter(
            match_action='review',
            status='pending'
        ).order_by('-confidence_score', '-source_amount')
        
        if job:
            queryset = queryset.filter(job=job)
        
        return queryset
    
    @classmethod
    def get_unmatched_items(cls, job=None):
        """Get unmatched items"""
        queryset = cls.objects.filter(
            status='unmatched'
        ).order_by('-source_amount', '-source_date')
        
        if job:
            queryset = queryset.filter(job=job)
        
        return queryset


class ReconciliationRule(TimeStampedModel):
    """
    Custom reconciliation rules for specific scenarios.
    """
    
    RULE_TYPE_CHOICES = [
        ('amount_tolerance', 'Amount Tolerance'),
        ('date_range', 'Date Range'),
        ('customer_mapping', 'Customer Mapping'),
        ('auto_match_threshold', 'Auto-Match Threshold'),
    ]
    
    # Rule details
    name = models.CharField(max_length=100)
    rule_type = models.CharField(max_length=30, choices=RULE_TYPE_CHOICES)
    description = models.TextField(blank=True)
    
    # Rule configuration
    config = models.JSONField(
        default=dict,
        help_text="Rule-specific configuration"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(
        default=0,
        help_text="Higher priority rules applied first"
    )
    
    # Usage tracking
    times_applied = models.IntegerField(default=0)
    last_applied = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        app_label = 'finance'
        verbose_name = "Reconciliation Rule"
        verbose_name_plural = "Reconciliation Rules"
        ordering = ['-priority', 'name']
        indexes = [
            models.Index(fields=['rule_type', 'is_active']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_rule_type_display()})"
    
    def apply(self):
        """Mark rule as applied"""
        self.times_applied += 1
        self.last_applied = timezone.now()
        self.save()
    
    @classmethod
    def get_active_rules(cls, rule_type=None):
        """Get active rules"""
        queryset = cls.objects.filter(is_active=True).order_by('-priority')
        
        if rule_type:
            queryset = queryset.filter(rule_type=rule_type)
        
        return queryset
