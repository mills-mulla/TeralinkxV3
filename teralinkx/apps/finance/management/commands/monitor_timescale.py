"""
Monitor TimescaleDB Performance
Compares query performance between PostgreSQL and TimescaleDB.
"""
from django.core.management.base import BaseCommand
from django.db import connections
from django.utils import timezone
from datetime import timedelta
import time
from finance.models import PaymentTransaction, TransactionQueue


class Command(BaseCommand):
    help = 'Monitor and compare PostgreSQL vs TimescaleDB query performance'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to query (default: 30)'
        )
        parser.add_argument(
            '--iterations',
            type=int,
            default=5,
            help='Number of test iterations (default: 5)'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        iterations = options['iterations']
        
        self.stdout.write(self.style.SUCCESS(f'\n=== TimescaleDB Performance Monitor ==='))
        self.stdout.write(f'Testing {iterations} iterations over {days} days of data\n')
        
        # Test queries
        queries = [
            ('Count transactions', self._test_count),
            ('Sum amounts', self._test_sum),
            ('Group by date', self._test_group_by_date),
            ('Filter by status', self._test_filter_status),
            ('Recent transactions', self._test_recent),
        ]
        
        results = {}
        
        for query_name, query_func in queries:
            self.stdout.write(f'\nTesting: {query_name}')
            pg_times = []
            ts_times = []
            
            for i in range(iterations):
                # Test PostgreSQL
                pg_time = query_func('default', days)
                pg_times.append(pg_time)
                
                # Test TimescaleDB (if configured)
                try:
                    ts_time = query_func('timescale', days)
                    ts_times.append(ts_time)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'  TimescaleDB not available: {e}'))
                    ts_times = None
                    break
            
            # Calculate averages
            pg_avg = sum(pg_times) / len(pg_times)
            results[query_name] = {'pg': pg_avg}
            
            if ts_times:
                ts_avg = sum(ts_times) / len(ts_times)
                results[query_name]['ts'] = ts_avg
                improvement = ((pg_avg - ts_avg) / pg_avg) * 100
                results[query_name]['improvement'] = improvement
        
        # Display results
        self._display_results(results)
    
    def _test_count(self, db, days):
        """Test simple count query."""
        start = time.time()
        cutoff = timezone.now() - timedelta(days=days)
        count = PaymentTransaction.objects.using(db).filter(created_at__gte=cutoff).count()
        elapsed = time.time() - start
        return elapsed
    
    def _test_sum(self, db, days):
        """Test aggregation query."""
        from django.db.models import Sum
        start = time.time()
        cutoff = timezone.now() - timedelta(days=days)
        total = PaymentTransaction.objects.using(db).filter(
            created_at__gte=cutoff
        ).aggregate(total=Sum('amount'))
        elapsed = time.time() - start
        return elapsed
    
    def _test_group_by_date(self, db, days):
        """Test group by date query."""
        from django.db.models import Count
        from django.db.models.functions import TruncDate
        start = time.time()
        cutoff = timezone.now() - timedelta(days=days)
        results = PaymentTransaction.objects.using(db).filter(
            created_at__gte=cutoff
        ).annotate(trunc_date=TruncDate('created_at')).values('trunc_date').annotate(count=Count('id'))[:10]
        list(results)  # Force evaluation
        elapsed = time.time() - start
        return elapsed
    
    def _test_filter_status(self, db, days):
        """Test filtered query."""
        start = time.time()
        cutoff = timezone.now() - timedelta(days=days)
        results = PaymentTransaction.objects.using(db).filter(
            created_at__gte=cutoff,
            status='completed'
        )[:100]
        list(results)  # Force evaluation
        elapsed = time.time() - start
        return elapsed
    
    def _test_recent(self, db, days):
        """Test recent records query."""
        start = time.time()
        results = PaymentTransaction.objects.using(db).order_by('-created_at')[:50]
        list(results)  # Force evaluation
        elapsed = time.time() - start
        return elapsed
    
    def _display_results(self, results):
        """Display performance comparison results."""
        self.stdout.write(self.style.SUCCESS('\n\n=== Performance Results ===\n'))
        
        self.stdout.write(f'{"Query":<25} {"PostgreSQL":<15} {"TimescaleDB":<15} {"Improvement":<15}')
        self.stdout.write('-' * 70)
        
        for query_name, data in results.items():
            pg_time = f"{data['pg']*1000:.2f}ms"
            
            if 'ts' in data:
                ts_time = f"{data['ts']*1000:.2f}ms"
                improvement = f"{data['improvement']:+.1f}%"
                
                if data['improvement'] > 0:
                    improvement = self.style.SUCCESS(improvement)
                elif data['improvement'] < 0:
                    improvement = self.style.ERROR(improvement)
                
                self.stdout.write(f'{query_name:<25} {pg_time:<15} {ts_time:<15} {improvement}')
            else:
                self.stdout.write(f'{query_name:<25} {pg_time:<15} {"N/A":<15} {"N/A":<15}')
        
        self.stdout.write('')
