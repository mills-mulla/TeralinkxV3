# apps/finance/tests/api/test_endpoints.py
"""
API Endpoint Tests
Tests REST API endpoints for finance app.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.utils import timezone

from finance.models import Currency, PaymentGateway, Department
from finance.models_board_report import BoardReport
from finance.models_kpi import KPISnapshot

User = get_user_model()


class BaseAPITestCase(TestCase):
    """Base test case with authentication setup"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create base currency
        self.currency = Currency.objects.create(
            code='KES',
            name='Kenyan Shilling',
            is_base_currency=True
        )


class KPIEndpointTest(BaseAPITestCase):
    """Test KPI API endpoints"""
    
    def test_kpi_summary_endpoint(self):
        """Test GET /api/finance/kpi/summary/"""
        # Create a KPI snapshot
        KPISnapshot.objects.create(
            mrr_current=Decimal('150000.00'),
            mrr_last_month=Decimal('140000.00'),
            active_customers=450,
            churn_rate_30d=2.5,
            cash_position=Decimal('500000.00'),
            computed_in_ms=1500
        )
        
        url = '/api/finance/kpi/summary/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('mrr', response.data)
        self.assertIn('customers', response.data)
        self.assertIn('cash', response.data)
    
    def test_kpi_summary_requires_auth(self):
        """Test KPI endpoint requires authentication"""
        self.client.force_authenticate(user=None)
        
        url = '/api/finance/kpi/summary/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BoardReportEndpointTest(BaseAPITestCase):
    """Test Board Report API endpoints"""
    
    def test_generate_board_report(self):
        """Test POST /api/finance/board-reports/generate/"""
        url = '/api/finance/board-report/generate/'
        data = {
            'year': 2025,
            'month': 1
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('report_id', response.data)
        self.assertIn('report_period', response.data)
    
    def test_get_latest_board_report(self):
        """Test GET /api/finance/board-reports/latest/"""
        # Create a report
        BoardReport.objects.create(
            report_year=2025,
            report_month=timezone.now().date().replace(day=1),
            financial_performance={'revenue': {'current': 1500000}},
            customer_metrics={'active_customers': 450},
            operational_metrics={'success_rate_pct': 98.5}
        )
        
        url = '/api/finance/board-report/latest/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('financial_performance', response.data)
        self.assertIn('customer_metrics', response.data)
    
    def test_export_board_report_pdf(self):
        """Test GET /api/finance/board-reports/{id}/export/pdf/"""
        report = BoardReport.objects.create(
            report_year=2025,
            report_month=timezone.now().date().replace(day=1),
            financial_performance={'revenue': {'current': 1500000}},
            customer_metrics={'active_customers': 450},
            operational_metrics={'success_rate_pct': 98.5}
        )
        
        url = f'/api/finance/board-report/{report.id}/export/pdf/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')


class PricingEndpointTest(BaseAPITestCase):
    """Test Pricing Intelligence API endpoints"""
    
    def test_pricing_dashboard(self):
        """Test GET /api/finance/pricing/dashboard/"""
        url = '/api/finance/pricing/dashboard/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('summary', response.data)
        self.assertIn('package_performance', response.data)
        self.assertIn('recommendations', response.data)
    
    def test_package_performance(self):
        """Test GET /api/finance/pricing/package-performance/"""
        url = '/api/finance/pricing/package-performance/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('packages', response.data)
        self.assertIn('count', response.data)
    
    def test_pricing_recommendations(self):
        """Test GET /api/finance/pricing/recommendations/"""
        url = '/api/finance/pricing/recommendations/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('recommendations', response.data)


class VendorEndpointTest(BaseAPITestCase):
    """Test Vendor Intelligence API endpoints"""
    
    def test_vendor_dashboard(self):
        """Test GET /api/finance/vendors/dashboard/"""
        url = '/api/finance/vendors/dashboard/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('summary', response.data)
        self.assertIn('vendor_performance', response.data)
        self.assertIn('alerts', response.data)
    
    def test_vendor_performance(self):
        """Test GET /api/finance/vendors/performance/"""
        url = '/api/finance/vendors/performance/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('vendors', response.data)
    
    def test_invoice_alerts(self):
        """Test GET /api/finance/vendors/invoice-alerts/"""
        url = '/api/finance/vendors/invoice-alerts/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('alerts', response.data)


class BudgetEndpointTest(BaseAPITestCase):
    """Test Budget Intelligence API endpoints"""
    
    def setUp(self):
        super().setUp()
        self.department = Department.objects.create(
            name='Marketing',
            code='MKT',
            budget=Decimal('50000.00')
        )
    
    def test_budget_dashboard(self):
        """Test GET /api/finance/budget/dashboard/"""
        url = '/api/finance/api/budget/dashboard/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('departments', response.data)
    
    def test_budget_utilization(self):
        """Test GET /api/finance/budget/utilization/"""
        url = f'/api/finance/api/budget/utilization/?department={self.department.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('department', response.data)
        self.assertIn('utilization_pct', response.data)


class ChurnEndpointTest(BaseAPITestCase):
    """Test Churn Prediction API endpoints"""
    
    def test_churn_predictions_list(self):
        """Test GET /api/finance/churn/predictions/"""
        url = '/api/finance/api/churn/predictions/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('predictions', response.data)
    
    def test_revenue_at_risk(self):
        """Test GET /api/finance/revenue-at-risk/dashboard/"""
        url = '/api/finance/api/revenue-at-risk/dashboard/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_revenue_at_risk', response.data)
