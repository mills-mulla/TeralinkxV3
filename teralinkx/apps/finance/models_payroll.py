# apps/finance/models_payroll.py
from django.db import models
from django.utils import timezone
from decimal import Decimal
from core.models import TimeStampedModel


class Employee(TimeStampedModel):
    """Employee record for payroll processing."""

    EMPLOYMENT_TYPES = [
        ('full_time',  'Full Time'),
        ('part_time',  'Part Time'),
        ('contract',   'Contract'),
        ('intern',     'Intern'),
    ]

    # Identity
    user            = models.OneToOneField('auth.User', on_delete=models.PROTECT,
                                           related_name='employee_profile', null=True, blank=True)
    employee_number = models.CharField(max_length=20, unique=True)
    first_name      = models.CharField(max_length=100)
    last_name       = models.CharField(max_length=100)
    id_number       = models.CharField(max_length=20, unique=True)
    kra_pin         = models.CharField(max_length=20, blank=True)
    nhif_number     = models.CharField(max_length=20, blank=True)
    nssf_number     = models.CharField(max_length=20, blank=True)

    # Employment
    department      = models.ForeignKey('finance.Department', on_delete=models.SET_NULL,
                                        null=True, blank=True)
    job_title       = models.CharField(max_length=100)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES, default='full_time')
    start_date      = models.DateField()
    end_date        = models.DateField(null=True, blank=True)
    is_active       = models.BooleanField(default=True)

    # Compensation
    gross_salary    = models.DecimalField(max_digits=12, decimal_places=2)
    bank_name       = models.CharField(max_length=100, blank=True)
    bank_account    = models.CharField(max_length=30, blank=True)
    phone_number    = models.CharField(max_length=20, blank=True)
    email           = models.EmailField(blank=True)

    class Meta:
        app_label = 'finance'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.employee_number} — {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @classmethod
    def generate_number(cls):
        count = cls.objects.count() + 1
        return f'EMP-{count:04d}'


class PayrollRun(TimeStampedModel):
    """Monthly payroll run."""

    STATUS_CHOICES = [
        ('draft',     'Draft'),
        ('processed', 'Processed'),
        ('approved',  'Approved'),
        ('paid',      'Paid'),
    ]

    period_month    = models.IntegerField()
    period_year     = models.IntegerField()
    period_label    = models.CharField(max_length=30)

    # Totals
    total_gross     = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_paye      = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_nhif      = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_nssf_employee = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_nssf_employer = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_net       = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_cost      = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    processed_by    = models.ForeignKey('auth.User', on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='payroll_runs_processed')
    approved_by     = models.ForeignKey('auth.User', on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='payroll_runs_approved')
    paid_at         = models.DateTimeField(null=True, blank=True)
    notes           = models.TextField(blank=True)

    class Meta:
        app_label = 'finance'
        unique_together = ['period_year', 'period_month']
        ordering = ['-period_year', '-period_month']

    def __str__(self):
        return f"Payroll {self.period_label} — KES {self.total_net}"

    def approve(self, user):
        self.status = 'approved'
        self.approved_by = user
        self.save()

    def mark_paid(self):
        self.status = 'paid'
        self.paid_at = timezone.now()
        self.save()


class PayslipItem(TimeStampedModel):
    """Individual payslip for one employee in a payroll run."""

    payroll_run     = models.ForeignKey(PayrollRun, on_delete=models.CASCADE,
                                        related_name='payslips')
    employee        = models.ForeignKey(Employee, on_delete=models.PROTECT,
                                        related_name='payslips')

    # Earnings
    gross_salary    = models.DecimalField(max_digits=12, decimal_places=2)
    allowances      = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_earnings  = models.DecimalField(max_digits=12, decimal_places=2)

    # Deductions
    paye            = models.DecimalField(max_digits=12, decimal_places=2)
    nhif            = models.DecimalField(max_digits=12, decimal_places=2)
    nssf_employee   = models.DecimalField(max_digits=12, decimal_places=2)
    other_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2)

    # Employer costs
    nssf_employer   = models.DecimalField(max_digits=12, decimal_places=2)

    # Net
    net_pay         = models.DecimalField(max_digits=12, decimal_places=2)

    # Breakdown JSON for payslip display
    breakdown       = models.JSONField(default=dict)

    class Meta:
        app_label = 'finance'
        unique_together = ['payroll_run', 'employee']
        ordering = ['employee__last_name']

    def __str__(self):
        return f"{self.employee.full_name} — {self.payroll_run.period_label} — Net KES {self.net_pay}"


class PayrollCalculator:
    """
    Kenya payroll calculations 2024/2025.
    PAYE bands, NHIF, NSSF per KRA/NHIF/NSSF regulations.
    """

    @staticmethod
    def calculate_paye(gross_monthly: Decimal) -> Decimal:
        """
        Kenya PAYE 2024 tax bands (monthly):
        0 - 24,000:       10%
        24,001 - 32,333:  25%
        32,334 - 500,000: 30%
        500,001 - 800,000: 32.5%
        800,001+:          35%
        Personal relief: KES 2,400/month
        """
        gross = float(gross_monthly)
        tax = 0.0

        if gross <= 24000:
            tax = gross * 0.10
        elif gross <= 32333:
            tax = 24000 * 0.10 + (gross - 24000) * 0.25
        elif gross <= 500000:
            tax = 24000 * 0.10 + 8333 * 0.25 + (gross - 32333) * 0.30
        elif gross <= 800000:
            tax = 24000 * 0.10 + 8333 * 0.25 + 467667 * 0.30 + (gross - 500000) * 0.325
        else:
            tax = 24000 * 0.10 + 8333 * 0.25 + 467667 * 0.30 + 300000 * 0.325 + (gross - 800000) * 0.35

        # Personal relief
        tax = max(0, tax - 2400)
        return Decimal(str(round(tax, 2)))

    @staticmethod
    def calculate_nhif(gross_monthly: Decimal) -> Decimal:
        """
        NHIF 2024 income-based bands (monthly contribution).
        """
        gross = float(gross_monthly)
        bands = [
            (5999,   150),
            (7999,   300),
            (11999,  400),
            (14999,  500),
            (19999,  600),
            (24999,  750),
            (29999,  850),
            (34999,  900),
            (39999,  950),
            (44999, 1000),
            (49999, 1100),
            (59999, 1200),
            (69999, 1300),
            (79999, 1400),
            (89999, 1500),
            (99999, 1600),
            (float('inf'), 1700),
        ]
        for limit, contribution in bands:
            if gross <= limit:
                return Decimal(str(contribution))
        return Decimal('1700')

    @staticmethod
    def calculate_nssf(gross_monthly: Decimal) -> tuple:
        """
        NSSF 2024: 6% employee + 6% employer, capped at KES 2,160 each.
        Lower limit: KES 6,000 (Tier I), Upper limit: KES 18,000 (Tier II).
        """
        gross = float(gross_monthly)
        tier1_limit = 6000
        tier2_limit = 18000

        tier1 = min(gross, tier1_limit) * 0.06
        tier2 = max(0, min(gross, tier2_limit) - tier1_limit) * 0.06

        employee = min(tier1 + tier2, 2160)
        employer = min(tier1 + tier2, 2160)

        return Decimal(str(round(employee, 2))), Decimal(str(round(employer, 2)))

    @classmethod
    def calculate_payslip(cls, employee: Employee) -> dict:
        """Calculate full payslip for one employee."""
        gross = employee.gross_salary
        paye = cls.calculate_paye(gross)
        nhif = cls.calculate_nhif(gross)
        nssf_emp, nssf_er = cls.calculate_nssf(gross)

        total_deductions = paye + nhif + nssf_emp
        net_pay = gross - total_deductions

        return {
            'gross_salary':    gross,
            'allowances':      Decimal('0'),
            'total_earnings':  gross,
            'paye':            paye,
            'nhif':            nhif,
            'nssf_employee':   nssf_emp,
            'nssf_employer':   nssf_er,
            'other_deductions': Decimal('0'),
            'total_deductions': total_deductions,
            'net_pay':         net_pay,
            'breakdown': {
                'gross': float(gross),
                'paye': float(paye),
                'nhif': float(nhif),
                'nssf_employee': float(nssf_emp),
                'nssf_employer': float(nssf_er),
                'total_deductions': float(total_deductions),
                'net_pay': float(net_pay),
                'effective_tax_rate': round(float(paye) / float(gross) * 100, 1) if gross > 0 else 0,
            }
        }

    @classmethod
    def run_payroll(cls, year: int, month: int, processed_by=None) -> PayrollRun:
        """Process full payroll for all active employees."""
        from datetime import date
        import calendar

        period_label = date(year, month, 1).strftime('%B %Y')

        run, _ = PayrollRun.objects.get_or_create(
            period_year=year,
            period_month=month,
            defaults={'period_label': period_label, 'status': 'draft', 'processed_by': processed_by}
        )

        # Clear existing payslips if re-running
        run.payslips.all().delete()

        employees = Employee.objects.filter(is_active=True)
        totals = {
            'gross': Decimal('0'), 'paye': Decimal('0'),
            'nhif': Decimal('0'), 'nssf_emp': Decimal('0'),
            'nssf_er': Decimal('0'), 'net': Decimal('0')
        }

        for emp in employees:
            calc = cls.calculate_payslip(emp)
            PayslipItem.objects.create(
                payroll_run=run,
                employee=emp,
                gross_salary=calc['gross_salary'],
                allowances=calc['allowances'],
                total_earnings=calc['total_earnings'],
                paye=calc['paye'],
                nhif=calc['nhif'],
                nssf_employee=calc['nssf_employee'],
                nssf_employer=calc['nssf_employer'],
                total_deductions=calc['total_deductions'],
                net_pay=calc['net_pay'],
                breakdown=calc['breakdown']
            )
            totals['gross']    += calc['gross_salary']
            totals['paye']     += calc['paye']
            totals['nhif']     += calc['nhif']
            totals['nssf_emp'] += calc['nssf_employee']
            totals['nssf_er']  += calc['nssf_employer']
            totals['net']      += calc['net_pay']

        run.total_gross          = totals['gross']
        run.total_paye           = totals['paye']
        run.total_nhif           = totals['nhif']
        run.total_nssf_employee  = totals['nssf_emp']
        run.total_nssf_employer  = totals['nssf_er']
        run.total_net            = totals['net']
        run.total_cost           = totals['gross'] + totals['nssf_er']
        run.status               = 'processed'
        run.processed_by         = processed_by
        run.save()

        return run
