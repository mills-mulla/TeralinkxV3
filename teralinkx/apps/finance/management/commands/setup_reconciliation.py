"""
Management command to set up M-Pesa Pull reconciliation periodic task.
Run once after deployment: python manage.py setup_reconciliation
"""
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Register M-Pesa Pull reconciliation as a periodic Celery Beat task'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=30,
            help='Interval in minutes between reconciliation runs (default: 30)'
        )
        parser.add_argument(
            '--nominated-number',
            type=str,
            help='Register shortcode with Pull API using this nominated number'
        )

    def handle(self, *args, **options):
        from django_celery_beat.models import PeriodicTask, IntervalSchedule

        interval_minutes = options['interval']

        # Create or get interval schedule
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=interval_minutes,
            period=IntervalSchedule.MINUTES
        )

        # Create or update the periodic task
        task, created = PeriodicTask.objects.update_or_create(
            name='mpesa-pull-reconciliation',
            defaults={
                'task': 'finance.tasks.reconcile_missed_mpesa_callbacks',
                'interval': schedule,
                'enabled': True,
                'description': (
                    'Queries M-Pesa Pull API every 30 minutes to recover '
                    'transactions whose callbacks were missed. Populates '
                    'PaymentTransaction for each recovered transaction.'
                )
            }
        )

        action = 'Created' if created else 'Updated'
        self.stdout.write(
            self.style.SUCCESS(
                f'{action} periodic task: "{task.name}" '
                f'running every {interval_minutes} minutes'
            )
        )

        # Optionally register with Pull API
        nominated_number = options.get('nominated_number')
        if nominated_number:
            from finance.payment_gateway import MpesaPullReconciliation
            try:
                result = MpesaPullReconciliation.register_pull(nominated_number)
                self.stdout.write(
                    self.style.SUCCESS(f'Pull API registration: {result}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Pull API registration failed: {e}')
                )
        else:
            self.stdout.write(
                self.style.WARNING(
                    'Tip: Pass --nominated-number=<phone> to also register '
                    'your shortcode with the Pull API (required once before going live)'
                )
            )
