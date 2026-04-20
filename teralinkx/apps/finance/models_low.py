# apps/finance/models_low.py
"""
Models for Phase 6 remaining features:
6.18 Payment Allocation
6.19 SLA Credit Management
6.20 Loan Repayment Schedule
6.21 Multi-Branch Support
6.22 Insurance Management
6.23 Dividend Distribution
6.24 CLV Cohort Analysis
"""
from django.db import models
from django.utils import timezone
from decimal import Decimal
from datetime import date
from core.models import TimeStampedModel


# ── 6.18 Payment Allocation ───────────────────────────────────────────────────

class PaymentAllocation(TimeStampedModel):
    """Links a payment to one or more invoices."""
    transaction_id  = models.CharField(max_length=255, db_index=True)
    invoice         = models.ForeignKey('finance.Invoice', on_delete=models.CASCADE,
                                        related_name='allocations')
    amount_allocated = models.DecimalField(max_digits=14, decimal_places=2)
    allocated_by    = models.ForeignKey('auth.User', on_delete=models.SET_NULL,
                                        null=True, blank=True)
    is_auto         = models.BooleanField(default=True)
    notes           = models.TextField(blank=True)

    class Meta:
        app_label = 'finance'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['transaction_id'])]

    def __str__(self):
        return f"TXN {self.transaction_id} → INV {self.invoice.invoice_number} KES {self.amount_allocated}"

    @classmethod
    def auto_allocate(cls, transaction_id, customer, amount):
        """Allocate payment to oldest unpaid invoices first."""
        from finance.models_invoice import Invoice
        unpaid = Invoice.objects.filter(
            customer=customer, status='issued'
        ).order_by('issue_date')

        remaining = Decimal(str(amount))
        allocations = []

        for invoice in unpaid:
            if remaining <= 0:
                break
            already = cls.objects.filter(invoice=invoice).aggregate(
                total=models.Sum('amount_allocated')
            )['total'] or Decimal('0')
            outstanding = invoice.total - already
            if outstanding <= 0:
                continue
            alloc_amount = min(remaining, outstanding)
            alloc = cls.objects.create(
                transaction_id=transaction_id,
                invoice=invoice,
                amount_allocated=alloc_amount,
                is_auto=True,
            )
            allocations.append(alloc)
            remaining -= alloc_amount
            if alloc_amount >= outstanding:
                invoice.status = 'paid'
                invoice.save()

        return allocations, remaining


# ── 6.19 SLA Credit Management ────────────────────────────────────────────────

class SLAPolicy(TimeStampedModel):
    """SLA policy defining uptime guarantees and credit rates."""
    name                = models.CharField(max_length=100, default='Standard SLA')
    uptime_guarantee_pct = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('99.5'))
    credit_pct_per_hour = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('2.0'),
                                               help_text='% of monthly bill credited per hour of downtime')
    max_credit_pct      = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('30.0'),
                                               help_text='Maximum credit as % of monthly bill')
    is_active           = models.BooleanField(default=True)

    class Meta:
        app_label = 'finance'

    def __str__(self):
        return f"{self.name} — {self.uptime_guarantee_pct}% uptime"


class OutageEvent(TimeStampedModel):
    """Network outage event for SLA credit calculation."""
    STATUS_CHOICES = [
        ('open',     'Open'),
        ('resolved', 'Resolved'),
        ('credited', 'Credits Applied'),
    ]
    start_time          = models.DateTimeField()
    end_time            = models.DateTimeField(null=True, blank=True)
    description         = models.TextField()
    affected_customers  = models.ManyToManyField('users.ClientH', blank=True,
                                                  related_name='outage_events')
    status              = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    sla_policy          = models.ForeignKey(SLAPolicy, on_delete=models.SET_NULL, null=True, blank=True)
    credits_generated   = models.IntegerField(default=0)

    class Meta:
        app_label = 'finance'
        ordering = ['-start_time']

    def __str__(self):
        return f"Outage {self.start_time.date()} — {self.status}"

    @property
    def duration_hours(self):
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() / 3600
        return (timezone.now() - self.start_time).total_seconds() / 3600

    def resolve(self, end_time=None):
        self.end_time = end_time or timezone.now()
        self.status = 'resolved'
        self.save()

    def generate_credits(self, policy=None):
        """Generate SLA credit notes AND refund logs for all affected customers."""
        from finance.models_credit_note import CreditNote
        from analytics.models import RefundLog, DowntimeRecord
        policy = policy or self.sla_policy or SLAPolicy.objects.filter(is_active=True).first()
        if not policy:
            return 0

        hours = self.duration_hours
        downtime_minutes = int(hours * 60)
        credit_rate = float(policy.credit_pct_per_hour) / 100
        max_rate = float(policy.max_credit_pct) / 100
        created = 0

        # Create a DowntimeRecord linked to this outage
        downtime_record, _ = DowntimeRecord.objects.get_or_create(
            outage_event_id=self.id,
            defaults={
                'start_time': self.start_time,
                'end_time': self.end_time or timezone.now(),
                'description': self.description,
            }
        )

        for customer in self.affected_customers.all():
            from finance.models import TransactionQueue
            last_payment = TransactionQueue.objects.filter(
                user=customer, status__in=['completed', 'processed']
            ).order_by('-created_at').first()

            if not last_payment:
                continue

            monthly_bill = float(last_payment.price)
            credit_amount = min(monthly_bill * credit_rate * hours, monthly_bill * max_rate)

            if credit_amount < 1:
                continue

            credit_amount = round(credit_amount, 2)

            # 1. Create finance CreditNote
            CreditNote.create(
                customer=customer,
                amount=Decimal(str(credit_amount)),
                reason='sla_breach',
                description=f'SLA credit for {hours:.1f}h outage on {self.start_time.date()}',
            )

            # 2. Credit customer balance directly
            customer.balance = (customer.balance or 0) + Decimal(str(credit_amount))
            customer.save(update_fields=['balance'])

            # 3. Log in RefundLog for the Refunds page
            RefundLog.objects.create(
                account=customer.account,
                client_username=customer.user.username if customer.user else customer.account,
                refund_amount=Decimal(str(credit_amount)),
                downtime_minutes=downtime_minutes,
                refund_type='sla',
                status='completed',
                downtime_record=downtime_record,
                notes=f'Auto-generated from SLA outage #{self.id}',
            )

            created += 1

        self.credits_generated = created
        self.status = 'credited'
        self.save()
        return created


# ── 6.20 Loan Repayment Schedule ─────────────────────────────────────────────

class RepaymentSchedule(TimeStampedModel):
    """Loan repayment schedule for Investment records."""
    investment      = models.ForeignKey('finance.Investment', on_delete=models.CASCADE,
                                        related_name='repayment_schedule')
    installment_no  = models.IntegerField()
    due_date        = models.DateField()
    principal       = models.DecimalField(max_digits=14, decimal_places=2)
    interest        = models.DecimalField(max_digits=14, decimal_places=2)
    total           = models.DecimalField(max_digits=14, decimal_places=2)
    status          = models.CharField(max_length=20,
                                       choices=[('pending','Pending'),('paid','Paid'),('overdue','Overdue')],
                                       default='pending')
    paid_date       = models.DateField(null=True, blank=True)
    paid_amount     = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    class Meta:
        app_label = 'finance'
        ordering = ['installment_no']
        unique_together = ['investment', 'installment_no']

    def __str__(self):
        return f"Installment {self.installment_no} — KES {self.total} — {self.due_date}"

    @classmethod
    def generate_for_investment(cls, investment):
        """Generate repayment schedule for a loan investment."""
        if investment.investment_type != 'loan':
            return []
        if not investment.maturity_date or not investment.interest_rate:
            return []

        from dateutil.relativedelta import relativedelta
        start = investment.investment_date
        end = investment.maturity_date
        months = (end.year - start.year) * 12 + (end.month - start.month)
        if months <= 0:
            return []

        principal_per_month = (investment.amount / months).quantize(Decimal('0.01'))
        monthly_rate = investment.interest_rate / 100 / 12
        balance = investment.amount
        schedules = []

        for i in range(1, months + 1):
            due = start + relativedelta(months=i)
            interest = (balance * monthly_rate).quantize(Decimal('0.01'))
            total = principal_per_month + interest
            balance -= principal_per_month

            s, _ = cls.objects.get_or_create(
                investment=investment,
                installment_no=i,
                defaults={
                    'due_date': due,
                    'principal': principal_per_month,
                    'interest': interest,
                    'total': total,
                }
            )
            schedules.append(s)

        return schedules


# ── 6.21 Multi-Branch ─────────────────────────────────────────────────────────

class Branch(TimeStampedModel):
    """Business branch for multi-location operations."""
    name        = models.CharField(max_length=100)
    code        = models.CharField(max_length=10, unique=True)
    location    = models.CharField(max_length=200, blank=True)
    manager     = models.ForeignKey('auth.User', on_delete=models.SET_NULL,
                                    null=True, blank=True)
    is_active   = models.BooleanField(default=True)
    is_hq       = models.BooleanField(default=False)

    class Meta:
        app_label = 'finance'
        ordering = ['-is_hq', 'name']

    def __str__(self):
        return f"{self.code} — {self.name}"


# ── 6.22 Insurance Management ─────────────────────────────────────────────────

class InsurancePolicy(TimeStampedModel):
    """Insurance policy tracking."""
    STATUS_CHOICES = [('active','Active'), ('expired','Expired'), ('cancelled','Cancelled')]

    provider        = models.CharField(max_length=200)
    policy_number   = models.CharField(max_length=100)
    coverage_type   = models.CharField(max_length=100)
    premium_amount  = models.DecimalField(max_digits=12, decimal_places=2)
    premium_frequency = models.CharField(max_length=20,
                                          choices=[('monthly','Monthly'),('annual','Annual')],
                                          default='annual')
    start_date      = models.DateField()
    end_date        = models.DateField()
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    assets_covered  = models.TextField(blank=True)
    notes           = models.TextField(blank=True)

    class Meta:
        app_label = 'finance'
        ordering = ['end_date']

    def __str__(self):
        return f"{self.provider} — {self.coverage_type} — expires {self.end_date}"

    @property
    def days_until_expiry(self):
        return (self.end_date - date.today()).days

    @property
    def is_expiring_soon(self):
        return 0 < self.days_until_expiry <= 30


# ── 6.23 Dividend Distribution ────────────────────────────────────────────────

class DividendDeclaration(TimeStampedModel):
    """Dividend declaration for equity investors."""
    STATUS_CHOICES = [('draft','Draft'), ('approved','Approved'), ('paid','Paid')]

    period_label    = models.CharField(max_length=50)
    total_profit    = models.DecimalField(max_digits=14, decimal_places=2)
    distribution_amount = models.DecimalField(max_digits=14, decimal_places=2)
    per_share       = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    wht_rate        = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('5.0'))
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    declared_by     = models.ForeignKey('auth.User', on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='dividend_declarations')
    declared_at     = models.DateTimeField(null=True, blank=True)
    notes           = models.TextField(blank=True)

    class Meta:
        app_label = 'finance'
        ordering = ['-created_at']

    def __str__(self):
        return f"Dividend {self.period_label} — KES {self.distribution_amount}"

    def approve(self, user):
        self.status = 'approved'
        self.declared_by = user
        self.declared_at = timezone.now()
        self.save()


# ── 6.24 CLV Cohort Analysis ──────────────────────────────────────────────────

class CLVCohort(TimeStampedModel):
    """Customer Lifetime Value cohort analysis."""
    cohort_month    = models.DateField(help_text='First month of customer acquisition')
    cohort_size     = models.IntegerField(default=0)
    month_offset    = models.IntegerField(help_text='Months since acquisition (0=first month)')
    active_customers = models.IntegerField(default=0)
    retention_rate  = models.FloatField(default=0)
    revenue         = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    avg_revenue_per_customer = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cumulative_clv  = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        app_label = 'finance'
        unique_together = ['cohort_month', 'month_offset']
        ordering = ['cohort_month', 'month_offset']

    def __str__(self):
        return f"Cohort {self.cohort_month.strftime('%b %Y')} — Month {self.month_offset}"

    @classmethod
    def calculate(cls, cohort_month_start, max_months=12):
        """Calculate cohort metrics for customers acquired in a given month."""
        from users.models import ClientH
        from finance.models import TransactionQueue
        from django.db.models import Sum, Count
        from datetime import date
        import calendar

        cohort_end = date(cohort_month_start.year,
                          cohort_month_start.month,
                          calendar.monthrange(cohort_month_start.year, cohort_month_start.month)[1])

        cohort_customers = ClientH.objects.filter(
            created_at__date__gte=cohort_month_start,
            created_at__date__lte=cohort_end
        )
        cohort_size = cohort_customers.count()
        if cohort_size == 0:
            return []

        customer_ids = list(cohort_customers.values_list('id', flat=True))
        results = []
        cumulative = Decimal('0')

        for offset in range(max_months):
            from dateutil.relativedelta import relativedelta
            period_start = cohort_month_start + relativedelta(months=offset)
            period_end = period_start + relativedelta(months=1)

            txns = TransactionQueue.objects.filter(
                user_id__in=customer_ids,
                status__in=['completed', 'processed'],
                created_at__date__gte=period_start,
                created_at__date__lt=period_end,
            )
            active = txns.values('user_id').distinct().count()
            revenue = txns.aggregate(total=Sum('price'))['total'] or Decimal('0')
            cumulative += revenue
            avg_rev = (revenue / active).quantize(Decimal('0.01')) if active > 0 else Decimal('0')

            cohort, _ = cls.objects.update_or_create(
                cohort_month=cohort_month_start,
                month_offset=offset,
                defaults={
                    'cohort_size': cohort_size,
                    'active_customers': active,
                    'retention_rate': round(active / cohort_size * 100, 1),
                    'revenue': revenue,
                    'avg_revenue_per_customer': avg_rev,
                    'cumulative_clv': cumulative,
                }
            )
            results.append(cohort)

        return results
