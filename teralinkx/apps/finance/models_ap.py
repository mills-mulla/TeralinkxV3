# apps/finance/models_ap.py
from django.db import models
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
from core.models import TimeStampedModel


class VendorInvoice(TimeStampedModel):
    """Vendor invoice tracking for accounts payable."""

    STATUS_CHOICES = [
        ('received',  'Received'),
        ('approved',  'Approved'),
        ('scheduled', 'Payment Scheduled'),
        ('paid',      'Paid'),
        ('disputed',  'Disputed'),
        ('overdue',   'Overdue'),
    ]

    # Identity
    vendor_name     = models.CharField(max_length=200)
    vendor_pin      = models.CharField(max_length=20, blank=True)
    invoice_number  = models.CharField(max_length=100)
    our_reference   = models.CharField(max_length=50, blank=True)

    # Amounts
    subtotal        = models.DecimalField(max_digits=14, decimal_places=2)
    vat_amount      = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total           = models.DecimalField(max_digits=14, decimal_places=2)
    currency        = models.ForeignKey('finance.Currency', on_delete=models.PROTECT,
                                        null=True, blank=True)

    # Dates
    invoice_date    = models.DateField()
    due_date        = models.DateField()
    payment_date    = models.DateField(null=True, blank=True)

    # Category
    expense_category = models.CharField(max_length=20, blank=True)
    department      = models.ForeignKey('finance.Department', on_delete=models.SET_NULL,
                                        null=True, blank=True)

    # Status
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='received')
    approved_by     = models.ForeignKey('auth.User', on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='approved_vendor_invoices')
    notes           = models.TextField(blank=True)

    # WHT
    wht_applicable  = models.BooleanField(default=False)
    wht_amount      = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_payable     = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        app_label = 'finance'
        ordering = ['due_date']
        indexes = [
            models.Index(fields=['status', 'due_date']),
            models.Index(fields=['vendor_name']),
        ]

    def __str__(self):
        return f"{self.vendor_name} — {self.invoice_number} — KES {self.total}"

    def save(self, *args, **kwargs):
        # Auto-calculate WHT and net payable
        if self.wht_applicable:
            self.wht_amount = (self.subtotal * Decimal('0.06')).quantize(Decimal('0.01'))
        self.net_payable = self.total - self.wht_amount
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        return self.status not in ('paid',) and date.today() > self.due_date

    @property
    def days_overdue(self):
        if self.is_overdue:
            return (date.today() - self.due_date).days
        return 0

    @property
    def aging_bucket(self):
        if self.status == 'paid':
            return 'paid'
        days = (date.today() - self.due_date).days
        if days <= 0:
            return 'current'
        elif days <= 30:
            return '1_30'
        elif days <= 60:
            return '31_60'
        elif days <= 90:
            return '61_90'
        return 'over_90'

    def approve(self, user):
        self.status = 'approved'
        self.approved_by = user
        self.save()

    def mark_paid(self, payment_date=None):
        self.status = 'paid'
        self.payment_date = payment_date or date.today()
        self.save()

    @classmethod
    def get_aging_summary(cls):
        """Get AP aging summary by bucket."""
        invoices = cls.objects.exclude(status='paid')
        buckets = {'current': 0, '1_30': 0, '31_60': 0, '61_90': 0, 'over_90': 0}
        totals  = {'current': 0, '1_30': 0, '31_60': 0, '61_90': 0, 'over_90': 0}

        for inv in invoices:
            bucket = inv.aging_bucket
            if bucket in buckets:
                buckets[bucket] += 1
                totals[bucket] += float(inv.net_payable)

        return {
            'buckets': buckets,
            'totals': totals,
            'total_outstanding': sum(totals.values()),
            'total_invoices': sum(buckets.values()),
        }
