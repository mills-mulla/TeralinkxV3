# apps/finance/models_tax.py
from django.db import models
from django.utils import timezone
from datetime import date
from decimal import Decimal
from core.models import TimeStampedModel


class TaxReturn(TimeStampedModel):
    """KRA tax return tracking — PAYE, VAT, WHT, Income Tax"""

    TAX_TYPES = [
        ('vat',          'VAT (Value Added Tax)'),
        ('paye',         'PAYE (Pay As You Earn)'),
        ('wht',          'Withholding Tax'),
        ('income_tax',   'Corporate Income Tax'),
        ('nssf',         'NSSF Contributions'),
        ('nhif',         'NHIF Contributions'),
    ]

    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('calculated','Calculated'),
        ('filed',     'Filed'),
        ('paid',      'Paid'),
        ('overdue',   'Overdue'),
    ]

    tax_type        = models.CharField(max_length=20, choices=TAX_TYPES)
    period_month    = models.IntegerField(null=True, blank=True)
    period_year     = models.IntegerField()
    period_label    = models.CharField(max_length=30)  # e.g. "April 2026" or "FY 2026"

    # Amounts
    gross_amount    = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tax_amount      = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    penalties       = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_payable   = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    # Dates
    due_date        = models.DateField()
    filed_date      = models.DateField(null=True, blank=True)
    paid_date       = models.DateField(null=True, blank=True)

    # Status
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # KRA
    kra_reference   = models.CharField(max_length=50, blank=True)
    payment_slip    = models.CharField(max_length=100, blank=True)
    notes           = models.TextField(blank=True)

    filed_by        = models.ForeignKey('auth.User', on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='tax_returns_filed')

    class Meta:
        app_label = 'finance'
        ordering = ['-period_year', '-period_month']
        indexes = [
            models.Index(fields=['tax_type', 'period_year', 'period_month']),
            models.Index(fields=['status', 'due_date']),
        ]

    def __str__(self):
        return f"{self.get_tax_type_display()} — {self.period_label} — KES {self.tax_amount}"

    @property
    def is_overdue(self):
        return self.status not in ('filed', 'paid') and date.today() > self.due_date

    @property
    def days_until_due(self):
        return (self.due_date - date.today()).days

    def mark_filed(self, user, kra_reference=''):
        self.status = 'filed'
        self.filed_by = user
        self.filed_date = date.today()
        self.kra_reference = kra_reference
        self.save()

    def mark_paid(self, payment_slip=''):
        self.status = 'paid'
        self.paid_date = date.today()
        self.payment_slip = payment_slip
        self.save()

    @classmethod
    def generate_calendar(cls, year):
        """Generate full tax calendar for a year with all filing deadlines."""
        from calendar import monthrange
        entries = []

        for month in range(1, 13):
            month_name = date(year, month, 1).strftime('%B %Y')
            # Due date: 20th of following month for VAT and PAYE
            if month == 12:
                due = date(year + 1, 1, 20)
            else:
                due = date(year, month + 1, 20)

            for tax_type in ['vat', 'paye', 'nssf', 'nhif']:
                obj, _ = cls.objects.get_or_create(
                    tax_type=tax_type,
                    period_year=year,
                    period_month=month,
                    defaults={
                        'period_label': month_name,
                        'due_date': due,
                        'status': 'pending'
                    }
                )
                entries.append(obj)

        # Annual income tax — due 30 June following year
        obj, _ = cls.objects.get_or_create(
            tax_type='income_tax',
            period_year=year,
            period_month=None,
            defaults={
                'period_label': f'FY {year}',
                'due_date': date(year + 1, 6, 30),
                'status': 'pending'
            }
        )
        entries.append(obj)

        return entries

    @classmethod
    def get_upcoming(cls, days=30):
        """Get tax returns due within next N days."""
        today = date.today()
        cutoff = date(today.year, today.month + 1 if today.month < 12 else 1,
                      today.day) if days > 30 else date.fromordinal(today.toordinal() + days)
        return cls.objects.filter(
            due_date__gte=today,
            due_date__lte=date.fromordinal(today.toordinal() + days),
            status__in=['pending', 'calculated']
        ).order_by('due_date')

    @classmethod
    def calculate_wht(cls, year, month):
        """Calculate withholding tax on vendor payments (6% on services)."""
        from finance.models import Expense
        from django.db.models import Sum
        from datetime import date as d

        start = d(year, month, 1)
        end_month = month + 1 if month < 12 else 1
        end_year = year if month < 12 else year + 1
        end = d(end_year, end_month, 1)

        # WHT applies to service expenses paid to vendors
        service_categories = ['network', 'software', 'maintenance', 'other']
        vendor_payments = Expense.objects.filter(
            expense_date__gte=start,
            expense_date__lt=end,
            approval_status='paid',
            category__in=service_categories
        ).aggregate(total=Sum('amount'))['total'] or 0

        wht_amount = vendor_payments * Decimal('0.06')  # 6% WHT on services

        if month == 12:
            due = d(year + 1, 1, 20)
        else:
            due = d(year, month + 1, 20)

        obj, _ = cls.objects.update_or_create(
            tax_type='wht',
            period_year=year,
            period_month=month,
            defaults={
                'period_label': d(year, month, 1).strftime('%B %Y'),
                'gross_amount': vendor_payments,
                'tax_amount': wht_amount,
                'total_payable': wht_amount,
                'due_date': due,
                'status': 'calculated'
            }
        )
        return obj
