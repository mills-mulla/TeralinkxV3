# apps/finance/models_credit_note.py
from django.db import models
from django.utils import timezone
from decimal import Decimal
from core.models import TimeStampedModel


class CreditNote(TimeStampedModel):
    """Formal credit note issued to customers for overcharges or SLA breaches."""

    REASON_CHOICES = [
        ('overcharge',    'Customer Overcharged'),
        ('sla_breach',    'SLA Breach / Service Outage'),
        ('duplicate',     'Duplicate Payment'),
        ('cancellation',  'Service Cancellation'),
        ('goodwill',      'Goodwill Gesture'),
        ('other',         'Other'),
    ]

    STATUS_CHOICES = [
        ('draft',    'Draft'),
        ('approved', 'Approved'),
        ('applied',  'Applied to Account'),
        ('voided',   'Voided'),
    ]

    # Identity
    credit_note_number = models.CharField(max_length=30, unique=True, db_index=True)
    customer           = models.ForeignKey('users.ClientH', on_delete=models.PROTECT,
                                           related_name='credit_notes')
    original_invoice   = models.ForeignKey('finance.Invoice', on_delete=models.SET_NULL,
                                           null=True, blank=True, related_name='credit_notes')

    # Amounts
    subtotal           = models.DecimalField(max_digits=12, decimal_places=2)
    vat_rate           = models.DecimalField(max_digits=5, decimal_places=2, default=16)
    vat_amount         = models.DecimalField(max_digits=12, decimal_places=2)
    total              = models.DecimalField(max_digits=12, decimal_places=2)

    # Details
    reason             = models.CharField(max_length=20, choices=REASON_CHOICES)
    description        = models.TextField()
    issue_date         = models.DateField(default=timezone.now)

    # Workflow
    status             = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    approved_by        = models.ForeignKey('auth.User', on_delete=models.SET_NULL,
                                           null=True, blank=True, related_name='approved_credit_notes')
    approved_at        = models.DateTimeField(null=True, blank=True)
    applied_at         = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'finance'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['credit_note_number']),
        ]

    def __str__(self):
        return f"{self.credit_note_number} — {self.customer.account} — KES {self.total}"

    @classmethod
    def generate_number(cls):
        year = timezone.now().year
        last = cls.objects.filter(
            credit_note_number__startswith=f'CN-{year}-'
        ).order_by('-credit_note_number').first()
        seq = int(last.credit_note_number.split('-')[-1]) + 1 if last else 1
        return f'CN-{year}-{seq:05d}'

    @classmethod
    def create(cls, customer, amount, reason, description, original_invoice=None, approved_by=None):
        """Create a credit note with VAT calculation."""
        vat_rate = Decimal('16')
        subtotal = (amount / (1 + vat_rate / 100)).quantize(Decimal('0.01'))
        vat_amt  = (amount - subtotal).quantize(Decimal('0.01'))

        status = 'approved' if approved_by else 'draft'

        cn = cls.objects.create(
            credit_note_number = cls.generate_number(),
            customer           = customer,
            original_invoice   = original_invoice,
            subtotal           = subtotal,
            vat_rate           = vat_rate,
            vat_amount         = vat_amt,
            total              = amount,
            reason             = reason,
            description        = description,
            status             = status,
            approved_by        = approved_by,
            approved_at        = timezone.now() if approved_by else None,
        )
        return cn

    def approve(self, user):
        self.status = 'approved'
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save()

    def apply_to_account(self):
        """Apply credit to customer balance."""
        from finance.models import BalanceTransaction
        if self.status != 'approved':
            raise ValueError('Credit note must be approved before applying')

        # Add credit to customer balance
        customer = self.customer
        balance_before = customer.balance
        customer.balance += self.total
        customer.save()

        BalanceTransaction.objects.create(
            user=customer,
            transaction_type='adjustment',
            credit=self.total,
            debit=0,
            balance_before=balance_before,
            balance_after=customer.balance,
            description=f'Credit note {self.credit_note_number}: {self.description}'
        )

        self.status = 'applied'
        self.applied_at = timezone.now()
        self.save()

    def void(self):
        if self.status == 'applied':
            raise ValueError('Cannot void an applied credit note')
        self.status = 'voided'
        self.save()
