# apps/finance/models_billing.py
from django.db import models
from django.utils import timezone
from decimal import Decimal
from datetime import date
from core.models import TimeStampedModel


class RecurringBilling(TimeStampedModel):
    """Automated recurring billing for monthly packages."""

    STATUS_CHOICES = [
        ('active',   'Active'),
        ('paused',   'Paused'),
        ('cancelled','Cancelled'),
        ('failed',   'Failed — Max Retries'),
    ]

    customer        = models.OneToOneField('users.ClientH', on_delete=models.CASCADE,
                                           related_name='recurring_billing')
    package_name    = models.CharField(max_length=200)
    package_code    = models.CharField(max_length=50, blank=True)
    amount          = models.DecimalField(max_digits=12, decimal_places=2)
    billing_day     = models.IntegerField(default=1, help_text='Day of month to bill (1-28)')
    next_billing_date = models.DateField()
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    retry_count     = models.IntegerField(default=0)
    max_retries     = models.IntegerField(default=3)
    last_billed_at  = models.DateTimeField(null=True, blank=True)
    last_failed_at  = models.DateTimeField(null=True, blank=True)
    failure_reason  = models.TextField(blank=True)

    class Meta:
        app_label = 'finance'
        ordering = ['next_billing_date']
        indexes = [
            models.Index(fields=['status', 'next_billing_date']),
        ]

    def __str__(self):
        return f"{self.customer.account} — {self.package_name} — KES {self.amount}"

    def advance_billing_date(self):
        """Move next billing date to following month."""
        from datetime import date
        import calendar
        today = self.next_billing_date
        next_month = today.month + 1 if today.month < 12 else 1
        next_year = today.year if today.month < 12 else today.year + 1
        max_day = calendar.monthrange(next_year, next_month)[1]
        day = min(self.billing_day, max_day)
        self.next_billing_date = date(next_year, next_month, day)
        self.save()

    def mark_billed(self):
        self.last_billed_at = timezone.now()
        self.retry_count = 0
        self.failure_reason = ''
        self.advance_billing_date()

    def mark_failed(self, reason=''):
        self.retry_count += 1
        self.last_failed_at = timezone.now()
        self.failure_reason = reason
        if self.retry_count >= self.max_retries:
            self.status = 'failed'
        self.save()

    @classmethod
    def process_due_billings(cls):
        """Process all billings due today. Returns (success, failed) counts."""
        from finance.models import TransactionQueue
        today = date.today()
        due = cls.objects.filter(
            status='active',
            next_billing_date__lte=today
        )

        success = 0
        failed = 0

        for billing in due:
            customer = billing.customer
            try:
                # Check if customer has sufficient balance
                if customer.balance >= billing.amount:
                    # Deduct from balance
                    customer.balance -= billing.amount
                    customer.save()

                    # Create transaction record
                    TransactionQueue.objects.create(
                        user=customer,
                        method='balance',
                        initiator=customer.phone_number or customer.account,
                        package_code=billing.package_code or 'AUTO',
                        package=billing.package_name,
                        price=billing.amount,
                        status='completed',
                        queue_type='auto_renewal',
                        account_reference=customer.account,
                    )
                    billing.mark_billed()
                    success += 1
                else:
                    billing.mark_failed('Insufficient balance')
                    failed += 1
            except Exception as e:
                billing.mark_failed(str(e))
                failed += 1

        return success, failed
