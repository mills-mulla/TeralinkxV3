"""
Data Quality Audit Management Command
Checks data completeness across critical finance tables
"""
from django.core.management.base import BaseCommand
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from finance.models import (
    PaymentTransaction, Expense, Investment, 
    TransactionQueue, Currency, ExchangeRate
)
from users.models import ClientH
from decimal import Decimal


class Command(BaseCommand):
    help = 'Audit data quality across finance tables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Attempt to fix data quality issues',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== DATA QUALITY AUDIT ===\n'))
        
        results = {
            'payment_transactions': self.audit_payment_transactions(),
            'customers': self.audit_customers(),
            'expenses': self.audit_expenses(),
            'transaction_queue': self.audit_transaction_queue(),
            'currencies': self.audit_currencies(),
        }
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n=== AUDIT SUMMARY ===\n'))
        
        total_issues = 0
        for table, data in results.items():
            issues = data.get('issues_found', 0)
            total_issues += issues
            completeness = data.get('completeness_pct', 0)
            
            status = '✓' if completeness >= 90 else '✗'
            color = self.style.SUCCESS if completeness >= 90 else self.style.ERROR
            
            self.stdout.write(
                color(f"{status} {table}: {completeness:.1f}% complete ({issues} issues)")
            )
        
        self.stdout.write(f"\nTotal issues found: {total_issues}")
        
        if options['fix']:
            self.stdout.write(self.style.WARNING('\n=== FIXING ISSUES ===\n'))
            self.fix_issues(results)
        else:
            self.stdout.write(self.style.WARNING('\nRun with --fix to attempt automatic fixes'))

    def audit_payment_transactions(self):
        self.stdout.write(self.style.HTTP_INFO('\n--- PaymentTransaction Audit ---'))
        
        total = PaymentTransaction.objects.count()
        if total == 0:
            self.stdout.write(self.style.WARNING('No payment transactions found'))
            return {'completeness_pct': 0, 'issues_found': 0}
        
        issues = []
        
        # Check for null amounts
        null_amounts = PaymentTransaction.objects.filter(amount__isnull=True).count()
        if null_amounts > 0:
            issues.append(f"{null_amounts} transactions with null amount")
        
        # Check for null currency
        null_currency = PaymentTransaction.objects.filter(currency__isnull=True).count()
        if null_currency > 0:
            issues.append(f"{null_currency} transactions with null currency")
        
        # Check for null users
        null_users = PaymentTransaction.objects.filter(user__isnull=True).count()
        if null_users > 0:
            issues.append(f"{null_users} transactions with null user")
        
        # Check for missing transaction_id
        null_txn_id = PaymentTransaction.objects.filter(
            Q(transaction_id__isnull=True) | Q(transaction_id='')
        ).count()
        if null_txn_id > 0:
            issues.append(f"{null_txn_id} transactions with missing transaction_id")
        
        # Check for duplicate transaction_ids
        duplicates = PaymentTransaction.objects.values('transaction_id').annotate(
            count=Count('id')
        ).filter(count__gt=1).count()
        if duplicates > 0:
            issues.append(f"{duplicates} duplicate transaction_ids")
        
        # Check for missing amount_base
        null_base = PaymentTransaction.objects.filter(amount_base__isnull=True).count()
        if null_base > 0:
            issues.append(f"{null_base} transactions with null amount_base")
        
        # Check for zero amounts
        zero_amounts = PaymentTransaction.objects.filter(amount=0).count()
        if zero_amounts > 0:
            issues.append(f"{zero_amounts} transactions with zero amount")
        
        # Calculate completeness
        complete_records = total - null_amounts - null_currency - null_users - null_txn_id
        completeness_pct = (complete_records / total) * 100
        
        self.stdout.write(f"Total records: {total}")
        self.stdout.write(f"Complete records: {complete_records}")
        self.stdout.write(f"Completeness: {completeness_pct:.1f}%")
        
        for issue in issues:
            self.stdout.write(self.style.WARNING(f"  ⚠ {issue}"))
        
        return {
            'completeness_pct': completeness_pct,
            'issues_found': len(issues),
            'issues': issues,
            'total': total
        }

    def audit_customers(self):
        self.stdout.write(self.style.HTTP_INFO('\n--- Customer (ClientH) Audit ---'))
        
        total = ClientH.objects.count()
        if total == 0:
            self.stdout.write(self.style.WARNING('No customers found'))
            return {'completeness_pct': 0, 'issues_found': 0}
        
        issues = []
        
        # Check for missing phone numbers
        null_phone = ClientH.objects.filter(
            Q(phone_number__isnull=True) | Q(phone_number='')
        ).count()
        if null_phone > 0:
            issues.append(f"{null_phone} customers with missing phone number")
        
        # Check for missing account IDs
        null_account = ClientH.objects.filter(
            Q(account__isnull=True) | Q(account='')
        ).count()
        if null_account > 0:
            issues.append(f"{null_account} customers with missing account ID")
        
        # Check for duplicate phone numbers
        duplicate_phones = ClientH.objects.values('phone_number').annotate(
            count=Count('id')
        ).filter(count__gt=1, phone_number__isnull=False).exclude(phone_number='').count()
        if duplicate_phones > 0:
            issues.append(f"{duplicate_phones} duplicate phone numbers")
        
        # Check for orphaned accounts (no transactions)
        orphaned = ClientH.objects.annotate(
            txn_count=Count('paymenttransaction')
        ).filter(txn_count=0).count()
        if orphaned > 0:
            issues.append(f"{orphaned} customers with no transactions (potential orphans)")
        
        # Check for negative balances
        negative_balance = ClientH.objects.filter(balance__lt=0).count()
        if negative_balance > 0:
            issues.append(f"{negative_balance} customers with negative balance")
        
        # Calculate completeness
        complete_records = total - null_phone - null_account
        completeness_pct = (complete_records / total) * 100
        
        self.stdout.write(f"Total records: {total}")
        self.stdout.write(f"Complete records: {complete_records}")
        self.stdout.write(f"Completeness: {completeness_pct:.1f}%")
        
        for issue in issues:
            self.stdout.write(self.style.WARNING(f"  ⚠ {issue}"))
        
        return {
            'completeness_pct': completeness_pct,
            'issues_found': len(issues),
            'issues': issues,
            'total': total
        }

    def audit_expenses(self):
        self.stdout.write(self.style.HTTP_INFO('\n--- Expense Audit ---'))
        
        total = Expense.objects.count()
        if total == 0:
            self.stdout.write(self.style.WARNING('No expenses found'))
            return {'completeness_pct': 100, 'issues_found': 0}
        
        issues = []
        
        # Check for null amounts
        null_amounts = Expense.objects.filter(amount__isnull=True).count()
        if null_amounts > 0:
            issues.append(f"{null_amounts} expenses with null amount")
        
        # Check for null descriptions
        null_desc = Expense.objects.filter(
            Q(description__isnull=True) | Q(description='')
        ).count()
        if null_desc > 0:
            issues.append(f"{null_desc} expenses with missing description")
        
        # Check for null categories
        null_category = Expense.objects.filter(
            Q(category__isnull=True) | Q(category='')
        ).count()
        if null_category > 0:
            issues.append(f"{null_category} expenses with missing category")
        
        # Check for null expense_date
        null_date = Expense.objects.filter(expense_date__isnull=True).count()
        if null_date > 0:
            issues.append(f"{null_date} expenses with missing date")
        
        # Check for future-dated expenses
        future_expenses = Expense.objects.filter(
            expense_date__gt=timezone.now().date()
        ).count()
        if future_expenses > 0:
            issues.append(f"{future_expenses} expenses dated in the future")
        
        # Check category consistency
        category_distribution = Expense.objects.values('category').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Calculate completeness
        complete_records = total - null_amounts - null_desc - null_category - null_date
        completeness_pct = (complete_records / total) * 100
        
        self.stdout.write(f"Total records: {total}")
        self.stdout.write(f"Complete records: {complete_records}")
        self.stdout.write(f"Completeness: {completeness_pct:.1f}%")
        
        self.stdout.write("\nCategory distribution:")
        for cat in category_distribution[:5]:
            self.stdout.write(f"  - {cat['category']}: {cat['count']}")
        
        for issue in issues:
            self.stdout.write(self.style.WARNING(f"  ⚠ {issue}"))
        
        return {
            'completeness_pct': completeness_pct,
            'issues_found': len(issues),
            'issues': issues,
            'total': total
        }

    def audit_transaction_queue(self):
        self.stdout.write(self.style.HTTP_INFO('\n--- TransactionQueue Audit ---'))
        
        total = TransactionQueue.objects.count()
        if total == 0:
            self.stdout.write(self.style.WARNING('No queue items found'))
            return {'completeness_pct': 100, 'issues_found': 0}
        
        issues = []
        
        # Check for stale pending items (>24 hours)
        cutoff = timezone.now() - timedelta(hours=24)
        stale_pending = TransactionQueue.objects.filter(
            status='pending',
            created_at__lt=cutoff
        ).count()
        if stale_pending > 0:
            issues.append(f"{stale_pending} pending items older than 24 hours")
        
        # Check for missing checkout_request_id
        null_checkout = TransactionQueue.objects.filter(
            method='mpesa',
            checkout_request_id__isnull=True
        ).count()
        if null_checkout > 0:
            issues.append(f"{null_checkout} M-Pesa items with missing checkout_request_id")
        
        # Check for null prices
        null_price = TransactionQueue.objects.filter(price__isnull=True).count()
        if null_price > 0:
            issues.append(f"{null_price} queue items with null price")
        
        # Status distribution
        status_dist = TransactionQueue.objects.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        self.stdout.write(f"Total records: {total}")
        self.stdout.write("\nStatus distribution:")
        for stat in status_dist:
            self.stdout.write(f"  - {stat['status']}: {stat['count']}")
        
        for issue in issues:
            self.stdout.write(self.style.WARNING(f"  ⚠ {issue}"))
        
        completeness_pct = 100 if len(issues) == 0 else 85
        
        return {
            'completeness_pct': completeness_pct,
            'issues_found': len(issues),
            'issues': issues,
            'total': total
        }

    def audit_currencies(self):
        self.stdout.write(self.style.HTTP_INFO('\n--- Currency & Exchange Rate Audit ---'))
        
        total_currencies = Currency.objects.count()
        total_rates = ExchangeRate.objects.count()
        
        issues = []
        
        # Check if KES exists
        try:
            kes = Currency.objects.get(code='KES')
            if not kes.is_base_currency:
                issues.append("KES exists but is not marked as base currency")
        except Currency.DoesNotExist:
            issues.append("KES currency not found (required as base)")
        
        # Check for stale exchange rates
        stale_cutoff = timezone.now() - timedelta(days=7)
        stale_rates = ExchangeRate.objects.filter(
            last_updated__lt=stale_cutoff,
            is_active=True
        ).count()
        if stale_rates > 0:
            issues.append(f"{stale_rates} exchange rates not updated in 7+ days")
        
        # Check for missing rates for active currencies
        active_currencies = Currency.objects.filter(is_active=True).exclude(code='KES')
        missing_rates = 0
        for currency in active_currencies:
            if not ExchangeRate.objects.filter(
                base_currency__code='KES',
                target_currency=currency,
                is_active=True
            ).exists():
                missing_rates += 1
        
        if missing_rates > 0:
            issues.append(f"{missing_rates} active currencies missing KES exchange rate")
        
        self.stdout.write(f"Total currencies: {total_currencies}")
        self.stdout.write(f"Total exchange rates: {total_rates}")
        self.stdout.write(f"Active currencies: {Currency.objects.filter(is_active=True).count()}")
        
        for issue in issues:
            self.stdout.write(self.style.WARNING(f"  ⚠ {issue}"))
        
        completeness_pct = 100 if len(issues) == 0 else 80
        
        return {
            'completeness_pct': completeness_pct,
            'issues_found': len(issues),
            'issues': issues,
            'total': total_currencies
        }

    def fix_issues(self, results):
        """Attempt to fix common data quality issues"""
        
        # Fix missing amount_base in PaymentTransaction
        null_base = PaymentTransaction.objects.filter(amount_base__isnull=True)
        if null_base.exists():
            self.stdout.write('Fixing missing amount_base...')
            for txn in null_base:
                if txn.amount and txn.currency:
                    txn.amount_base = txn.convert_to_base_currency()
                    txn.save(update_fields=['amount_base'])
            self.stdout.write(self.style.SUCCESS(f"  ✓ Fixed {null_base.count()} records"))
        
        # Fix missing transaction_id
        null_txn_id = PaymentTransaction.objects.filter(
            Q(transaction_id__isnull=True) | Q(transaction_id='')
        )
        if null_txn_id.exists():
            self.stdout.write('Fixing missing transaction_id...')
            for txn in null_txn_id:
                txn.transaction_id = txn.generate_transaction_id()
                txn.save(update_fields=['transaction_id'])
            self.stdout.write(self.style.SUCCESS(f"  ✓ Fixed {null_txn_id.count()} records"))
        
        # Mark stale pending queue items as failed
        cutoff = timezone.now() - timedelta(hours=24)
        stale_pending = TransactionQueue.objects.filter(
            status='pending',
            created_at__lt=cutoff
        )
        if stale_pending.exists():
            self.stdout.write('Marking stale pending items as failed...')
            count = 0
            for item in stale_pending:
                item.mark_pending_timeout_failure()
                count += 1
            self.stdout.write(self.style.SUCCESS(f"  ✓ Marked {count} items as failed"))
        
        # Ensure KES is base currency
        try:
            kes = Currency.objects.get(code='KES')
            if not kes.is_base_currency:
                kes.is_base_currency = True
                kes.save(update_fields=['is_base_currency'])
                self.stdout.write(self.style.SUCCESS("  ✓ Set KES as base currency"))
        except Currency.DoesNotExist:
            self.stdout.write(self.style.ERROR("  ✗ KES currency not found - create it manually"))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Fix attempt complete'))
