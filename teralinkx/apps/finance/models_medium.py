# apps/finance/models_medium.py
"""
Models for Phase 6 medium priority features:
6.13 Expense Approval Notifications
6.14 Financial Year Management
6.15 Petty Cash Management
6.16 Purchase Orders
6.17 Audit Trail
"""
from django.db import models
from django.utils import timezone
from decimal import Decimal
from datetime import date
from core.models import TimeStampedModel


# ── 6.13 Expense Notifications ────────────────────────────────────────────────

class NotificationPreference(TimeStampedModel):
    """Per-user notification preferences."""
    user            = models.OneToOneField('auth.User', on_delete=models.CASCADE,
                                           related_name='notification_prefs')
    expense_submitted_sms   = models.BooleanField(default=True)
    expense_submitted_email = models.BooleanField(default=True)
    expense_approved_sms    = models.BooleanField(default=True)
    expense_approved_email  = models.BooleanField(default=True)
    budget_alert_sms        = models.BooleanField(default=True)
    budget_alert_email      = models.BooleanField(default=True)
    tax_deadline_sms        = models.BooleanField(default=True)
    tax_deadline_email      = models.BooleanField(default=True)

    class Meta:
        app_label = 'finance'

    def __str__(self):
        return f"Notification prefs — {self.user.username}"


class ExpenseNotification(TimeStampedModel):
    """Log of expense approval notifications sent."""
    TYPES = [
        ('submitted', 'Expense Submitted'),
        ('approved',  'Expense Approved'),
        ('rejected',  'Expense Rejected'),
        ('overdue',   'Approval Overdue'),
    ]
    expense         = models.ForeignKey('finance.Expense', on_delete=models.CASCADE,
                                        related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=TYPES)
    recipient       = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    channel         = models.CharField(max_length=10, choices=[('sms','SMS'),('email','Email')])
    sent_at         = models.DateTimeField(auto_now_add=True)
    message         = models.TextField()
    delivered       = models.BooleanField(default=True)

    class Meta:
        app_label = 'finance'
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.notification_type} — {self.recipient.username} — {self.sent_at.date()}"


# ── 6.14 Financial Year ───────────────────────────────────────────────────────

class FinancialYear(TimeStampedModel):
    """Financial year management with opening/closing."""
    STATUS_CHOICES = [
        ('open',   'Open'),
        ('closed', 'Closed'),
    ]
    year            = models.IntegerField(unique=True)
    start_date      = models.DateField()
    end_date        = models.DateField()
    status          = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    closed_by       = models.ForeignKey('auth.User', on_delete=models.SET_NULL,
                                        null=True, blank=True)
    closed_at       = models.DateTimeField(null=True, blank=True)
    opening_balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    closing_balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    notes           = models.TextField(blank=True)

    class Meta:
        app_label = 'finance'
        ordering = ['-year']

    def __str__(self):
        return f"FY {self.year} ({self.status})"

    @classmethod
    def get_current(cls):
        year = timezone.now().year
        obj, _ = cls.objects.get_or_create(
            year=year,
            defaults={
                'start_date': date(year, 1, 1),
                'end_date': date(year, 12, 31),
                'status': 'open',
            }
        )
        return obj

    def close(self, user, closing_balance=None):
        self.status = 'closed'
        self.closed_by = user
        self.closed_at = timezone.now()
        if closing_balance is not None:
            self.closing_balance = closing_balance
        self.save()

        # Auto-create next year
        next_year = self.year + 1
        FinancialYear.objects.get_or_create(
            year=next_year,
            defaults={
                'start_date': date(next_year, 1, 1),
                'end_date': date(next_year, 12, 31),
                'status': 'open',
                'opening_balance': self.closing_balance,
            }
        )


# ── 6.15 Petty Cash ───────────────────────────────────────────────────────────

class PettyCashFund(TimeStampedModel):
    """Petty cash fund with float tracking."""
    name            = models.CharField(max_length=100)
    float_amount    = models.DecimalField(max_digits=12, decimal_places=2)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2)
    custodian       = models.ForeignKey('auth.User', on_delete=models.PROTECT,
                                        related_name='petty_cash_funds')
    department      = models.ForeignKey('finance.Department', on_delete=models.SET_NULL,
                                        null=True, blank=True)
    low_balance_threshold = models.DecimalField(max_digits=12, decimal_places=2, default=1000)
    is_active       = models.BooleanField(default=True)

    class Meta:
        app_label = 'finance'

    def __str__(self):
        return f"{self.name} — Balance KES {self.current_balance}"

    @property
    def is_low(self):
        return self.current_balance <= self.low_balance_threshold


class PettyCashTransaction(TimeStampedModel):
    """Individual petty cash expense."""
    TYPES = [('expense','Expense'), ('replenishment','Replenishment')]

    fund            = models.ForeignKey(PettyCashFund, on_delete=models.CASCADE,
                                        related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TYPES, default='expense')
    amount          = models.DecimalField(max_digits=12, decimal_places=2)
    description     = models.CharField(max_length=200)
    receipt_number  = models.CharField(max_length=50, blank=True)
    approved_by     = models.ForeignKey('auth.User', on_delete=models.SET_NULL,
                                        null=True, blank=True)
    balance_after   = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        app_label = 'finance'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        fund = self.fund
        if self.transaction_type == 'expense':
            fund.current_balance -= self.amount
        else:
            fund.current_balance += self.amount
        self.balance_after = fund.current_balance
        fund.save()
        super().save(*args, **kwargs)


# ── 6.16 Purchase Orders ──────────────────────────────────────────────────────

class PurchaseOrder(TimeStampedModel):
    """Purchase order for vendor procurement."""
    STATUS_CHOICES = [
        ('draft',    'Draft'),
        ('submitted','Submitted'),
        ('approved', 'Approved'),
        ('received', 'Goods Received'),
        ('invoiced', 'Vendor Invoice Received'),
        ('paid',     'Paid'),
        ('cancelled','Cancelled'),
    ]

    po_number       = models.CharField(max_length=30, unique=True)
    vendor_name     = models.CharField(max_length=200)
    department      = models.ForeignKey('finance.Department', on_delete=models.SET_NULL,
                                        null=True, blank=True)
    total_amount    = models.DecimalField(max_digits=14, decimal_places=2)
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    expected_delivery = models.DateField(null=True, blank=True)
    notes           = models.TextField(blank=True)
    submitted_by    = models.ForeignKey('auth.User', on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='submitted_pos')
    approved_by     = models.ForeignKey('auth.User', on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='approved_pos')
    approved_at     = models.DateTimeField(null=True, blank=True)
    line_items      = models.JSONField(default=list)

    class Meta:
        app_label = 'finance'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.po_number} — {self.vendor_name} — KES {self.total_amount}"

    @classmethod
    def generate_number(cls):
        year = timezone.now().year
        last = cls.objects.filter(po_number__startswith=f'PO-{year}-').order_by('-po_number').first()
        seq = int(last.po_number.split('-')[-1]) + 1 if last else 1
        return f'PO-{year}-{seq:04d}'

    def approve(self, user):
        self.status = 'approved'
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save()

    def mark_received(self):
        self.status = 'received'
        self.save()


# ── 6.17 Audit Trail ──────────────────────────────────────────────────────────

class AuditLog(TimeStampedModel):
    """Immutable audit log for all financial record changes."""
    ACTIONS = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('approve','Approved'),
        ('reject', 'Rejected'),
        ('file',   'Filed'),
        ('pay',    'Paid'),
    ]

    model_name      = models.CharField(max_length=100, db_index=True)
    record_id       = models.CharField(max_length=50, db_index=True)
    action          = models.CharField(max_length=20, choices=ACTIONS)
    changed_by      = models.ForeignKey('auth.User', on_delete=models.SET_NULL,
                                        null=True, blank=True)
    changed_at      = models.DateTimeField(auto_now_add=True, db_index=True)
    old_values      = models.JSONField(null=True, blank=True)
    new_values      = models.JSONField(null=True, blank=True)
    ip_address      = models.GenericIPAddressField(null=True, blank=True)
    description     = models.TextField(blank=True)

    class Meta:
        app_label = 'finance'
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['model_name', 'record_id']),
            models.Index(fields=['changed_by', 'changed_at']),
        ]

    def __str__(self):
        return f"{self.model_name} #{self.record_id} — {self.action} by {self.changed_by}"

    @classmethod
    def log(cls, model_name, record_id, action, user=None,
            old_values=None, new_values=None, description='', request=None):
        """Create an audit log entry."""
        ip = None
        if request:
            ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or \
                 request.META.get('REMOTE_ADDR')
        return cls.objects.create(
            model_name=model_name,
            record_id=str(record_id),
            action=action,
            changed_by=user,
            old_values=old_values,
            new_values=new_values,
            description=description,
            ip_address=ip,
        )

    @classmethod
    def get_record_history(cls, model_name, record_id):
        return cls.objects.filter(model_name=model_name, record_id=str(record_id))
