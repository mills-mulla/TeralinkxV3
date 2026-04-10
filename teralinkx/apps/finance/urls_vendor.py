# apps/finance/urls_vendor.py
from django.urls import path
from .views_vendor import (
    VendorDashboardView,
    VendorPerformanceView,
    BandwidthCostAnalysisView,
    ContractExpiryCalendarView,
    InvoiceDiscrepancyAlertsView,
    VendorRecommendationsView
)

urlpatterns = [
    path('dashboard/', VendorDashboardView.as_view(), name='vendor-dashboard'),
    path('performance/', VendorPerformanceView.as_view(), name='vendor-performance'),
    path('bandwidth-costs/', BandwidthCostAnalysisView.as_view(), name='bandwidth-cost-analysis'),
    path('contract-calendar/', ContractExpiryCalendarView.as_view(), name='contract-expiry-calendar'),
    path('invoice-alerts/', InvoiceDiscrepancyAlertsView.as_view(), name='invoice-discrepancy-alerts'),
    path('recommendations/', VendorRecommendationsView.as_view(), name='vendor-recommendations'),
]
