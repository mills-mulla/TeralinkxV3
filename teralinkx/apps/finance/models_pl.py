# apps/finance/models_pl.py
from django.db import models
from django.utils import timezone
from decimal import Decimal
from core.models import TimeStampedModel


class ForexGainLoss(TimeStampedModel):
    """Tracks forex gain/loss on foreign currency transactions."""

    TRANSACTION_TYPES = [
        ('expense',  'Expense in Foreign Currency'),
        ('payment',  'Payment Received in Foreign Currency'),
        ('invoice',  'Invoice in Foreign Currency'),
    ]

    transaction_ref     = models.CharField(max_length=100)
    transaction_type    = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    transaction_date    = models.DateField()

    original_currency   = models.ForeignKey('finance.Currency', on_delete=models.PROTECT,
                                             related_name='forex_originals')
    original_amount     = models.DecimalField(max_digits=14, decimal_places=2)
    exchange_rate_used  = models.DecimalField(max_digits=15, decimal_places=6)
    kes_amount          = models.DecimalField(max_digits=14, decimal_places=2)

    # Settlement rate (when actually paid/received)
    settlement_rate     = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True)
    settlement_kes      = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    # Gain = positive, Loss = negative
    gain_loss           = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    is_realized         = models.BooleanField(default=False)

    description         = models.TextField(blank=True)

    class Meta:
        app_label = 'finance'
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['transaction_date', 'original_currency']),
            models.Index(fields=['is_realized']),
        ]

    def __str__(self):
        direction = 'Gain' if self.gain_loss >= 0 else 'Loss'
        return f"Forex {direction} KES {abs(self.gain_loss)} — {self.transaction_ref}"

    def realize(self, settlement_rate):
        """Record actual settlement and calculate realized gain/loss."""
        self.settlement_rate = settlement_rate
        self.settlement_kes = (self.original_amount * settlement_rate).quantize(Decimal('0.01'))
        self.gain_loss = self.settlement_kes - self.kes_amount
        self.is_realized = True
        self.save()


class PLStatement(TimeStampedModel):
    """Pre-computed P&L statement for a period."""

    PERIOD_TYPES = [
        ('monthly',   'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual',    'Annual'),
    ]

    period_type     = models.CharField(max_length=20, choices=PERIOD_TYPES)
    period_start    = models.DateField()
    period_end      = models.DateField()
    period_label    = models.CharField(max_length=50)

    # Revenue
    gross_revenue   = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    vat_collected   = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    net_revenue     = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    # Expenses
    total_expenses  = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    depreciation    = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    payroll_cost    = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    # Forex
    forex_gain_loss = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    # Profit
    gross_profit    = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    net_profit      = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    profit_margin   = models.FloatField(default=0)

    # Breakdown JSON
    expense_breakdown = models.JSONField(default=dict)
    revenue_breakdown = models.JSONField(default=dict)

    class Meta:
        app_label = 'finance'
        ordering = ['-period_start']
        unique_together = ['period_type', 'period_start', 'period_end']

    def __str__(self):
        return f"P&L {self.period_label} — Net KES {self.net_profit}"

    @classmethod
    def generate(cls, year, month=None, quarter=None):
        """Generate P&L statement for a period."""
        from finance.models import TransactionQueue, Expense
        from finance.models_payroll import PayrollRun
        from django.db.models import Sum
        from datetime import date

        if month:
            period_type = 'monthly'
            start = date(year, month, 1)
            end_month = month + 1 if month < 12 else 1
            end_year = year if month < 12 else year + 1
            end = date(end_year, end_month, 1)
            label = date(year, month, 1).strftime('%B %Y')
        elif quarter:
            period_type = 'quarterly'
            start_month = (quarter - 1) * 3 + 1
            start = date(year, start_month, 1)
            end_month = start_month + 3 if start_month + 3 <= 12 else 1
            end_year = year if start_month + 3 <= 12 else year + 1
            end = date(end_year, end_month, 1)
            label = f'Q{quarter} {year}'
        else:
            period_type = 'annual'
            start = date(year, 1, 1)
            end = date(year + 1, 1, 1)
            label = f'FY {year}'

        # Revenue from completed transactions
        gross_revenue = TransactionQueue.objects.filter(
            status__in=['completed', 'processed'],
            created_at__date__gte=start,
            created_at__date__lt=end
        ).aggregate(total=Sum('price'))['total'] or Decimal('0')

        # VAT collected (16/116 of gross)
        vat_collected = (gross_revenue * Decimal('16') / Decimal('116')).quantize(Decimal('0.01'))
        net_revenue = gross_revenue - vat_collected

        # Expenses by category
        expenses_qs = Expense.objects.filter(
            expense_date__gte=start,
            expense_date__lt=end,
            approval_status='paid'
        )
        total_expenses = expenses_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0')

        expense_breakdown = {}
        for cat_data in expenses_qs.values('category').annotate(total=Sum('amount')):
            expense_breakdown[cat_data['category']] = float(cat_data['total'])

        # Depreciation from expenses
        depreciation = Expense.objects.filter(
            expense_date__gte=start,
            expense_date__lt=end,
            approval_status='paid',
            description__icontains='Depreciation'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        # Payroll cost
        payroll_cost = Decimal('0')
        if month:
            try:
                run = PayrollRun.objects.get(period_year=year, period_month=month)
                payroll_cost = run.total_cost
            except PayrollRun.DoesNotExist:
                pass

        # Forex gain/loss
        forex = ForexGainLoss.objects.filter(
            transaction_date__gte=start,
            transaction_date__lt=end,
            is_realized=True
        ).aggregate(total=Sum('gain_loss'))['total'] or Decimal('0')

        # Profit calculations
        gross_profit = net_revenue - total_expenses
        net_profit = gross_profit + forex
        margin = float(net_profit / net_revenue * 100) if net_revenue > 0 else 0

        pl, _ = cls.objects.update_or_create(
            period_type=period_type,
            period_start=start,
            period_end=end,
            defaults={
                'period_label': label,
                'gross_revenue': gross_revenue,
                'vat_collected': vat_collected,
                'net_revenue': net_revenue,
                'total_expenses': total_expenses,
                'depreciation': depreciation,
                'payroll_cost': payroll_cost,
                'forex_gain_loss': forex,
                'gross_profit': gross_profit,
                'net_profit': net_profit,
                'profit_margin': round(margin, 2),
                'expense_breakdown': expense_breakdown,
                'revenue_breakdown': {'gross': float(gross_revenue), 'vat': float(vat_collected), 'net': float(net_revenue)},
            }
        )
        return pl
