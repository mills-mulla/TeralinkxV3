"""
Test Churn Prediction System
Tests rule-based churn prediction and retention workflow.
"""
from django.core.management.base import BaseCommand
from apps.finance.models_churn import ChurnPrediction, RetentionTask
from users.models import ClientH


class Command(BaseCommand):
    help = 'Test churn prediction and retention workflow'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== CHURN PREDICTION TEST ===\n'))
        
        # Get first customer
        customer = ClientH.objects.first()
        
        if not customer:
            self.stdout.write(self.style.ERROR('No customers found in database'))
            return
        
        self.stdout.write(f'Testing with customer: {customer.account}')
        
        # Create churn prediction
        self.stdout.write('\n1. Creating churn prediction...')
        prediction = ChurnPrediction.create_prediction(customer, method='rule_based')
        
        self.stdout.write(self.style.SUCCESS(f'   ✓ Prediction created'))
        self.stdout.write(f'   - Churn Score: {prediction.churn_score:.2f}')
        self.stdout.write(f'   - Risk Level: {prediction.risk_level}')
        self.stdout.write(f'   - Method: {prediction.prediction_method}')
        
        # Display risk factors
        self.stdout.write('\n2. Risk Factors:')
        for factor, data in prediction.risk_factors.items():
            self.stdout.write(f'   - {factor}: {data["value"]} (score: {data["score"]:.2f})')
        
        # Display top factors
        self.stdout.write('\n3. Top Contributing Factors:')
        for i, factor in enumerate(prediction.top_factors, 1):
            self.stdout.write(f'   {i}. {factor["factor"]}: {factor["value"]} (score: {factor["score"]:.2f})')
        
        # Create retention task
        self.stdout.write('\n4. Creating retention task...')
        
        # Set MRR for testing
        prediction.monthly_recurring_revenue = 3000  # Medium-value customer
        prediction.save()
        
        task = RetentionTask.create_retention_task(prediction)
        
        self.stdout.write(self.style.SUCCESS(f'   ✓ Retention task created'))
        self.stdout.write(f'   - Action Type: {task.action_type}')
        self.stdout.write(f'   - Priority Score: {task.priority_score:.2f}')
        self.stdout.write(f'   - MRR: KES {task.monthly_recurring_revenue}')
        self.stdout.write(f'   - Revenue at Risk: KES {task.revenue_at_risk}')
        self.stdout.write(f'   - Status: {task.status}')
        
        # Test action execution
        self.stdout.write('\n5. Executing retention action...')
        success = task.execute_action()
        
        if success:
            self.stdout.write(self.style.SUCCESS(f'   ✓ Action executed successfully'))
            self.stdout.write(f'   - Status: {task.status}')
            self.stdout.write(f'   - Action Details: {task.action_details}')
        else:
            self.stdout.write(self.style.ERROR(f'   ✗ Action execution failed'))
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n\n=== TEST COMPLETE ==='))
        self.stdout.write(f'Churn Prediction ID: {prediction.id}')
        self.stdout.write(f'Retention Task ID: {task.id}')
        
        # Statistics
        self.stdout.write('\n=== SYSTEM STATISTICS ===')
        total_predictions = ChurnPrediction.objects.count()
        active_predictions = ChurnPrediction.objects.filter(is_active=True).count()
        high_risk = ChurnPrediction.objects.filter(risk_level='high', is_active=True).count()
        critical_risk = ChurnPrediction.objects.filter(risk_level='critical', is_active=True).count()
        
        self.stdout.write(f'Total Predictions: {total_predictions}')
        self.stdout.write(f'Active Predictions: {active_predictions}')
        self.stdout.write(f'High Risk Customers: {high_risk}')
        self.stdout.write(f'Critical Risk Customers: {critical_risk}')
        
        total_tasks = RetentionTask.objects.count()
        pending_tasks = RetentionTask.objects.filter(status='pending').count()
        completed_tasks = RetentionTask.objects.filter(status='completed').count()
        
        self.stdout.write(f'\nTotal Retention Tasks: {total_tasks}')
        self.stdout.write(f'Pending Tasks: {pending_tasks}')
        self.stdout.write(f'Completed Tasks: {completed_tasks}')
