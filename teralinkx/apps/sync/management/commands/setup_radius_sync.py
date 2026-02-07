# apps/sync/management/commands/setup_radius_sync.py
from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule


class Command(BaseCommand):
    help = 'Setup Celery Beat schedules for RADIUS usage sync'

    def handle(self, *args, **options):
        self.stdout.write('Setting up RADIUS sync schedules...')

        # Create intervals
        interval_5min, _ = IntervalSchedule.objects.get_or_create(
            every=5,
            period=IntervalSchedule.MINUTES,
        )

        interval_2min, _ = IntervalSchedule.objects.get_or_create(
            every=2,
            period=IntervalSchedule.MINUTES,
        )

        # Create/update task for all active vouchers (every 5 minutes)
        task_all, created = PeriodicTask.objects.update_or_create(
            name='Sync RADIUS Usage - All Active Vouchers',
            defaults={
                'task': 'sync.tasks.sync_radius_usage_all',
                'interval': interval_5min,
                'enabled': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created task: {task_all.name}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✓ Updated task: {task_all.name}'))

        # Create/update task for critical vouchers (every 2 minutes)
        task_critical, created = PeriodicTask.objects.update_or_create(
            name='Sync RADIUS Usage - Critical Vouchers',
            defaults={
                'task': 'sync.tasks.sync_radius_usage_critical',
                'interval': interval_2min,
                'enabled': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created task: {task_critical.name}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✓ Updated task: {task_critical.name}'))

        self.stdout.write(self.style.SUCCESS('\n✅ RADIUS sync schedules configured successfully!'))
        self.stdout.write('\nScheduled tasks:')
        self.stdout.write(f'  - All active vouchers: Every 5 minutes')
        self.stdout.write(f'  - Critical vouchers (>80% data): Every 2 minutes')
