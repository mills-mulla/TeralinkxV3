"""
Test Dual-Read Consistency
Validates that PostgreSQL and TimescaleDB return identical results.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Sum, Count, Avg
from datetime import timedelta
from finance.models import PaymentTransaction, TransactionQueue


class Command(BaseCommand):
    help = 'Test dual-read consistency between PostgreSQL and TimescaleDB'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output'
        )
    
    def handle(self, *args, **options):
        verbose = options['verbose']
        
        self.stdout.write(self.style.SUCCESS('\n=== Dual-Read Consistency Test ===\n'))
        
        tests = [
            ('Count all transactions', self._test_count_all),
            ('Sum amounts', self._test_sum_amounts),
            ('Average transaction value', self._test_avg_amount),
            ('Count by status', self._test_count_by_status),
            ('Recent 7 days', self._test_recent_7_days),
            ('Group by date', self._test_group_by_date),
            ('Filter by user', self._test_filter_by_user),
            ('Complex aggregation', self._test_complex_aggregation),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            self.stdout.write(f'\nTest: {test_name}')
            try:
                result = test_func(verbose)
                if result['match']:
                    self.stdout.write(self.style.SUCCESS('  ✓ PASS'))
                    passed += 1
                else:
                    self.stdout.write(self.style.ERROR('  ✗ FAIL'))
                    self.stdout.write(f"    PG: {result['pg']}")
                    self.stdout.write(f"    TS: {result['ts']}")
                    failed += 1
                
                if verbose and 'details' in result:
                    self.stdout.write(f"    {result['details']}")
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ ERROR: {e}'))
                failed += 1
        
        # Summary
        self.stdout.write(self.style.SUCCESS(
            f'\n\n=== Test Summary ===\n'
            f'Passed: {passed}\n'
            f'Failed: {failed}\n'
            f'Total: {passed + failed}\n'
        ))
        
        if failed > 0:
            self.stdout.write(self.style.ERROR(
                '⚠ Some tests failed. Do not increase rollout until fixed.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                '✓ All tests passed. Safe to increase rollout.'
            ))
    
    def _test_count_all(self, verbose):
        """Test simple count."""
        pg_count = PaymentTransaction.objects.using('default').count()
        ts_count = PaymentTransaction.objects.using('timescale').count()
        
        return {
            'match': pg_count == ts_count,
            'pg': pg_count,
            'ts': ts_count,
            'details': f'{pg_count:,} transactions'
        }
    
    def _test_sum_amounts(self, verbose):
        """Test sum aggregation."""
        pg_sum = PaymentTransaction.objects.using('default').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        ts_sum = PaymentTransaction.objects.using('timescale').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Allow small floating point differences
        match = abs(float(pg_sum) - float(ts_sum)) < 0.01
        
        return {
            'match': match,
            'pg': float(pg_sum),
            'ts': float(ts_sum),
            'details': f'Total: {pg_sum:,.2f}'
        }
    
    def _test_avg_amount(self, verbose):
        """Test average aggregation."""
        pg_avg = PaymentTransaction.objects.using('default').aggregate(
            avg=Avg('amount')
        )['avg'] or 0
        
        ts_avg = PaymentTransaction.objects.using('timescale').aggregate(
            avg=Avg('amount')
        )['avg'] or 0
        
        match = abs(float(pg_avg) - float(ts_avg)) < 0.01
        
        return {
            'match': match,
            'pg': float(pg_avg),
            'ts': float(ts_avg),
            'details': f'Average: {pg_avg:,.2f}'
        }
    
    def _test_count_by_status(self, verbose):
        """Test grouping by status."""
        pg_counts = dict(PaymentTransaction.objects.using('default').values('status').annotate(
            count=Count('id')
        ).values_list('status', 'count'))
        
        ts_counts = dict(PaymentTransaction.objects.using('timescale').values('status').annotate(
            count=Count('id')
        ).values_list('status', 'count'))
        
        match = pg_counts == ts_counts
        
        return {
            'match': match,
            'pg': pg_counts,
            'ts': ts_counts,
            'details': f'Statuses: {list(pg_counts.keys())}'
        }
    
    def _test_recent_7_days(self, verbose):
        """Test date filtering."""
        cutoff = timezone.now() - timedelta(days=7)
        
        pg_count = PaymentTransaction.objects.using('default').filter(
            created_at__gte=cutoff
        ).count()
        
        ts_count = PaymentTransaction.objects.using('timescale').filter(
            created_at__gte=cutoff
        ).count()
        
        return {
            'match': pg_count == ts_count,
            'pg': pg_count,
            'ts': ts_count,
            'details': f'Last 7 days: {pg_count:,} transactions'
        }
    
    def _test_group_by_date(self, verbose):
        """Test date grouping."""
        from django.db.models.functions import TruncDate
        
        cutoff = timezone.now() - timedelta(days=7)
        
        pg_dates = list(PaymentTransaction.objects.using('default').filter(
            created_at__gte=cutoff
        ).annotate(
            trunc_date=TruncDate('created_at')
        ).values('trunc_date').annotate(
            count=Count('id')
        ).order_by('trunc_date').values_list('trunc_date', 'count'))
        
        ts_dates = list(PaymentTransaction.objects.using('timescale').filter(
            created_at__gte=cutoff
        ).annotate(
            trunc_date=TruncDate('created_at')
        ).values('trunc_date').annotate(
            count=Count('id')
        ).order_by('trunc_date').values_list('trunc_date', 'count'))
        
        return {
            'match': pg_dates == ts_dates,
            'pg': len(pg_dates),
            'ts': len(ts_dates),
            'details': f'{len(pg_dates)} unique dates'
        }
    
    def _test_filter_by_user(self, verbose):
        """Test user filtering."""
        # Get first user with transactions
        first_user = PaymentTransaction.objects.using('default').values_list(
            'user_id', flat=True
        ).first()
        
        if not first_user:
            return {'match': True, 'pg': 0, 'ts': 0, 'details': 'No users found'}
        
        pg_count = PaymentTransaction.objects.using('default').filter(
            user_id=first_user
        ).count()
        
        ts_count = PaymentTransaction.objects.using('timescale').filter(
            user_id=first_user
        ).count()
        
        return {
            'match': pg_count == ts_count,
            'pg': pg_count,
            'ts': ts_count,
            'details': f'User {first_user}: {pg_count} transactions'
        }
    
    def _test_complex_aggregation(self, verbose):
        """Test complex multi-field aggregation."""
        cutoff = timezone.now() - timedelta(days=30)
        
        pg_result = PaymentTransaction.objects.using('default').filter(
            created_at__gte=cutoff,
            status='completed'
        ).aggregate(
            count=Count('id'),
            total=Sum('amount'),
            avg=Avg('amount')
        )
        
        ts_result = PaymentTransaction.objects.using('timescale').filter(
            created_at__gte=cutoff,
            status='completed'
        ).aggregate(
            count=Count('id'),
            total=Sum('amount'),
            avg=Avg('amount')
        )
        
        match = (
            pg_result['count'] == ts_result['count'] and
            abs(float(pg_result['total'] or 0) - float(ts_result['total'] or 0)) < 0.01 and
            abs(float(pg_result['avg'] or 0) - float(ts_result['avg'] or 0)) < 0.01
        )
        
        return {
            'match': match,
            'pg': pg_result,
            'ts': ts_result,
            'details': f"Count: {pg_result['count']}, Total: {pg_result['total']}"
        }
