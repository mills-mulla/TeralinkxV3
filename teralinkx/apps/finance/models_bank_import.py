# apps/finance/models_bank_import.py
import csv
import io
from django.db import models
from django.utils import timezone
from decimal import Decimal
from core.models import TimeStampedModel


class BankStatement(TimeStampedModel):
    """Uploaded bank statement for reconciliation."""

    BANK_CHOICES = [
        ('equity',  'Equity Bank'),
        ('kcb',     'KCB Bank'),
        ('coop',    'Co-op Bank'),
        ('mpesa',   'M-Pesa Statement'),
        ('other',   'Other'),
    ]

    STATUS_CHOICES = [
        ('uploaded',     'Uploaded'),
        ('parsed',       'Parsed'),
        ('reconciling',  'Reconciling'),
        ('completed',    'Completed'),
        ('failed',       'Failed'),
    ]

    bank            = models.CharField(max_length=20, choices=BANK_CHOICES)
    file            = models.FileField(upload_to='bank_statements/')
    filename        = models.CharField(max_length=255)
    period_start    = models.DateField(null=True, blank=True)
    period_end      = models.DateField(null=True, blank=True)
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    total_entries   = models.IntegerField(default=0)
    parsed_entries  = models.IntegerField(default=0)
    error_message   = models.TextField(blank=True)
    uploaded_by     = models.ForeignKey('auth.User', on_delete=models.SET_NULL,
                                        null=True, blank=True)

    class Meta:
        app_label = 'finance'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_bank_display()} — {self.filename} — {self.status}"


class BankStatementEntry(TimeStampedModel):
    """Individual transaction from a bank statement."""

    statement       = models.ForeignKey(BankStatement, on_delete=models.CASCADE,
                                        related_name='entries')
    transaction_date = models.DateField()
    value_date      = models.DateField(null=True, blank=True)
    description     = models.TextField()
    reference       = models.CharField(max_length=200, blank=True)
    debit           = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    credit          = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    balance         = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    is_reconciled   = models.BooleanField(default=False)
    matched_transaction_id = models.CharField(max_length=255, blank=True)

    class Meta:
        app_label = 'finance'
        ordering = ['transaction_date']

    def __str__(self):
        amount = self.credit if self.credit > 0 else -self.debit
        return f"{self.transaction_date} | {self.description[:50]} | KES {amount}"


class BankStatementParser:
    """Parse CSV bank statements from different Kenyan banks."""

    @staticmethod
    def parse(statement: BankStatement, file_content: str) -> int:
        """Parse CSV content and create BankStatementEntry records. Returns entry count."""
        bank = statement.bank
        if bank == 'equity':
            return BankStatementParser._parse_equity(statement, file_content)
        elif bank == 'kcb':
            return BankStatementParser._parse_kcb(statement, file_content)
        elif bank == 'mpesa':
            return BankStatementParser._parse_mpesa(statement, file_content)
        else:
            return BankStatementParser._parse_generic(statement, file_content)

    @staticmethod
    def _parse_generic(statement, content):
        """Generic CSV parser — expects: Date, Description, Debit, Credit, Balance"""
        reader = csv.DictReader(io.StringIO(content))
        count = 0
        dates = []

        for row in reader:
            try:
                # Flexible column name matching
                date_val = (row.get('Date') or row.get('Transaction Date') or
                            row.get('date') or '').strip()
                desc = (row.get('Description') or row.get('Narration') or
                        row.get('description') or '').strip()
                debit = Decimal(str(row.get('Debit', 0) or 0).replace(',', '') or '0')
                credit = Decimal(str(row.get('Credit', 0) or 0).replace(',', '') or '0')
                balance = row.get('Balance', '') or row.get('Running Balance', '')
                ref = (row.get('Reference') or row.get('Ref') or '').strip()

                if not date_val or not desc:
                    continue

                from datetime import datetime
                for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y']:
                    try:
                        parsed_date = datetime.strptime(date_val, fmt).date()
                        break
                    except ValueError:
                        continue
                else:
                    continue

                dates.append(parsed_date)
                BankStatementEntry.objects.create(
                    statement=statement,
                    transaction_date=parsed_date,
                    description=desc,
                    reference=ref,
                    debit=debit,
                    credit=credit,
                    balance=Decimal(str(balance).replace(',', '')) if balance else None,
                )
                count += 1
            except Exception:
                continue

        if dates:
            statement.period_start = min(dates)
            statement.period_end = max(dates)

        statement.parsed_entries = count
        statement.total_entries = count
        statement.status = 'parsed'
        statement.save()
        return count

    @staticmethod
    def _parse_equity(statement, content):
        return BankStatementParser._parse_generic(statement, content)

    @staticmethod
    def _parse_kcb(statement, content):
        return BankStatementParser._parse_generic(statement, content)

    @staticmethod
    def _parse_mpesa(statement, content):
        """M-Pesa statement format: Receipt No, Completion Time, Details, Transaction Status, Paid In, Withdrawn, Balance"""
        reader = csv.DictReader(io.StringIO(content))
        count = 0
        dates = []

        for row in reader:
            try:
                receipt = (row.get('Receipt No.') or row.get('Receipt No') or '').strip()
                date_str = (row.get('Completion Time') or row.get('Date') or '').strip()
                details = (row.get('Details') or row.get('Description') or '').strip()
                paid_in = Decimal(str(row.get('Paid In', 0) or 0).replace(',', '') or '0')
                withdrawn = Decimal(str(row.get('Withdrawn', 0) or 0).replace(',', '') or '0')
                balance = row.get('Balance', '')

                if not date_str:
                    continue

                from datetime import datetime
                for fmt in ['%d/%m/%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y']:
                    try:
                        parsed_date = datetime.strptime(date_str.strip(), fmt).date()
                        break
                    except ValueError:
                        continue
                else:
                    continue

                dates.append(parsed_date)
                BankStatementEntry.objects.create(
                    statement=statement,
                    transaction_date=parsed_date,
                    description=details,
                    reference=receipt,
                    debit=withdrawn,
                    credit=paid_in,
                    balance=Decimal(str(balance).replace(',', '')) if balance else None,
                )
                count += 1
            except Exception:
                continue

        if dates:
            statement.period_start = min(dates)
            statement.period_end = max(dates)

        statement.parsed_entries = count
        statement.total_entries = count
        statement.status = 'parsed'
        statement.save()
        return count
