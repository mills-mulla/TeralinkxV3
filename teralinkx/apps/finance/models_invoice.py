# apps/finance/models_invoice.py
from django.db import models
from django.utils import timezone
from core.models import TimeStampedModel


class Invoice(TimeStampedModel):
    """KRA-compliant tax invoice auto-generated on every payment."""

    STATUS_CHOICES = [
        ('draft',    'Draft'),
        ('issued',   'Issued'),
        ('paid',     'Paid'),
        ('cancelled','Cancelled'),
        ('credited', 'Credited'),
    ]

    # Identity
    invoice_number  = models.CharField(max_length=30, unique=True, db_index=True)
    customer        = models.ForeignKey('users.ClientH', on_delete=models.PROTECT, related_name='invoices')
    # Store transaction_id as string reference (TimescaleDB hypertable FK limitation)
    transaction_id_ref = models.CharField(max_length=255, blank=True, db_index=True,
                                          help_text='PaymentTransaction.transaction_id')

    # Amounts (KES)
    subtotal        = models.DecimalField(max_digits=12, decimal_places=2)
    vat_rate        = models.DecimalField(max_digits=5, decimal_places=2, default=16.00)
    vat_amount      = models.DecimalField(max_digits=12, decimal_places=2)
    total           = models.DecimalField(max_digits=12, decimal_places=2)

    # Dates
    issue_date      = models.DateField(default=timezone.now)
    due_date        = models.DateField(null=True, blank=True)

    # Status
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='issued')

    # Line items (JSON — flexible for future multi-line invoices)
    line_items      = models.JSONField(default=list)

    # Description
    description     = models.TextField(blank=True)

    # PDF storage
    pdf_file        = models.FileField(upload_to='invoices/pdf/', null=True, blank=True)

    # KRA fields
    kra_pin_customer = models.CharField(max_length=20, blank=True)

    class Meta:
        app_label = 'finance'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['issue_date']),
            models.Index(fields=['invoice_number']),
        ]

    def __str__(self):
        return f"{self.invoice_number} — {self.customer.account} — KES {self.total}"

    @classmethod
    def generate_invoice_number(cls):
        """Generate sequential invoice number: INV-2026-00001"""
        year = timezone.now().year
        last = cls.objects.filter(
            invoice_number__startswith=f'INV-{year}-'
        ).order_by('-invoice_number').first()

        if last:
            try:
                seq = int(last.invoice_number.split('-')[-1]) + 1
            except ValueError:
                seq = 1
        else:
            seq = 1

        return f'INV-{year}-{seq:05d}'

    @classmethod
    def create_from_transaction(cls, transaction):
        """Create invoice from a completed PaymentTransaction."""
        from decimal import Decimal

        # Avoid duplicate invoices
        if Invoice.objects.filter(transaction_id_ref=transaction.transaction_id).exists():
            return Invoice.objects.filter(transaction_id_ref=transaction.transaction_id).first()

        vat_rate = Decimal('16.00')
        # Back-calculate: total includes VAT
        # subtotal = total / 1.16, vat = total - subtotal
        total    = transaction.amount_base
        subtotal = (total / (1 + vat_rate / 100)).quantize(Decimal('0.01'))
        vat_amt  = (total - subtotal).quantize(Decimal('0.01'))

        line_items = [{
            'description': f'Internet Service — {transaction.account_reference}',
            'quantity':    1,
            'unit_price':  float(subtotal),
            'vat_rate':    float(vat_rate),
            'vat_amount':  float(vat_amt),
            'total':       float(total),
        }]

        invoice = cls.objects.create(
            invoice_number = cls.generate_invoice_number(),
            customer       = transaction.user,
            transaction_id_ref = transaction.transaction_id,
            subtotal       = subtotal,
            vat_rate       = vat_rate,
            vat_amount     = vat_amt,
            total          = total,
            issue_date     = transaction.created_at.date(),
            status         = 'paid',
            line_items     = line_items,
            description    = f'Payment via {transaction.payment_method.upper()} — Ref: {transaction.gateway_reference}',
        )

        return invoice
