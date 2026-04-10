"""
Enable TimescaleDB Rollout
Gradually increase rollout percentage with safety checks.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import FeatureFlag
from finance.models import PaymentTransaction, TransactionQueue


class Command(BaseCommand):
    help = 'Enable TimescaleDB rollout with specified percentage'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--percentage',
            type=int,
            required=True,
            help='Rollout percentage (0-100)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip safety checks'
        )
    
    def handle(self, *args, **options):
        percentage = options['percentage']
        force = options['force']
        
        if percentage < 0 or percentage > 100:
            self.stdout.write(self.style.ERROR('Percentage must be between 0 and 100'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'\n=== TimescaleDB Rollout: {percentage}% ===\n'))
        
        # Safety checks
        if not force:
            self.stdout.write('Running safety checks...')
            
            # Check data integrity
            if not self._check_data_integrity():
                self.stdout.write(self.style.ERROR('Data integrity check failed. Use --force to override.'))
                return
            
            # Check TimescaleDB availability
            if not self._check_timescale_available():
                self.stdout.write(self.style.ERROR('TimescaleDB not available. Use --force to override.'))
                return
            
            self.stdout.write(self.style.SUCCESS('✓ Safety checks passed'))
        
        # Update feature flag
        try:
            flag = FeatureFlag.objects.get(name='timescaledb_migration')
            old_percentage = flag.rollout_percentage
            
            flag.enabled = True
            flag.rollout_percentage = percentage
            flag.save()
            
            self.stdout.write(self.style.SUCCESS(
                f'\n✓ Rollout updated: {old_percentage}% → {percentage}%'
            ))
            
            # Calculate affected queries
            if percentage > 0:
                total_transactions = PaymentTransaction.objects.count()
                affected = int(total_transactions * percentage / 100)
                self.stdout.write(f'\nEstimated affected queries: ~{affected:,} transactions')
            
            self.stdout.write(self.style.WARNING(
                f'\n⚠ Monitor performance with: python manage.py monitor_timescale'
            ))
            
        except FeatureFlag.DoesNotExist:
            self.stdout.write(self.style.ERROR('Feature flag not found. Run init_timescale_flag first.'))
    
    def _check_data_integrity(self):
        """Verify data integrity between databases."""
        try:
            pg_count = PaymentTransaction.objects.using('default').count()
            ts_count = PaymentTransaction.objects.using('timescale').count()
            
            if pg_count != ts_count:
                self.stdout.write(self.style.WARNING(
                    f'  Row count mismatch: PostgreSQL={pg_count}, TimescaleDB={ts_count}'
                ))
                return False
            
            self.stdout.write(f'  ✓ Row counts match: {pg_count:,} transactions')
            return True
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  Error checking integrity: {e}'))
            return False
    
    def _check_timescale_available(self):
        """Check if TimescaleDB is accessible."""
        try:
            from django.db import connections
            with connections['timescale'].cursor() as cursor:
                cursor.execute("SELECT 1")
            self.stdout.write('  ✓ TimescaleDB connection OK')
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  TimescaleDB connection failed: {e}'))
            return False
