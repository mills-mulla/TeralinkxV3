"""
Initialize TimescaleDB Feature Flag
Creates the feature flag for gradual TimescaleDB migration rollout.
"""
from django.core.management.base import BaseCommand
from core.models import FeatureFlag


class Command(BaseCommand):
    help = 'Initialize TimescaleDB feature flag for gradual migration'
    
    def handle(self, *args, **options):
        flag, created = FeatureFlag.objects.get_or_create(
            name='timescaledb_migration',
            defaults={
                'description': 'Gradual migration of finance queries to TimescaleDB hypertables',
                'enabled': False,
                'rollout_percentage': 0
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(
                f'✓ Created TimescaleDB feature flag (0% rollout, disabled)'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f'Feature flag already exists:\n'
                f'  Enabled: {flag.enabled}\n'
                f'  Rollout: {flag.rollout_percentage}%'
            ))
        
        self.stdout.write('\nNext steps:')
        self.stdout.write('1. Run: python manage.py setup_timescaledb')
        self.stdout.write('2. Enable flag: flag.enable()')
        self.stdout.write('3. Increase rollout: flag.set_rollout_percentage(10)')
        self.stdout.write('4. Monitor: python manage.py monitor_timescale')
