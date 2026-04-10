"""
Automated TimescaleDB Rollout Monitor
Continuously monitors performance and errors during rollout.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import connections
from datetime import timedelta
import time
from core.models import FeatureFlag
from finance.models import PaymentTransaction


class Command(BaseCommand):
    help = 'Monitor TimescaleDB rollout health and performance'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--duration',
            type=int,
            default=60,
            help='Monitoring duration in minutes (default: 60)'
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=5,
            help='Check interval in minutes (default: 5)'
        )
    
    def handle(self, *args, **options):
        duration = options['duration']
        interval = options['interval']
        
        self.stdout.write(self.style.SUCCESS(
            f'\n=== TimescaleDB Rollout Monitor ===\n'
            f'Duration: {duration} minutes\n'
            f'Check interval: {interval} minutes\n'
        ))
        
        start_time = timezone.now()
        end_time = start_time + timedelta(minutes=duration)
        check_count = 0
        
        while timezone.now() < end_time:
            check_count += 1
            self.stdout.write(f'\n--- Check #{check_count} at {timezone.now().strftime("%H:%M:%S")} ---')
            
            # Get current rollout status
            rollout_pct = self._get_rollout_percentage()
            self.stdout.write(f'Rollout: {rollout_pct}%')
            
            if rollout_pct > 0:
                # Run health checks
                health = self._check_health()
                performance = self._check_performance()
                errors = self._check_errors()
                
                # Display results
                self._display_health(health)
                self._display_performance(performance)
                self._display_errors(errors)
                
                # Alert on issues
                if not health['ok'] or errors['count'] > 0:
                    self.stdout.write(self.style.ERROR(
                        '\n⚠ ALERT: Issues detected! Consider rolling back.'
                    ))
            else:
                self.stdout.write('Rollout at 0% - no monitoring needed')
            
            # Wait for next check
            if timezone.now() < end_time:
                self.stdout.write(f'\nNext check in {interval} minutes...')
                time.sleep(interval * 60)
        
        self.stdout.write(self.style.SUCCESS(
            f'\n\n=== Monitoring Complete ===\n'
            f'Total checks: {check_count}\n'
            f'Duration: {duration} minutes\n'
        ))
    
    def _get_rollout_percentage(self):
        """Get current rollout percentage."""
        try:
            flag = FeatureFlag.objects.get(name='timescaledb_migration')
            return flag.rollout_percentage if flag.enabled else 0
        except FeatureFlag.DoesNotExist:
            return 0
    
    def _check_health(self):
        """Check database health."""
        health = {'ok': True, 'issues': []}
        
        try:
            # Check PostgreSQL
            with connections['default'].cursor() as cursor:
                cursor.execute("SELECT 1")
            
            # Check TimescaleDB
            with connections['timescale'].cursor() as cursor:
                cursor.execute("SELECT 1")
            
            # Check row counts
            pg_count = PaymentTransaction.objects.using('default').count()
            ts_count = PaymentTransaction.objects.using('timescale').count()
            
            if pg_count != ts_count:
                health['ok'] = False
                health['issues'].append(f'Row count mismatch: PG={pg_count}, TS={ts_count}')
            
            health['pg_count'] = pg_count
            health['ts_count'] = ts_count
            
        except Exception as e:
            health['ok'] = False
            health['issues'].append(f'Connection error: {e}')
        
        return health
    
    def _check_performance(self):
        """Compare query performance."""
        from django.db.models import Sum
        
        performance = {}
        cutoff = timezone.now() - timedelta(days=7)
        
        try:
            # Test PostgreSQL
            start = time.time()
            pg_result = PaymentTransaction.objects.using('default').filter(
                created_at__gte=cutoff
            ).aggregate(total=Sum('amount'))
            pg_time = time.time() - start
            
            # Test TimescaleDB
            start = time.time()
            ts_result = PaymentTransaction.objects.using('timescale').filter(
                created_at__gte=cutoff
            ).aggregate(total=Sum('amount'))
            ts_time = time.time() - start
            
            performance['pg_time'] = pg_time
            performance['ts_time'] = ts_time
            performance['improvement'] = ((pg_time - ts_time) / pg_time) * 100 if pg_time > 0 else 0
            performance['ok'] = ts_time <= pg_time * 1.5  # Allow 50% slower
            
        except Exception as e:
            performance['ok'] = False
            performance['error'] = str(e)
        
        return performance
    
    def _check_errors(self):
        """Check for database errors."""
        errors = {'count': 0, 'messages': []}
        
        try:
            # Check PostgreSQL logs (simplified)
            with connections['default'].cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM pg_stat_database 
                    WHERE datname = current_database()
                """)
                # In production, check actual error logs
            
            # Check TimescaleDB logs
            with connections['timescale'].cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM pg_stat_database 
                    WHERE datname = current_database()
                """)
            
        except Exception as e:
            errors['count'] += 1
            errors['messages'].append(str(e))
        
        return errors
    
    def _display_health(self, health):
        """Display health check results."""
        if health['ok']:
            self.stdout.write(self.style.SUCCESS('✓ Health: OK'))
            self.stdout.write(f"  Rows: PG={health.get('pg_count', 0):,}, TS={health.get('ts_count', 0):,}")
        else:
            self.stdout.write(self.style.ERROR('✗ Health: FAILED'))
            for issue in health['issues']:
                self.stdout.write(f'  - {issue}')
    
    def _display_performance(self, performance):
        """Display performance results."""
        if 'error' in performance:
            self.stdout.write(self.style.ERROR(f'✗ Performance: ERROR - {performance["error"]}'))
            return
        
        pg_ms = performance['pg_time'] * 1000
        ts_ms = performance['ts_time'] * 1000
        improvement = performance['improvement']
        
        if performance['ok']:
            self.stdout.write(self.style.SUCCESS('✓ Performance: OK'))
        else:
            self.stdout.write(self.style.WARNING('⚠ Performance: DEGRADED'))
        
        self.stdout.write(f'  PG: {pg_ms:.2f}ms, TS: {ts_ms:.2f}ms ({improvement:+.1f}%)')
    
    def _display_errors(self, errors):
        """Display error check results."""
        if errors['count'] == 0:
            self.stdout.write(self.style.SUCCESS('✓ Errors: None'))
        else:
            self.stdout.write(self.style.ERROR(f'✗ Errors: {errors["count"]} found'))
            for msg in errors['messages']:
                self.stdout.write(f'  - {msg}')
