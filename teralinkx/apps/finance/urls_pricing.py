# apps/finance/urls_pricing.py
from django.urls import path
from .views_pricing import (
    PricingDashboardView,
    PackagePerformanceView,
    PriceElasticityView,
    UpgradeDowngradeAnalysisView,
    PricingRecommendationsView,
    CompetitivePositioningView
)

urlpatterns = [
    path('dashboard/', PricingDashboardView.as_view(), name='pricing-dashboard'),
    path('package-performance/', PackagePerformanceView.as_view(), name='package-performance'),
    path('price-elasticity/', PriceElasticityView.as_view(), name='price-elasticity'),
    path('upgrade-downgrade/', UpgradeDowngradeAnalysisView.as_view(), name='upgrade-downgrade-analysis'),
    path('recommendations/', PricingRecommendationsView.as_view(), name='pricing-recommendations'),
    path('competitive-positioning/', CompetitivePositioningView.as_view(), name='competitive-positioning'),
]
