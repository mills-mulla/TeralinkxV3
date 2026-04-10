# apps/finance/tests/unit/test_services.py
"""
Unit Tests for Finance Services
Tests business logic in service layer.
"""
from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from unittest.mock import Mock, patch, MagicMock

from finance.models import Currency, PaymentGateway, Department, Expense
from finance.models_churn import ChurnPrediction, RetentionTask
from finance.models_kpi import KPISnapshot
from finance.kpi_service import KPIService
from finance.pricing_intelligence_service import PricingIntelligenceService
from finance.vendor_intelligence_service import VendorIntelligenceService
from finance.budget_service import BudgetService


class KPIServiceTest(TestCase):
    """Test KPI calculation service"""
    
    def setUp(self):
        self.currency = Currency.objects.create(
            code='KES',
            name='Kenyan Shilling',
            is_base_currency=True
        )
    
    def test_calculate_mrr(self):
        """Test MRR calculation"""
        mrr = KPIService.calculate_mrr()
        self.assertIsInstance(mrr, (int, float, Decimal))
        self.assertGreaterEqual(mrr, 0)
    
    def test_calculate_active_customers(self):
        """Test active customer count"""
        count = KPIService.calculate_active_customers()
        self.assertIsInstance(count, int)
        self.assertGreaterEqual(count, 0)
    
    def test_calculate_churn_rate(self):
        """Test churn rate calculation"""
        churn_rate = KPIService.calculate_churn_rate(days=30)
        self.assertIsInstance(churn_rate, float)
        self.assertGreaterEqual(churn_rate, 0)
        self.assertLessEqual(churn_rate, 100)
    
    def test_get_kpi_summary(self):
        """Test complete KPI summary generation"""
        summary = KPIService.get_kpi_summary()
        
        self.assertIn('mrr', summary)
        self.assertIn('active_customers', summary)
        self.assertIn('churn_rate', summary)
        self.assertIn('timestamp', summary)


class PricingIntelligenceServiceTest(TestCase):
    """Test pricing intelligence service"""
    
    def setUp(self):
        self.currency = Currency.objects.create(
            code='KES',
            name='Kenyan Shilling',
            is_base_currency=True
        )
    
    def test_get_package_performance(self):
        """Test package performance analysis"""
        performance = PricingIntelligenceService.get_package_performance()
        
        self.assertIsInstance(performance, list)
        for package in performance:
            self.assertIn('package_name', package)
            self.assertIn('customer_count', package)
            self.assertIn('total_revenue', package)
            self.assertIn('arpu', package)
            self.assertIn('churn_rate_pct', package)
    
    def test_get_pricing_recommendations(self):
        """Test pricing recommendations generation"""
        recommendations = PricingIntelligenceService.get_pricing_recommendations()
        
        self.assertIsInstance(recommendations, list)
        for rec in recommendations:
            self.assertIn('package', rec)
            self.assertIn('type', rec)
            self.assertIn('priority', rec)
            self.assertIn('recommendation', rec)
    
    def test_get_dashboard_summary(self):
        """Test pricing dashboard summary"""
        summary = PricingIntelligenceService.get_dashboard_summary()
        
        self.assertIn('summary', summary)
        self.assertIn('package_performance', summary)
        self.assertIn('recommendations', summary)
        self.assertIn('timestamp', summary)


class VendorIntelligenceServiceTest(TestCase):
    """Test vendor intelligence service"""
    
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
    
    def test_get_vendor_performance(self):
        """Test vendor performance analysis"""
        performance = VendorIntelligenceService.get_vendor_performance()
        
        self.assertIsInstance(performance, list)
        for vendor in performance:
            self.assertIn('vendor_name', vendor)
            self.assertIn('total_spend_12m', vendor)
            self.assertIn('invoice_count', vendor)
    
    def test_get_invoice_discrepancy_alerts(self):
        """Test invoice discrepancy detection"""
        alerts = VendorIntelligenceService.get_invoice_discrepancy_alerts()
        
        self.assertIsInstance(alerts, list)
        for alert in alerts:
            self.assertIn('vendor', alert)
            self.assertIn('alert_type', alert)
            self.assertIn('severity', alert)
    
    def test_get_vendor_recommendations(self):
        """Test vendor recommendations"""
        recommendations = VendorIntelligenceService.get_vendor_recommendations()
        
        self.assertIsInstance(recommendations, list)


class BudgetServiceTest(TestCase):
    """Test budget intelligence service"""
    
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
    
    def test_calculate_budget_utilization(self):
        """Test budget utilization calculation"""
        utilization = BudgetService.calculate_budget_utilization(
            self.department.id,
            timezone.now().year,
            timezone.now().month
        )
        
        self.assertIn('department', utilization)
        self.assertIn('budget', utilization)
        self.assertIn('spent', utilization)
        self.assertIn('utilization_pct', utilization)
        self.assertIn('remaining', utilization)
    
    def test_get_budget_alerts(self):
        """Test budget alert generation"""
        alerts = BudgetService.get_budget_alerts()
        
        self.assertIsInstance(alerts, list)
        for alert in alerts:
            self.assertIn('department', alert)
            self.assertIn('alert_type', alert)
            self.assertIn('severity', alert)
