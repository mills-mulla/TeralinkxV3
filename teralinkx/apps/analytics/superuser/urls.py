from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.clientsview import ClientViewSet
from .views.transactionsview import TransactionViewSet
from .views.dashboard_metrics import (
    DashboardMetricsView, RevenueAnalyticsView, ClientGrowthView,
    PackageSalesView, LocationPerformanceView, PaymentMethodsView,
    RecentActivityView, VoucherStatusView, HourlyUsageView,
    ConversionFunnelView, DeviceBreakdownView, RewardTierDistributionView,
    SessionMetricsView, RefundMetricsView, CohortAnalysisView,
    RFMSegmentationView, FinancialAnalyticsView, FunnelAnalysisView,
    ChurnPredictionView, RevenueForecastView, NetworkAnalyticsView,
    ABTestingView, CustomerHealthView, AuditLogView, DataQualityView
)

from .views.auth import (
    AdminLoginView, 
    AdminLogoutView, 
    CheckAuthView, 
    TokenRefreshView,
    VerifyTokenView,
    TokenObtainPairView
)
from .views.systemstatusview import SystemStatusView

from .views.user_views import DjangoUserViewSet, UserDeviceViewSet, UserSessionViewSet
from .views.package_views import (
    PackageTypeViewSet,
    DispatchVoucherViewSet,
    CouponViewSet,
    FeaturedPromotionViewSet,
    PointTransactionViewSet
)
from .views.location_views import LocationViewSet

router = DefaultRouter()

router.register(r'clients', ClientViewSet, basename='clients')
router.register(r'transactions', TransactionViewSet, basename='transactions')

router.register(r'users', DjangoUserViewSet, basename='users')
router.register(r'devices', UserDeviceViewSet, basename='devices')
router.register(r'sessions', UserSessionViewSet, basename='sessions')
router.register(r'packages', PackageTypeViewSet, basename='packages')
router.register(r'vouchers', DispatchVoucherViewSet, basename='vouchers')
router.register(r'coupons', CouponViewSet, basename='coupons')
router.register(r'promotions', FeaturedPromotionViewSet, basename='promotions')
router.register(r'point-transactions', PointTransactionViewSet, basename='point-transactions')
router.register(r'locations', LocationViewSet, basename='locations')

urlpatterns = [
    path('', include(router.urls)),
    
    path('auth/check/', CheckAuthView.as_view(), name='check-auth'),
    path('auth/login/', AdminLoginView.as_view(), name='admin-login'),
    path('auth/logout/', AdminLogoutView.as_view(), name='admin-logout'),
    path('auth/verify/', VerifyTokenView.as_view(), name='verify-token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    path('dashboard-metrics/', DashboardMetricsView.as_view(), name='dashboard-metrics'),
    path('dashboard-metrics/revenue-analytics/', RevenueAnalyticsView.as_view(), name='revenue-analytics'),
    path('dashboard-metrics/client-growth/', ClientGrowthView.as_view(), name='client-growth'),
    path('dashboard-metrics/package-sales/', PackageSalesView.as_view(), name='package-sales'),
    path('dashboard-metrics/location-performance/', LocationPerformanceView.as_view(), name='location-performance'),
    path('dashboard-metrics/payment-methods/', PaymentMethodsView.as_view(), name='payment-methods'),
    path('dashboard-metrics/recent-activity/', RecentActivityView.as_view(), name='recent-activity'),
    path('dashboard-metrics/voucher-status/', VoucherStatusView.as_view(), name='voucher-status'),
    path('dashboard-metrics/hourly-usage/', HourlyUsageView.as_view(), name='hourly-usage'),
    path('dashboard-metrics/conversion-funnel/', ConversionFunnelView.as_view(), name='conversion-funnel'),
    path('dashboard-metrics/device-breakdown/', DeviceBreakdownView.as_view(), name='device-breakdown'),
    path('dashboard-metrics/reward-tiers/', RewardTierDistributionView.as_view(), name='reward-tiers'),
    path('dashboard-metrics/session-metrics/', SessionMetricsView.as_view(), name='session-metrics'),
    path('dashboard-metrics/refund-metrics/', RefundMetricsView.as_view(), name='refund-metrics'),
    path('dashboard-metrics/cohort-analysis/', CohortAnalysisView.as_view(), name='cohort-analysis'),
    path('dashboard-metrics/rfm-segmentation/', RFMSegmentationView.as_view(), name='rfm-segmentation'),
    path('dashboard-metrics/financial-analytics/', FinancialAnalyticsView.as_view(), name='financial-analytics'),
    path('dashboard-metrics/funnel-analysis/', FunnelAnalysisView.as_view(), name='funnel-analysis'),
    path('dashboard-metrics/churn-prediction/', ChurnPredictionView.as_view(), name='churn-prediction'),
    path('dashboard-metrics/revenue-forecast/', RevenueForecastView.as_view(), name='revenue-forecast'),
    path('dashboard-metrics/network-analytics/', NetworkAnalyticsView.as_view(), name='network-analytics'),
    path('dashboard-metrics/ab-testing/', ABTestingView.as_view(), name='ab-testing'),
    path('dashboard-metrics/customer-health/', CustomerHealthView.as_view(), name='customer-health'),
    path('dashboard-metrics/audit-logs/', AuditLogView.as_view(), name='audit-logs'),
    path('dashboard-metrics/data-quality/', DataQualityView.as_view(), name='data-quality'),
    path('system-status/', SystemStatusView.as_view(), name='system-status'),
]