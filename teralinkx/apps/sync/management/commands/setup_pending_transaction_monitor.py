from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json


class Command(BaseCommand):
    help = 'Setup periodic task to monitor pending transactions'

    def handle(self, *args, **options):
        # Create interval: every 1 minute
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=2,
            period=IntervalSchedule.MINUTES,
        )

        # Create periodic task
        task, created = PeriodicTask.objects.get_or_create(
            name='Query Pending Transactions',
            defaults={
                'interval': schedule,
                'task': 'finance.tasks.check_pending_transactions',
                'enabled': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created periodic task: check_pending_transactions (every 2 minutes)'))
        else:
            self.stdout.write(self.style.SUCCESS('✓ Updated periodic task: check_pending_transactions'))
