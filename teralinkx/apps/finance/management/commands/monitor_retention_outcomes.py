"""
Monitor retention task outcomes and update predictions.
Run daily via Celery Beat.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.finance.models_churn import RetentionTask, ChurnPrediction


class Command(BaseCommand):
    help = 'Monitor retention task outcomes and detect relocated customers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Check tasks from last N days'
        )

    def handle(self, *args, **options):
        days = options['days']
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Get completed tasks without outcomes
        pending_outcome_tasks = RetentionTask.objects.filter(
            status='completed',
            outcome='pending',
            action_taken_at__gte=cutoff_date
        )
        
        self.stdout.write(f"Checking {pending_outcome_tasks.count()} tasks...")
        
        retained_count = 0
        churned_count = 0
        relocated_count = 0
        
        for task in pending_outcome_tasks:
            outcome = self._check_customer_status(task)
            
            if outcome == 'retained':
                task.mark_outcome('retained', 'Customer made payment after retention action')
                retained_count += 1
            elif outcome == 'churned':
                task.mark_outcome('churned', 'No activity for 60+ days')
                churned_count += 1
            elif outcome == 'relocated':
                task.mark_outcome('relocated', 'Customer relocated outside coverage area')
                relocated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Outcomes updated: {retained_count} retained, "
                f"{churned_count} churned, {relocated_count} relocated"
            )
        )

    def _check_customer_status(self, task):
        """Check customer status to determine outcome"""
        customer = task.customer
        action_date = task.action_taken_at
        
        # Check for payments after action
        from apps.finance.models import PaymentTransaction
        recent_payments = PaymentTransaction.objects.filter(
            user=customer,
            created_at__gte=action_date
        ).exists()
        
        if recent_payments:
            return 'retained'
        
        # Check for relocation indicators
        if self._is_relocated(customer):
            return 'relocated'
        
        # Check if churned (no activity for 60+ days)
        days_since_action = (timezone.now() - action_date).days
        if days_since_action >= 60:
            return 'churned'
        
        return 'pending'

    def _is_relocated(self, customer):
        """Detect if customer relocated outside coverage area"""
        # Check for relocation indicators:
        # 1. Customer explicitly marked as relocated
        if hasattr(customer, 'status') and customer.status == 'relocated':
            return True
        
        # 2. No sessions from usual location for 30+ days
        # TODO: Implement location-based detection when session data available
        
        return False
