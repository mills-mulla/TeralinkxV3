# apps/finance/urls.py
from django.urls import path
from finance.payment_gateway import (
    PaymentInitiateAPIView,
    PaymentCallbackAPIView
)
from .querycheckout import payment_status, payment_health_check

urlpatterns = [
    path('payments/initiate/', PaymentInitiateAPIView.as_view(), name='initiate-payment'),
    path('payments/callback/', PaymentCallbackAPIView.as_view(), name='payment-callback'),
    path('payment-status/', payment_status, name='payment_status'),
    path('payment-health/', payment_health_check, name='payment_health'),
]