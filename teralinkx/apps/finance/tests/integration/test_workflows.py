# apps/finance/tests/integration/test_workflows.py
"""
Integration Tests for Finance Workflows
Tests end-to-end business processes.
"""
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from unittest.mock import patch, Mock

from finance.models import Currency, PaymentGateway, Department, Expense
from finance.models_churn import ChurnPrediction, RetentionTask
from finance.models_board_report import BoardReport
from finance.board_report_service import BoardReportService
from finance.signals import payment_completed, expense_created


class ChurnRetentionWorkflowTest(TransactionTestCase):
    """Test churn prediction to retention workflow"""
    
    def setUp(self):
        self.currency = Currency.objects.create(
            code='KES',
            name='Kenyan Shilling',
            is_base_currency=True
        )
    
    def test_high_churn_creates_retention_task(self):
        """Test that high churn prediction creates retention task"""
        # Create high-risk churn prediction
        prediction = ChurnPrediction.objects.create(
            customer_id=1,
            churn_probability=0.85,
            model_version='v1',
            predicted_revenue_at_risk=Decimal('5000.00'),
            explanation={'top_factors': [
                {'factor': 'No session in 30 days', 'impact': '+40%'}
            ]}
        )
        
        # Create retention task
        task = RetentionTask.create_retention_task(prediction)
        
        self.assertIsNotNone(task)
        self.assertEqual(task.customer_id, 1)
        self.assertGreater(task.priority_score, 0)
        self.assertIn(task.recommended_action, [
            'discount_offer', 'personal_call', 'sms_campaign'
        ])
    
    def test_retention_task_execution(self):
        """Test retention task execution"""
        prediction = ChurnPrediction.objects.create(
            customer_id=1,
            churn_probability=0.75,
            model_version='v1',
            predicted_revenue_at_risk=Decimal('3000.00')
        )
        
        task = RetentionTask.create_retention_task(prediction)
        
        # Execute automated action
        if task.automated:
            result = task.execute_action()
            self.assertTrue(result)
            self.assertEqual(task.status, 'completed')


class BoardReportGenerationWorkflowTest(TestCase):
    """Test board report generation workflow"""
    
    def setUp(self):
        self.currency = Currency.objects.create(
            code='KES',
            name='Kenyan Shilling',
            is_base_currency=True
        )
    
    def test_generate_monthly_report(self):
        """Test complete board report generation"""
        year = 2025
        month = 1
        
        report = BoardReportService.generate_monthly_report(year, month)
        
        self.assertIsNotNone(report)
        self.assertEqual(report.report_year, year)
        self.assertIn('revenue', report.financial_performance)
        self.assertIn('active_customers', report.customer_metrics)
        self.assertIsInstance(report.key_highlights, list)
        self.assertIsInstance(report.challenges, list)
        self.assertIsInstance(report.recommendations, list)
    
    def test_report_approval_workflow(self):
        """Test report approval workflow"""
        report = BoardReport.objects.create(
            report_year=2025,
            report_month=timezone.now().date().replace(day=1),
            financial_performance={'revenue': {'current': 1500000}},
            customer_metrics={'active_customers': 450},
            operational_metrics={'success_rate_pct': 98.5}
        )
        
        # Initially draft
        self.assertEqual(report.status, 'draft')
        
        # Approve report
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(username='approver', password='pass')
        
        report.mark_approved(user)
        
        self.assertEqual(report.status, 'approved')
        self.assertIsNotNone(report.approved_at)
        self.assertEqual(report.approved_by, user)


class BudgetAlertWorkflowTest(TestCase):
    """Test budget monitoring and alert workflow"""
    
    def setUp(self):
        self.currency = Currency.objects.create(
            code='KES',
            name='Kenyan Shilling',
            is_base_currency=True
        )
        self.department = Department.objects.create(
            name='Marketing',
            code='MKT',
            budget=Decimal('50000.00')
        )
    
    def test_budget_threshold_alert(self):
        """Test budget threshold exceeded alert"""
        # Create expenses that exceed 80% of budget
        Expense.objects.create(
            expense_date=timezone.now().date(),
            description='Campaign 1',
            amount=Decimal('30000.00'),
            currency=self.currency,
            category='Marketing',
            department=self.department,
            approval_status='paid'
        )
        
        Expense.objects.create(
            expense_date=timezone.now().date(),
            description='Campaign 2',
            amount=Decimal('15000.00'),
            currency=self.currency,
            category='Marketing',
            department=self.department,
            approval_status='paid'
        )
        
        # Check budget utilization
        utilization = self.department.budget_utilization
        
        self.assertGreater(utilization, 80)
        
        # Should trigger alert
        from finance.budget_service import BudgetService
        alerts = BudgetService.get_budget_alerts()
        
        marketing_alerts = [a for a in alerts if a['department'] == 'Marketing']
        self.assertGreater(len(marketing_alerts), 0)


class ReconciliationWorkflowTest(TestCase):
    """Test payment reconciliation workflow"""
    
    def setUp(self):
        self.currency = Currency.objects.create(
            code='KES',
            name='Kenyan Shilling',
            is_base_currency=True
        )
    
    def test_reconciliation_matching(self):
        """Test payment to invoice matching"""
        from finance.reconciliation_service import ReconciliationService
        from finance.models_reconciliation import ReconciliationJob
        
        # Create reconciliation job
        job = ReconciliationJob.objects.create(
            source='bank_statement',
            total_items=10
        )
        
        # Process reconciliation
        result = ReconciliationService.process_reconciliation_job(job.id)
        
        self.assertIn('matched_count', result)
        self.assertIn('unmatched_count', result)
        self.assertIn('auto_matched_count', result)


class EventBusIntegrationTest(TransactionTestCase):
    """Test event bus signal integration"""
    
    def setUp(self):
        self.currency = Currency.objects.create(
            code='KES',
            name='Kenyan Shilling',
            is_base_currency=True
        )
    
    @patch('apps.finance.handlers.refresh_churn_prediction_handler')
    def test_payment_completed_signal(self, mock_handler):
        """Test payment completed signal triggers churn refresh"""
        # Send payment completed signal
        payment_completed.send(
            sender=self.__class__,
            customer_id=1,
            amount=Decimal('1000.00')
        )
        
        # Handler should be called
        mock_handler.assert_called_once()
    
    @patch('apps.finance.handlers.recalculate_budget_handler')
    def test_expense_created_signal(self, mock_handler):
        """Test expense created signal triggers budget recalc"""
        department = Department.objects.create(
            name='Operations',
            code='OPS',
            budget=Decimal('100000.00')
        )
        
        # Create expense
        expense = Expense.objects.create(
            expense_date=timezone.now().date(),
            description='Test expense',
            amount=Decimal('5000.00'),
            currency=self.currency,
            category='Operations',
            department=department
        )
        
        # Send signal
        expense_created.send(
            sender=self.__class__,
            expense=expense
        )
        
        # Handler should be called
        mock_handler.assert_called_once()
