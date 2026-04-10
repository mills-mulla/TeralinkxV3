"""
Churn Prediction Models
Tracks customer churn risk with rule-based and ML predictions.
"""
from django.db import models
from django.utils import timezone
from datetime import timedelta
from core.models import TimeStampedModel


class ChurnPrediction(TimeStampedModel):
    """
    Customer churn prediction with risk scoring and explanation.
    Supports both rule-based and ML-based predictions.
    """
    
    RISK_LEVEL_CHOICES = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk'),
    ]
    
    PREDICTION_METHOD_CHOICES = [
        ('rule_based', 'Rule-Based Model'),
        ('ml_model', 'Machine Learning Model'),
        ('hybrid', 'Hybrid (Rule + ML)'),
    ]
    
    # Customer reference
    customer = models.ForeignKey(
        'users.ClientH',
        on_delete=models.CASCADE,
        related_name='churn_predictions'
    )
    
    # Prediction details
    churn_score = models.FloatField(
        help_text="Churn probability (0-1)"
    )
    risk_level = models.CharField(
        max_length=20,
        choices=RISK_LEVEL_CHOICES
    )
    prediction_method = models.CharField(
        max_length=20,
        choices=PREDICTION_METHOD_CHOICES,
        default='rule_based'
    )
    
    # Risk factors (JSON for flexibility)
    risk_factors = models.JSONField(
        default=dict,
        help_text="Contributing factors with scores"
    )
    top_factors = models.JSONField(
        default=list,
        help_text="Top 3 factors driving churn risk"
    )
    
    # Customer metrics snapshot
    days_since_last_session = models.IntegerField(null=True, blank=True)
    support_tickets_90d = models.IntegerField(default=0)
    late_payments_count = models.IntegerField(default=0)
    package_downgrades_count = models.IntegerField(default=0)
    avg_session_duration_minutes = models.FloatField(null=True, blank=True)
    monthly_recurring_revenue = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # ML model reference
    ml_model = models.ForeignKey(
        'finance.MLModel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="ML model used for prediction"
    )
    
    # Prediction metadata
    prediction_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(
        default=True,
        help_text="Most recent prediction for customer"
    )
    confidence = models.FloatField(
        null=True,
        blank=True,
        help_text="Model confidence (0-1)"
    )
    
    # Outcome tracking
    actual_churned = models.BooleanField(
        null=True,
        blank=True,
        help_text="Did customer actually churn?"
    )
    churned_date = models.DateField(null=True, blank=True)
    
    class Meta:
        app_label = 'finance'
        verbose_name = "Churn Prediction"
        verbose_name_plural = "Churn Predictions"
        ordering = ['-prediction_date']
        indexes = [
            models.Index(fields=['customer', 'is_active']),
            models.Index(fields=['risk_level', 'prediction_date']),
            models.Index(fields=['churn_score']),
        ]
    
    def __str__(self):
        return f"{self.customer.account} - {self.risk_level} ({self.churn_score:.2f})"
    
    @classmethod
    def calculate_rule_based_score(cls, customer):
        """
        Calculate churn score using rule-based model.
        Returns score (0-1) and risk factors.
        """
        score = 0.0
        factors = {}
        
        # Factor 1: Days since last session (40% weight)
        days_inactive = cls._get_days_since_last_session(customer)
        if days_inactive is not None:
            if days_inactive > 60:
                session_score = 0.40
            elif days_inactive > 30:
                session_score = 0.30
            elif days_inactive > 14:
                session_score = 0.20
            elif days_inactive > 7:
                session_score = 0.10
            else:
                session_score = 0.0
            
            score += session_score
            factors['days_since_last_session'] = {
                'value': days_inactive,
                'score': session_score,
                'weight': 0.40
            }
        
        # Factor 2: Support tickets (20% weight)
        support_tickets = cls._get_support_tickets_count(customer)
        if support_tickets >= 5:
            ticket_score = 0.20
        elif support_tickets >= 3:
            ticket_score = 0.15
        elif support_tickets >= 1:
            ticket_score = 0.10
        else:
            ticket_score = 0.0
        
        score += ticket_score
        factors['support_tickets_90d'] = {
            'value': support_tickets,
            'score': ticket_score,
            'weight': 0.20
        }
        
        # Factor 3: Late payments (20% weight)
        late_payments = cls._get_late_payments_count(customer)
        if late_payments >= 3:
            payment_score = 0.20
        elif late_payments >= 2:
            payment_score = 0.15
        elif late_payments >= 1:
            payment_score = 0.10
        else:
            payment_score = 0.0
        
        score += payment_score
        factors['late_payments'] = {
            'value': late_payments,
            'score': payment_score,
            'weight': 0.20
        }
        
        # Factor 4: Package downgrades (20% weight)
        downgrades = cls._get_package_downgrades_count(customer)
        if downgrades >= 2:
            downgrade_score = 0.20
        elif downgrades >= 1:
            downgrade_score = 0.15
        else:
            downgrade_score = 0.0
        
        score += downgrade_score
        factors['package_downgrades'] = {
            'value': downgrades,
            'score': downgrade_score,
            'weight': 0.20
        }
        
        return min(score, 1.0), factors
    
    @classmethod
    def _get_days_since_last_session(cls, customer):
        """Get days since customer's last session"""
        # TODO: Implement actual session lookup
        # For now, return None
        return None
    
    @classmethod
    def _get_support_tickets_count(cls, customer):
        """Get support ticket count in last 90 days"""
        # TODO: Implement actual ticket lookup
        return 0
    
    @classmethod
    def _get_late_payments_count(cls, customer):
        """Get late payment count"""
        # TODO: Implement actual payment history lookup
        return 0
    
    @classmethod
    def _get_package_downgrades_count(cls, customer):
        """Get package downgrade count"""
        # TODO: Implement actual package history lookup
        return 0
    
    @classmethod
    def get_risk_level(cls, score):
        """Convert score to risk level"""
        if score >= 0.70:
            return 'critical'
        elif score >= 0.50:
            return 'high'
        elif score >= 0.30:
            return 'medium'
        else:
            return 'low'
    
    @classmethod
    def get_top_factors(cls, factors):
        """Get top 3 contributing factors"""
        sorted_factors = sorted(
            factors.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        return [
            {
                'factor': factor,
                'value': data['value'],
                'score': data['score']
            }
            for factor, data in sorted_factors[:3]
        ]
    
    @classmethod
    def create_prediction(cls, customer, method='rule_based'):
        """Create new churn prediction for customer"""
        # Deactivate previous predictions
        cls.objects.filter(customer=customer, is_active=True).update(is_active=False)
        
        # Calculate score
        if method == 'rule_based':
            score, factors = cls.calculate_rule_based_score(customer)
        else:
            # TODO: Implement ML prediction
            score, factors = cls.calculate_rule_based_score(customer)
        
        # Determine risk level
        risk_level = cls.get_risk_level(score)
        
        # Get top factors
        top_factors = cls.get_top_factors(factors)
        
        # Create prediction
        prediction = cls.objects.create(
            customer=customer,
            churn_score=score,
            risk_level=risk_level,
            prediction_method=method,
            risk_factors=factors,
            top_factors=top_factors,
            is_active=True
        )
        
        return prediction
    
    def mark_churned(self, churned_date=None):
        """Mark customer as actually churned"""
        self.actual_churned = True
        self.churned_date = churned_date or timezone.now().date()
        self.save()
    
    def mark_retained(self):
        """Mark customer as retained"""
        self.actual_churned = False
        self.save()


class RetentionTask(TimeStampedModel):
    """
    Automated retention tasks for at-risk customers.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    ACTION_TYPE_CHOICES = [
        ('auto_discount_20', 'Auto-Apply 20% Discount'),
        ('sms_discount_10', 'SMS with 10% Offer'),
        ('sms_reengagement', 'Re-engagement SMS'),
        ('manual_outreach', 'Manual Account Manager Outreach'),
    ]
    
    OUTCOME_CHOICES = [
        ('pending', 'Pending'),
        ('retained', 'Customer Retained'),
        ('churned', 'Customer Churned'),
        ('relocated', 'Customer Relocated'),
        ('no_response', 'No Response'),
    ]
    
    # Customer and prediction
    customer = models.ForeignKey(
        'users.ClientH',
        on_delete=models.CASCADE,
        related_name='retention_tasks'
    )
    churn_prediction = models.ForeignKey(
        ChurnPrediction,
        on_delete=models.CASCADE,
        related_name='retention_tasks'
    )
    
    # Task details
    action_type = models.CharField(max_length=30, choices=ACTION_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority_score = models.FloatField(
        help_text="Priority based on MRR and churn score"
    )
    
    # Customer value
    monthly_recurring_revenue = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    revenue_at_risk = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Estimated revenue loss if churned"
    )
    
    # Action tracking
    action_taken_at = models.DateTimeField(null=True, blank=True)
    action_details = models.JSONField(
        default=dict,
        help_text="Details of action taken (SMS sent, discount applied, etc.)"
    )
    
    # Outcome tracking
    outcome = models.CharField(
        max_length=20,
        choices=OUTCOME_CHOICES,
        default='pending'
    )
    outcome_date = models.DateField(null=True, blank=True)
    outcome_notes = models.TextField(blank=True)
    
    # Automation metadata
    automated = models.BooleanField(
        default=True,
        help_text="Was this action automated?"
    )
    assigned_to = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Account manager assigned (for manual tasks)"
    )
    
    class Meta:
        app_label = 'finance'
        verbose_name = "Retention Task"
        verbose_name_plural = "Retention Tasks"
        ordering = ['-priority_score', '-created_at']
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['status', 'priority_score']),
            models.Index(fields=['outcome']),
        ]
    
    def __str__(self):
        return f"{self.customer.account} - {self.action_type} ({self.status})"
    
    @classmethod
    def calculate_priority_score(cls, mrr, churn_score):
        """Calculate priority score based on MRR and churn risk"""
        # Normalize MRR (assuming max 10K KES/month)
        mrr_normalized = min(float(mrr) / 10000, 1.0)
        
        # Priority = (MRR weight * MRR) + (Churn weight * Churn Score)
        # 60% weight on MRR, 40% on churn score
        priority = (0.6 * mrr_normalized) + (0.4 * churn_score)
        
        return priority
    
    @classmethod
    def create_retention_task(cls, churn_prediction):
        """Create retention task based on churn prediction"""
        customer = churn_prediction.customer
        mrr = churn_prediction.monthly_recurring_revenue or 0
        
        # Determine action type based on MRR
        if mrr >= 5000:  # High-value (>KES 5K/month)
            action_type = 'auto_discount_20'
        elif mrr >= 2000:  # Medium-value
            action_type = 'sms_discount_10'
        else:  # Low-value
            action_type = 'sms_reengagement'
        
        # Calculate priority
        priority_score = cls.calculate_priority_score(mrr, churn_prediction.churn_score)
        
        # Estimate revenue at risk (6 months MRR)
        revenue_at_risk = mrr * 6
        
        # Create task
        task = cls.objects.create(
            customer=customer,
            churn_prediction=churn_prediction,
            action_type=action_type,
            priority_score=priority_score,
            monthly_recurring_revenue=mrr,
            revenue_at_risk=revenue_at_risk,
            automated=True
        )
        
        return task
    
    def execute_action(self):
        """Execute the retention action"""
        if self.status != 'pending':
            return False
        
        self.status = 'in_progress'
        self.save()
        
        try:
            if self.action_type == 'auto_discount_20':
                self._apply_discount(20)
            elif self.action_type == 'sms_discount_10':
                self._send_sms_offer(10)
            elif self.action_type == 'sms_reengagement':
                self._send_reengagement_sms()
            
            self.status = 'completed'
            self.action_taken_at = timezone.now()
            self.save()
            return True
            
        except Exception as e:
            self.status = 'failed'
            self.action_details['error'] = str(e)
            self.save()
            return False
    
    def _apply_discount(self, percentage):
        """Apply discount to customer account"""
        # TODO: Implement discount application
        self.action_details['discount_applied'] = f"{percentage}%"
        self.action_details['applied_at'] = timezone.now().isoformat()
    
    def _send_sms_offer(self, discount_percentage):
        """Send SMS with discount offer"""
        # TODO: Implement SMS sending via Twilio/Africa's Talking
        message = f"Hi {self.customer.account}, we value you! Get {discount_percentage}% off your next package. Reply YES to claim."
        self.action_details['sms_sent'] = message
        self.action_details['sent_at'] = timezone.now().isoformat()
    
    def _send_reengagement_sms(self):
        """Send re-engagement SMS"""
        # TODO: Implement SMS sending
        message = f"Hi {self.customer.account}, we miss you! Check out our latest packages and special offers."
        self.action_details['sms_sent'] = message
        self.action_details['sent_at'] = timezone.now().isoformat()
    
    def mark_outcome(self, outcome, notes=''):
        """Mark task outcome"""
        self.outcome = outcome
        self.outcome_date = timezone.now().date()
        self.outcome_notes = notes
        self.save()
        
        # Update churn prediction
        if outcome == 'retained':
            self.churn_prediction.mark_retained()
        elif outcome in ['churned', 'relocated']:
            self.churn_prediction.mark_churned()
