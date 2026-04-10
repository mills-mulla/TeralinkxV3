"""
Emergency Rollback Script
Quickly rollback TimescaleDB rollout if issues detected.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import FeatureFlag


class Command(BaseCommand):
    help = 'Emergency rollback of TimescaleDB rollout'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm rollback action'
        )
        parser.add_argument(
            '--to-percentage',
            type=int,
            default=0,
            help='Rollback to specific percentage (default: 0)'
        )
    
    def handle(self, *args, **options):
        confirm = options['confirm']
        to_percentage = options['to_percentage']
        
        if not confirm:
            self.stdout.write(self.style.WARNING(
                '\n⚠ ROLLBACK CONFIRMATION REQUIRED\n'
                'This will reduce TimescaleDB rollout percentage.\n'
                'Add --confirm to proceed.\n'
            ))
            return
        
        self.stdout.write(self.style.ERROR(
            f'\n=== EMERGENCY ROLLBACK ===\n'
            f'Rolling back to {to_percentage}%\n'
        ))
        
        try:
            flag = FeatureFlag.objects.get(name='timescaledb_migration')
            old_percentage = flag.rollout_percentage
            
            if to_percentage >= old_percentage:
                self.stdout.write(self.style.ERROR(
                    f'Cannot rollback from {old_percentage}% to {to_percentage}%'
                ))
                return
            
            # Perform rollback
            flag.rollout_percentage = to_percentage
            if to_percentage == 0:
                flag.enabled = False
            flag.save()
            
            self.stdout.write(self.style.SUCCESS(
                f'\n✓ Rollback complete: {old_percentage}% → {to_percentage}%'
            ))
            
            # Log rollback
            self._log_rollback(old_percentage, to_percentage)
            
            self.stdout.write(self.style.WARNING(
                '\n⚠ Next steps:\n'
                '1. Investigate root cause\n'
                '2. Fix issues\n'
                '3. Re-enable rollout when ready\n'
            ))
            
        except FeatureFlag.DoesNotExist:
            self.stdout.write(self.style.ERROR('Feature flag not found'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Rollback failed: {e}'))
    
    def _log_rollback(self, from_pct, to_pct):
        """Log rollback event."""
        import logging
        logger = logging.getLogger('finance.timescale')
        logger.warning(
            f'TimescaleDB rollback: {from_pct}% → {to_pct}% at {timezone.now()}'
        )
