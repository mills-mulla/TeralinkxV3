from django.urls import path
from .views import UserAPIView, ProfileAPIView, SessionAPIView, DisconnectAPIView, VoucherUsageAPIView, VoucherUsageBatchAPIView

urlpatterns = [
    path('users/', UserAPIView.as_view(), name='users'),
    path('profiles/', ProfileAPIView.as_view(), name='profiles'),
    path('sessions/', SessionAPIView.as_view(), name='sessions'),
    path('vouchers/usage/', VoucherUsageAPIView.as_view(), name='voucher-usage'),
    path('vouchers/usage/batch/', VoucherUsageBatchAPIView.as_view(), name='voucher-usage-batch'),
    path('disconnect/', DisconnectAPIView.as_view(), name='disconnect'),
]
