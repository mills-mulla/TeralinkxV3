# apps/finance/views_vendor.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .vendor_intelligence_service import VendorIntelligenceService
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class VendorDashboardView(APIView):
    """Get complete vendor intelligence dashboard"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Check cache first
        cached_data = cache.get('vendor_dashboard')
        if cached_data:
            cached_data['from_cache'] = True
            return Response(cached_data)
        
        # Generate fresh data
        dashboard = VendorIntelligenceService.get_dashboard_summary()
        
        # Cache for 1 hour
        cache.set('vendor_dashboard', dashboard, 3600)
        dashboard['from_cache'] = False
        
        return Response(dashboard)


class VendorPerformanceView(APIView):
    """Get vendor performance metrics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        performance = VendorIntelligenceService.get_vendor_performance()
        return Response({
            'vendors': performance,
            'count': len(performance)
        })


class BandwidthCostAnalysisView(APIView):
    """Get bandwidth cost analysis by provider"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        analysis = VendorIntelligenceService.get_bandwidth_cost_analysis()
        return Response({
            'providers': analysis,
            'count': len(analysis)
        })


class ContractExpiryCalendarView(APIView):
    """Get upcoming contract renewals"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        calendar = VendorIntelligenceService.get_contract_expiry_calendar()
        return Response(calendar)


class InvoiceDiscrepancyAlertsView(APIView):
    """Get invoice discrepancy alerts"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        alerts = VendorIntelligenceService.get_invoice_discrepancy_alerts()
        return Response({
            'alerts': alerts,
            'count': len(alerts)
        })


class VendorRecommendationsView(APIView):
    """Get vendor management recommendations"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        recommendations = VendorIntelligenceService.get_vendor_recommendations()
        return Response({
            'recommendations': recommendations,
            'count': len(recommendations)
        })
