# apps/finance/models_ar.py
from django.db import models
from django.utils import timezone
from decimal import Decimal
from datetime import date
from core.models import TimeStampedModel


class ARAccount(TimeStampedModel):
    """Accounts receivable tracking per customer."""

    customer        = models.OneToOneField('users.ClientH', on_delete=models.CASCADE,
                                           related_name='ar_account')
    total_invoiced  = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_paid      = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_credited  = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    outstanding     = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    last_payment_date = models.DateField(null=True, blank=True)
    last_updated    = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'finance'

    def __str__(self):
        return f"{self.customer.account} — Outstanding KES {self.outstanding}"

    def recalculate(self):
        from finance.models_invoice import Invoice
        invoices = Invoice.objects.filter(customer=self.customer, status__in=['issued', 'paid'])
        self.total_invoiced = sum(i.total for i in invoices)
        paid = Invoice.objects.filter(customer=self.customer, status='paid')
        self.total_paid = sum(i.total for i in paid)
        self.outstanding = self.total_invoiced - self.total_paid - self.total_credited
        last = paid.order_by('-issue_date').first()
        if last:
            self.last_payment_date = last.issue_date
        self.save()

    @property
    def aging_bucket(self):
        if self.outstanding <= 0:
            return 'current'
        if not self.last_payment_date:
            return 'over_90'
        days = (date.today() - self.last_payment_date).days
        if days <= 30:
            return 'current'
        elif days <= 60:
            return '31_60'
        elif days <= 90:
            return '61_90'
        return 'over_90'


class DebtCollection(TimeStampedModel):
    """Debt collection case for overdue customers."""

    STATUS_CHOICES = [
        ('open',        'Open'),
        ('in_progress', 'In Progress'),
        ('resolved',    'Resolved — Paid'),
        ('written_off', 'Written Off'),
        ('suspended',   'Service Suspended'),
    ]

    ESCALATION_CHOICES = [
        ('reminder',    'Payment Reminder'),
        ('warning',     'Formal Warning'),
        ('suspension',  'Service Suspension'),
        ('legal',       'Legal Action'),
    ]

    customer        = models.ForeignKey('users.ClientH', on_delete=models.CASCADE,
                                        related_name='debt_collections')
    amount_overdue  = models.DecimalField(max_digits=14, decimal_places=2)
    days_overdue    = models.IntegerField(default=0)
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    escalation_level = models.CharField(max_length=20, choices=ESCALATION_CHOICES, default='reminder')

    assigned_to     = models.ForeignKey('auth.User', on_delete=models.SET_NULL,
                                        null=True, blank=True)
    notes           = models.TextField(blank=True)
    resolved_at     = models.DateTimeField(null=True, blank=True)
    write_off_approved_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL,
                                               null=True, blank=True,
                                               related_name='approved_write_offs')

    class Meta:
        app_label = 'finance'
        ordering = ['-amount_overdue']
        indexes = [
            models.Index(fields=['status', 'days_overdue']),
            models.Index(fields=['customer']),
        ]

    def __str__(self):
        return f"{self.customer.account} — KES {self.amount_overdue} — {self.days_overdue}d overdue"

    def escalate(self):
        """Move to next escalation level."""
        levels = ['reminder', 'warning', 'suspension', 'legal']
        idx = levels.index(self.escalation_level)
        if idx < len(levels) - 1:
            self.escalation_level = levels[idx + 1]
            self.save()
        return self.escalation_level

    def resolve(self):
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.save()

    def write_off(self, approved_by):
        self.status = 'written_off'
        self.write_off_approved_by = approved_by
        self.resolved_at = timezone.now()
        self.save()

    @classmethod
    def get_aging_summary(cls):
        """AR aging summary across all customers."""
        from users.models import ClientH
        from finance.models_invoice import Invoice
        from django.db.models import Sum

        buckets = {'current': 0, '31_60': 0, '61_90': 0, 'over_90': 0}
        totals  = {'current': 0, '31_60': 0, '61_90': 0, 'over_90': 0}

        # Get all customers with outstanding invoices
        outstanding = Invoice.objects.filter(
            status='issued'
        ).values('customer_id').annotate(total=Sum('total'))

        for item in outstanding:
            try:
                ar = ARAccount.objects.get(customer_id=item['customer_id'])
                bucket = ar.aging_bucket
            except ARAccount.DoesNotExist:
                bucket = 'current'

            if bucket in buckets:
                buckets[bucket] += 1
                totals[bucket] += float(item['total'])

        return {
            'buckets': buckets,
            'totals': totals,
            'total_outstanding': sum(totals.values()),
            'total_customers': sum(buckets.values()),
        }

    @classmethod
    def create_collection_cases(cls):
        """Create collection cases for overdue customers. Called by Celery task."""
        from finance.models_invoice import Invoice
        from django.db.models import Sum

        today = date.today()
        created = 0

        overdue_invoices = Invoice.objects.filter(
            status='issued',
            due_date__lt=today
        ).values('customer_id').annotate(total=Sum('total'))

        for item in overdue_invoices:
            customer_id = item['customer_id']
            amount = item['total']

            # Get oldest unpaid invoice for days_overdue
            oldest = Invoice.objects.filter(
                customer_id=customer_id, status='issued'
            ).order_by('due_date').first()

            days = (today - oldest.due_date).days if oldest and oldest.due_date else 0

            # Create or update collection case
            case, made = cls.objects.update_or_create(
                customer_id=customer_id,
                status__in=['open', 'in_progress'],
                defaults={
                    'amount_overdue': amount,
                    'days_overdue': days,
                    'status': 'open',
                    'escalation_level': 'reminder' if days <= 14 else
                                        'warning' if days <= 30 else
                                        'suspension' if days <= 60 else 'legal'
                }
            )
            if made:
                created += 1

        return created
