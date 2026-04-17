# apps/finance/models_vat.py
from django.db import models
from django.utils import timezone
from core.models import TimeStampedModel


class VATReturn(TimeStampedModel):
    """Monthly VAT return (VAT-3 form for KRA)"""

    STATUS_CHOICES = [
        ('draft',       'Draft'),
        ('calculated',  'Calculated'),
        ('filed',       'Filed with KRA'),
        ('paid',        'VAT Paid'),
    ]

    # Period
    period_month = models.IntegerField()
    period_year  = models.IntegerField()

    # Output VAT (VAT charged to customers on sales)
    output_vat   = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_sales  = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Input VAT (VAT paid on purchases/expenses)
    input_vat    = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_purchases = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Net VAT (output - input)
    net_vat      = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Status
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    filed_at     = models.DateTimeField(null=True, blank=True)
    paid_at      = models.DateTimeField(null=True, blank=True)

    # KRA reference
    kra_reference = models.CharField(max_length=50, blank=True)

    # Metadata
    calculated_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='vat_returns_calculated')
    filed_by      = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='vat_returns_filed')

    class Meta:
        app_label = 'finance'
        unique_together = ['period_year', 'period_month']
        ordering = ['-period_year', '-period_month']
        indexes = [
            models.Index(fields=['period_year', 'period_month']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"VAT Return {self.period_month}/{self.period_year} — KES {self.net_vat}"

    @classmethod
    def calculate_for_period(cls, year, month):
        """Calculate VAT return for a specific month."""
        from finance.models_invoice import Invoice
        from finance.models import Expense
        from django.db.models import Sum
        from datetime import date

        # Month boundaries
        start = date(year, month, 1)
        if month == 12:
            end = date(year + 1, 1, 1)
        else:
            end = date(year, month + 1, 1)

        # Output VAT (from invoices issued to customers)
        invoices = Invoice.objects.filter(
            issue_date__gte=start,
            issue_date__lt=end,
            status__in=['issued', 'paid']
        )
        output_vat = invoices.aggregate(total=Sum('vat_amount'))['total'] or 0
        total_sales = invoices.aggregate(total=Sum('total'))['total'] or 0

        # Input VAT (from expenses paid to suppliers)
        expenses = Expense.objects.filter(
            expense_date__gte=start,
            expense_date__lt=end,
            approval_status='paid'
        )
        input_vat = expenses.aggregate(total=Sum('tax_amount'))['total'] or 0
        total_purchases = expenses.aggregate(total=Sum('amount'))['total'] or 0

        # Net VAT payable
        net_vat = output_vat - input_vat

        # Create or update return
        vat_return, created = cls.objects.update_or_create(
            period_year=year,
            period_month=month,
            defaults={
                'output_vat': output_vat,
                'total_sales': total_sales,
                'input_vat': input_vat,
                'total_purchases': total_purchases,
                'net_vat': net_vat,
                'status': 'calculated'
            }
        )

        return vat_return

    def mark_filed(self, user, kra_reference=''):
        """Mark VAT return as filed with KRA."""
        self.status = 'filed'
        self.filed_by = user
        self.filed_at = timezone.now()
        self.kra_reference = kra_reference
        self.save()

    def mark_paid(self):
        """Mark VAT as paid."""
        self.status = 'paid'
        self.paid_at = timezone.now()
        self.save()
