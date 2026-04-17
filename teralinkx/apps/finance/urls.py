# apps/finance/urls.py
from django.urls import path, include
from finance.payment_gateway import (
    PaymentInitiateAPIView,
    PaymentCallbackAPIView,
    ReconciliationAPIView,
    C2BValidationAPIView,
    C2BRegisterURLAPIView,
)
from .querycheckout import payment_status, payment_health_check
from .credit_balance import BalancePurchaseAPIView, balance_health_check
from .unified_payment import UnifiedPaymentAPIView
from .authentications import ConnectAPIView,ReconnectAPIView,DisconnectAPIView
from .views_health import HealthCheckView, ReadinessCheckView, LivenessCheckView, MetricsView


urlpatterns = [
    # Health check endpoints
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('ready/', ReadinessCheckView.as_view(), name='readiness-check'),
    path('alive/', LivenessCheckView.as_view(), name='liveness-check'),
    path('metrics/', MetricsView.as_view(), name='metrics'),
    
    # API endpoints for admin dashboard
    path('finance/api/', include('finance.api.urls')),
    
    # Churn prediction endpoints
    path('finance/api/', include('finance.urls_churn')),
    
    # Revenue at risk endpoints
    path('finance/api/revenue-at-risk/', include('finance.urls_revenue_at_risk')),
    
    # Reconciliation endpoints
    path('finance/api/', include('finance.urls_reconciliation')),
    
    # Budget intelligence endpoints
    path('finance/api/budget/', include('finance.urls_budget')),
    
    # KPI endpoints
    path('finance/api/kpi/', include('finance.urls_kpi')),
    
    # Invoice endpoints
    path('finance/api/', include('finance.urls_invoice')),
    
    # Board report endpoints
    path('finance/api/board-report/', include('finance.urls_board_report')),
    
    # Pricing intelligence endpoints (Phase 4.3)
    path('finance/api/pricing/', include('finance.urls_pricing')),
    
    # Vendor intelligence endpoints (Phase 4.4)
    path('finance/api/vendors/', include('finance.urls_vendor')),
    
    # Payment endpoints
    path('payments/unified/', UnifiedPaymentAPIView.as_view(), name='unified_payment'),
    path('payments/initiate/', PaymentInitiateAPIView.as_view(), name='initiate-payment'),
    path('payments/callback/', PaymentCallbackAPIView.as_view(), name='payment-callback'),
    path('payments/c2b/validate/', C2BValidationAPIView.as_view(), name='c2b-validation'),
    path('payments/c2b/register/', C2BRegisterURLAPIView.as_view(), name='c2b-register'),
    path('payment-status/<str:checkout_request_id>/', payment_status, name='payment_status'),
    path('payment-health/', payment_health_check, name='payment_health'),
    path('balance-purchase/', BalancePurchaseAPIView.as_view(), name='balance_purchase_v3'),
    path('balance-health/', balance_health_check, name='balance_health'),

    # Reconciliation endpoints
    path('payments/reconcile/', ReconciliationAPIView.as_view(), name='reconcile_payments'),
    path('payments/pull-register/', ReconciliationAPIView.as_view(), {'action': 'register'}, name='pull_register'),

    #hotspot authentication
    path('connect/', ConnectAPIView.as_view(), name='connect'),
    path('reconnect/', ReconnectAPIView.as_view(), name='reconnect'),
    path('disconnect/', DisconnectAPIView.as_view(), name='disconnect'),
    
]