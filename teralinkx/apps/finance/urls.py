# apps/finance/urls.py
from django.urls import path, include
from finance.payment_gateway import (
    PaymentInitiateAPIView,
    PaymentCallbackAPIView
)
from .querycheckout import payment_status, payment_health_check
from .credit_balance import BalancePurchaseAPIView, balance_health_check
from .unified_payment import UnifiedPaymentAPIView
from .authentications import ConnectAPIView,ReconnectAPIView,DisconnectAPIView


urlpatterns = [
    # API endpoints for admin dashboard
    path('finance/api/', include('finance.api.urls')),
    
    # Payment endpoints
    path('payments/unified/', UnifiedPaymentAPIView.as_view(), name='unified_payment'),
    path('payments/initiate/', PaymentInitiateAPIView.as_view(), name='initiate-payment'),
    path('payments/callback/', PaymentCallbackAPIView.as_view(), name='payment-callback'),
    path('payment-status/<str:checkout_request_id>/', payment_status, name='payment_status'),
    path('payment-health/', payment_health_check, name='payment_health'),
    path('balance-purchase/', BalancePurchaseAPIView.as_view(), name='balance_purchase_v3'),
    path('balance-health/', balance_health_check, name='balance_health'),

    #hotspot authentication
    path('connect/', ConnectAPIView.as_view(), name='connect'),
    path('reconnect/', ReconnectAPIView.as_view(), name='reconnect'),
    path('disconnect/', DisconnectAPIView.as_view(), name='disconnect'),
    
]