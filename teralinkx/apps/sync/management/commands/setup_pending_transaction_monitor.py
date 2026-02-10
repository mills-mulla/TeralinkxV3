from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json


class Command(BaseCommand):
    help = 'Setup periodic task to monitor pending transactions'

    def handle(self, *args, **options):
        # Create interval: every 1 minute
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.MINUTES,
        )

        # Create periodic task
        task, created = PeriodicTask.objects.get_or_create(
            name='Query Pending Transactions',
            defaults={
                'interval': schedule,
                'task': 'sync.tasks.task_query_pending_transactions',
                'enabled': True,
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created periodic task: Query Pending Transactions (every 1 minute)'))
        else:
            task.interval = schedule
            task.enabled = True
            task.save()
            self.stdout.write(self.style.SUCCESS('✓ Updated periodic task: Query Pending Transactions'))
