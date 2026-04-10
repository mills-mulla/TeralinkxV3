"""
Test Retention Workflow
Tests automated retention task creation and outcome monitoring.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.finance.models_churn import ChurnPrediction, RetentionTask
from apps.finance.models import PaymentTransaction
from apps.users.models import ClientH


class Command(BaseCommand):
    help = 'Test retention workflow end-to-end'

    def handle(self, *args, **options):
        self.stdout.write("=== Testing Retention Workflow ===\n")
        
        # Test 1: Create retention tasks for high-risk customers
        self.stdout.write("Test 1: Creating retention tasks...")
        high_risk_predictions = ChurnPrediction.objects.filter(
            risk_level__in=['high', 'critical'],
            is_active=True
        )[:3]
        
        tasks_created = 0
        for prediction in high_risk_predictions:
            # Check if task already exists
            existing_task = RetentionTask.objects.filter(
                customer=prediction.customer,
                status__in=['pending', 'in_progress']
            ).exists()
            
            if not existing_task:
                task = RetentionTask.create_retention_task(prediction)
                self.stdout.write(
                    f"  ✓ Created {task.action_type} for {task.customer.account} "
                    f"(MRR: {task.monthly_recurring_revenue}, Priority: {task.priority_score:.2f})"
                )
                tasks_created += 1
        
        if tasks_created == 0:
            self.stdout.write(self.style.WARNING("  No new tasks created (already exist)"))
        else:
            self.stdout.write(self.style.SUCCESS(f"  Created {tasks_created} retention tasks\n"))
        
        # Test 2: Execute automated actions
        self.stdout.write("Test 2: Executing automated actions...")
        pending_tasks = RetentionTask.objects.filter(
            status='pending',
            automated=True
        )[:3]
        
        executed_count = 0
        for task in pending_tasks:
            success = task.execute_action()
            if success:
                self.stdout.write(
                    f"  ✓ Executed {task.action_type} for {task.customer.account}"
                )
                executed_count += 1
            else:
                self.stdout.write(
                    self.style.ERROR(f"  ✗ Failed to execute {task.action_type}")
                )
        
        if executed_count > 0:
            self.stdout.write(self.style.SUCCESS(f"  Executed {executed_count} actions\n"))
        else:
            self.stdout.write(self.style.WARNING("  No pending tasks to execute\n"))
        
        # Test 3: Monitor outcomes
        self.stdout.write("Test 3: Monitoring retention outcomes...")
        completed_tasks = RetentionTask.objects.filter(
            status='completed',
            outcome='pending'
        )[:5]
        
        outcomes_updated = 0
        for task in completed_tasks:
            customer = task.customer
            action_date = task.action_taken_at
            
            # Check for recent payments
            recent_payments = PaymentTransaction.objects.filter(
                user=customer,
                created_at__gte=action_date
            ).exists()
            
            if recent_payments:
                task.mark_outcome('retained', 'Customer made payment after retention action')
                self.stdout.write(
                    f"  ✓ {customer.account} RETAINED (payment received)"
                )
                outcomes_updated += 1
            else:
                days_since_action = (timezone.now() - action_date).days
                if days_since_action >= 60:
                    task.mark_outcome('churned', 'No activity for 60+ days')
                    self.stdout.write(
                        f"  ✗ {customer.account} CHURNED (no activity {days_since_action} days)"
                    )
                    outcomes_updated += 1
        
        if outcomes_updated > 0:
            self.stdout.write(self.style.SUCCESS(f"  Updated {outcomes_updated} outcomes\n"))
        else:
            self.stdout.write(self.style.WARNING("  No outcomes to update\n"))
        
        # Test 4: Generate retention report
        self.stdout.write("Test 4: Generating retention report...")
        self._generate_report()
        
        self.stdout.write(self.style.SUCCESS("\n=== Retention Workflow Test Complete ==="))

    def _generate_report(self):
        """Generate retention effectiveness report"""
        # Get all retention tasks
        all_tasks = RetentionTask.objects.all()
        
        # Overall stats
        total_tasks = all_tasks.count()
        completed_tasks = all_tasks.filter(status='completed').count()
        
        # Outcome breakdown
        retained = all_tasks.filter(outcome='retained').count()
        churned = all_tasks.filter(outcome='churned').count()
        relocated = all_tasks.filter(outcome='relocated').count()
        pending = all_tasks.filter(outcome='pending').count()
        
        # Revenue metrics
        total_revenue_at_risk = all_tasks.aggregate(
            total=models.Sum('revenue_at_risk')
        )['total'] or 0
        
        retained_revenue = all_tasks.filter(outcome='retained').aggregate(
            total=models.Sum('revenue_at_risk')
        )['total'] or 0
        
        # Calculate retention rate
        retention_rate = (retained / (retained + churned) * 100) if (retained + churned) > 0 else 0
        
        self.stdout.write(f"\n  Total Tasks: {total_tasks}")
        self.stdout.write(f"  Completed: {completed_tasks}")
        self.stdout.write(f"\n  Outcomes:")
        self.stdout.write(f"    Retained: {retained}")
        self.stdout.write(f"    Churned: {churned}")
        self.stdout.write(f"    Relocated: {relocated}")
        self.stdout.write(f"    Pending: {pending}")
        self.stdout.write(f"\n  Retention Rate: {retention_rate:.1f}%")
        self.stdout.write(f"  Total Revenue at Risk: KES {total_revenue_at_risk:,.2f}")
        self.stdout.write(f"  Revenue Retained: KES {retained_revenue:,.2f}")


from django.db import models
