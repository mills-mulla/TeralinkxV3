# apps/finance/tests/unit/test_models.py
"""
Unit Tests for Finance Models
Tests model methods and properties.
"""
from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from finance.models import (
    Currency, ExchangeRate, PaymentGateway, PaymentTransaction,
    TransactionQueue, Expense, Department, BudgetCategory
)
from finance.models_churn import ChurnPrediction, RetentionTask
from finance.models_kpi import KPISnapshot, MLModel
from finance.models_board_report import BoardReport


class CurrencyModelTest(TestCase):
    """Test Currency model"""
    
    def test_create_currency(self):
        """Test currency creation"""
        currency = Currency.objects.create(
            code='USD',
            name='US Dollar',
            symbol='$',
            decimal_places=2
        )
        
        self.assertEqual(currency.code, 'USD')
        self.assertEqual(currency.name, 'US Dollar')
        self.assertEqual(str(currency), 'USD - US Dollar')
    
    def test_base_currency_uniqueness(self):
        """Test only one base currency allowed"""
        Currency.objects.create(
            code='KES',
            name='Kenyan Shilling',
            is_base_currency=True
        )
        
        usd = Currency.objects.create(
            code='USD',
            name='US Dollar',
            is_base_currency=True
        )
        
        # KES should no longer be base
        kes = Currency.objects.get(code='KES')
        self.assertFalse(kes.is_base_currency)
        self.assertTrue(usd.is_base_currency)


class PaymentGatewayModelTest(TestCase):
    """Test PaymentGateway model"""
    
    def setUp(self):
        self.currency = Currency.objects.create(
            code='KES',
            name='Kenyan Shilling',
            is_base_currency=True
        )
    
    def test_create_gateway(self):
        """Test payment gateway creation"""
        gateway = PaymentGateway.objects.create(
            name='M-Pesa',
            gateway_type='mpesa',
            default_currency=self.currency,
            config={'shortcode': '174379'}
        )
        
        self.assertEqual(gateway.name, 'M-Pesa')
        self.assertEqual(gateway.gateway_type, 'mpesa')
        self.assertTrue(gateway.is_active)
    
    def test_default_gateway(self):
        """Test default gateway setting"""
        gateway1 = PaymentGateway.objects.create(
            name='Gateway 1',
            gateway_type='mpesa',
            default_currency=self.currency,
            is_default=True
        )
        
        gateway2 = PaymentGateway.objects.create(
            name='Gateway 2',
            gateway_type='stripe',
            default_currency=self.currency,
            is_default=True
        )
        
        # Gateway 1 should no longer be default
        gateway1.refresh_from_db()
        self.assertFalse(gateway1.is_default)
        self.assertTrue(gateway2.is_default)


class TransactionQueueModelTest(TestCase):
    """Test TransactionQueue model"""
    
    def test_is_expired(self):
        """Test transaction expiry detection"""
        old_transaction = TransactionQueue.objects.create(
            queue_type='payment',
            initiator='254712345678',
            price=Decimal('1000.00'),
            status='pending',
            created_at=timezone.now() - timedelta(hours=25)
        )
        
        recent_transaction = TransactionQueue.objects.create(
            queue_type='payment',
            initiator='254712345678',
            price=Decimal('1000.00'),
            status='pending'
        )
        
        self.assertTrue(old_transaction.is_expired)
        self.assertFalse(recent_transaction.is_expired)
    
    def test_pending_duration(self):
        """Test pending duration calculation"""
        transaction = TransactionQueue.objects.create(
            queue_type='payment',
            initiator='254712345678',
            price=Decimal('1000.00'),
            status='pending',
            created_at=timezone.now() - timedelta(hours=2)
        )
        
        self.assertGreaterEqual(transaction.pending_duration_hours, 2)


class ExpenseModelTest(TestCase):
    """Test Expense model"""
    
    def setUp(self):
        self.currency = Currency.objects.create(
            code='KES',
            name='Kenyan Shilling',
            is_base_currency=True
        )
        self.department = Department.objects.create(
            name='Operations',
            code='OPS',
            budget=Decimal('100000.00')
        )
    
    def test_create_expense(self):
        """Test expense creation"""
        expense = Expense.objects.create(
            expense_date=timezone.now().date(),
            description='Office supplies',
            amount=Decimal('5000.00'),
            currency=self.currency,
            category='Office Supplies',
            department=self.department,
            vendor_name='Supplier A'
        )
        
        self.assertEqual(expense.amount, Decimal('5000.00'))
        self.assertEqual(expense.approval_status, 'draft')
    
    def test_capex_depreciation(self):
        """Test CAPEX depreciation calculation"""
        expense = Expense.objects.create(
            expense_date=timezone.now().date(),
            description='Server equipment',
            amount=Decimal('120000.00'),
            currency=self.currency,
            category='Equipment',
            department=self.department,
            is_capex=True,
            asset_life_years=5
        )
        
        monthly_depreciation = expense.monthly_depreciation
        expected = Decimal('120000.00') / (5 * 12)
        self.assertEqual(monthly_depreciation, expected)


class ChurnPredictionModelTest(TestCase):
    """Test ChurnPrediction model"""
    
    def test_risk_level_assignment(self):
        """Test automatic risk level assignment"""
        low_risk = ChurnPrediction.objects.create(
            customer_id=1,
            churn_probability=0.15,
            model_version='v1'
        )
        
        high_risk = ChurnPrediction.objects.create(
            customer_id=2,
            churn_probability=0.75,
            model_version='v1'
        )
        
        self.assertEqual(low_risk.risk_level, 'low')
        self.assertEqual(high_risk.risk_level, 'critical')


class KPISnapshotModelTest(TestCase):
    """Test KPISnapshot model"""
    
    def test_create_snapshot(self):
        """Test KPI snapshot creation"""
        snapshot = KPISnapshot.objects.create(
            mrr_current=Decimal('150000.00'),
            mrr_last_month=Decimal('140000.00'),
            active_customers=450,
            churn_rate_30d=2.5,
            cash_position=Decimal('500000.00'),
            computed_in_ms=1500
        )
        
        self.assertEqual(snapshot.mrr_current, Decimal('150000.00'))
        self.assertEqual(snapshot.active_customers, 450)
        self.assertIsNotNone(snapshot.timestamp)


class BoardReportModelTest(TestCase):
    """Test BoardReport model"""
    
    def test_create_board_report(self):
        """Test board report creation"""
        report = BoardReport.objects.create(
            report_year=2025,
            report_month=timezone.now().date().replace(day=1),
            financial_performance={'revenue': {'current': 1500000}},
            customer_metrics={'active_customers': 450},
            operational_metrics={'success_rate_pct': 98.5},
            generation_time_seconds=5
        )
        
        self.assertEqual(report.report_year, 2025)
        self.assertEqual(report.status, 'draft')
        self.assertIsNotNone(report.report_period_display)
    
    def test_get_latest_report(self):
        """Test getting latest report"""
        BoardReport.objects.create(
            report_year=2024,
            report_month=timezone.now().date().replace(day=1) - timedelta(days=60),
            financial_performance={},
            customer_metrics={},
            operational_metrics={}
        )
        
        latest = BoardReport.objects.create(
            report_year=2025,
            report_month=timezone.now().date().replace(day=1),
            financial_performance={},
            customer_metrics={},
            operational_metrics={}
        )
        
        self.assertEqual(BoardReport.get_latest(), latest)
