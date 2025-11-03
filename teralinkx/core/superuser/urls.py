from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import from your views folder
from .views.clientsview import ClientViewSet
from .views.transactionsview import TransactionViewSet
from .views.refundsview import RefundViewSet
from .views.dashboard_metrics import DashboardMetricsView, RevenueAnalyticsView, ClientGrowthView

from .views.auth import (
    AdminLoginView, 
    AdminLogoutView, 
    CheckAuthView, 
    TokenRefreshView,
    VerifyTokenView,
    TokenObtainPairView
)
from .views.systemstatusview import SystemStatusView

# Initialize router
router = DefaultRouter()

# Register ViewSets (they get automatic URL generation)
router.register(r'clients', ClientViewSet, basename='clients')
router.register(r'transactions', TransactionViewSet, basename='transactions')
# router.register(r'refunds', RefundViewSet, basename='refunds')
# Add DowntimeRecord ViewSet if you create one, or use the existing refund endpoints

urlpatterns = [
    # Router-generated URLs (automatic CRUD for ViewSets)
    path('', include(router.urls)),
    
    # Manual URLs for APIView classes (non-ViewSet views)
    path('auth/check/', CheckAuthView.as_view(), name='check-auth'),
    path('auth/login/', AdminLoginView.as_view(), name='admin-login'),
    path('auth/logout/', AdminLogoutView.as_view(), name='admin-logout'),
    path('auth/verify/', VerifyTokenView.as_view(), name='verify-token'),
    path('auth/check/', CheckAuthView.as_view(), name='check-auth'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Simple JWT standard endpoints (optional)
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('dashboard-metrics/', DashboardMetricsView.as_view(), name='dashboard-metrics'),
    path('dashboard-metrics/revenue-analytics/', RevenueAnalyticsView.as_view(), name='revenue-analytics'),
    path('dashboard-metrics/client-growth/', ClientGrowthView.as_view(), name='client-growth'),
    path('system-status/', SystemStatusView.as_view(), name='system-status'),
    
    # Refund-specific endpoints (from RefundViewSet custom actions)
    path('refunds/stats/', RefundViewSet.as_view({'get': 'stats'}), name='refund-stats'),
    path('refunds/eligible-clients/', RefundViewSet.as_view({'get': 'eligible_clients'}), name='eligible-clients'),
    path('refunds/client-details/<str:account>/', RefundViewSet.as_view({'get': 'client_details'}), name='client-details'),
    path('refunds/process-individual/', RefundViewSet.as_view({'post': 'process_individual'}), name='process-individual-refund'),
    path('refunds/batch-refund/', RefundViewSet.as_view({'post': 'batch_refund'}), name='batch-refund'),
    path('refunds/history/', RefundViewSet.as_view({'get': 'history'}), name='refund-history'),
    path('refunds/recent-downtimes/', RefundViewSet.as_view({'get': 'recent_downtimes'}), name='recent-downtimes'),
    path('refunds/record-downtime/', RefundViewSet.as_view({'post': 'record_downtime'}), name='record-downtime'),
    
    # Additional downtime management endpoints
    path('refunds/downtime-stats/', RefundViewSet.as_view({'get': 'downtime_stats'}), name='downtime-stats'),
    path('refunds/ongoing-downtimes/', RefundViewSet.as_view({'get': 'ongoing_downtimes'}), name='ongoing-downtimes'),
    path('refunds/critical-downtimes/', RefundViewSet.as_view({'get': 'critical_downtimes'}), name='critical-downtimes'),
]