# apps/finance/views_pricing.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .pricing_intelligence_service import PricingIntelligenceService
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class PricingDashboardView(APIView):
    """Get complete pricing intelligence dashboard"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Check cache first
        cached_data = cache.get('pricing_dashboard')
        if cached_data:
            cached_data['from_cache'] = True
            return Response(cached_data)
        
        # Generate fresh data
        dashboard = PricingIntelligenceService.get_dashboard_summary()
        
        # Cache for 1 hour
        cache.set('pricing_dashboard', dashboard, 3600)
        dashboard['from_cache'] = False
        
        return Response(dashboard)


class PackagePerformanceView(APIView):
    """Get package performance metrics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        performance = PricingIntelligenceService.get_package_performance()
        return Response({
            'packages': performance,
            'count': len(performance)
        })


class PriceElasticityView(APIView):
    """Analyze price elasticity for a package"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        package_name = request.query_params.get('package')
        months = int(request.query_params.get('months', 6))
        
        if not package_name:
            return Response(
                {'error': 'package parameter required'},
                status=400
            )
        
        analysis = PricingIntelligenceService.analyze_price_elasticity(
            package_name, months
        )
        
        return Response(analysis)


class UpgradeDowngradeAnalysisView(APIView):
    """Get upgrade/downgrade pattern analysis"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        analysis = PricingIntelligenceService.get_upgrade_downgrade_analysis()
        return Response(analysis)


class PricingRecommendationsView(APIView):
    """Get data-driven pricing recommendations"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        recommendations = PricingIntelligenceService.get_pricing_recommendations()
        return Response({
            'recommendations': recommendations,
            'count': len(recommendations)
        })


class CompetitivePositioningView(APIView):
    """Get competitive positioning data"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        positioning = PricingIntelligenceService.get_competitive_positioning()
        return Response(positioning)
