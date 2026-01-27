# from django.urls import path
# from .daraja import PaymentAPIView, ProcessCallback, MpesaHelper
# from .authentications import Connect, Reconnect, Disconnect
# from .balance import *

# # Modularized views
# from .views.client import ClientView
# from .views.get_client import GetClientView
# from .views.packages import PackageAPIView
# from .views.daily_pass import DailyPassAPIView
# from .views.check_dpass import CheckDpassStatus
# from .views.announcement import AnnouncementView
# from .views.active_packages import ActivePackages
# from .views.voucher import VoucherAPIView
# from .views.dispatch_voucher import DispatchVoucherAPIView
# from .views.superuser import SuperuserAPIView
# from .views.upload_csv import UploadCSVView
# from .views.retrieve_voucher import RetrieveVoucher
# from .views.dhcp_lease import DHCPLeaseListCreateView
# from .views.usage import get_live_usage
# from .services.csrf import get_csrf_token
# from .views.get_client import GetClientView as getClientView  # Optional alias if reused
# from .views.authuser import MeView
# from .views.deauth import LogoutView
# from .views.chekout_confirmation import payment_status
# from .views.ads import ActiveAdsAPIView
# from .views.clientprofile import UpdateClientProfileView
# from .views.client_notifications import get_user_notifications

# urlpatterns = [
#     path('notifications/', get_user_notifications, name='get_user_notifications'),
#     path('update-profile/', UpdateClientProfileView.as_view(), name='update-profile'),
#     path('logout/', LogoutView.as_view(), name='logout'),
#     path("me/", MeView.as_view(), name="user-me"),
#     path('get-csrf-token/', get_csrf_token),
#     path('live-usage/', get_live_usage),
#     path('payment/', PaymentAPIView.as_view()),
#     path('checkoutstatus/',payment_status, name='payment-status'),
#     path('callback/', ProcessCallback.as_view()),
#     path('vouchers/', VoucherAPIView.as_view()),
#     path('dispach/', DispatchVoucherAPIView.as_view()),
#     path('sup/', SuperuserAPIView.as_view()),
#     path('uploadcsv/', UploadCSVView.as_view()),
#     path('retrvoucher/', RetrieveVoucher.as_view()),
#     path('packages/', PackageAPIView.as_view()),
#     path('dailypass/', DailyPassAPIView.as_view()),
#     path('dpass/', CheckDpassStatus.as_view()),
#     path('auth/', MpesaHelper.get_access_token, name='auth'),
#     path('connect/', Connect.as_view()),
#     path('reconnect/', Reconnect.as_view()),
#     path('disconnect/', Disconnect.as_view()),
#     path('leases/', DHCPLeaseListCreateView.as_view()),
#     path('clients/', ClientView.as_view()),
#     path('getclient/', getClientView.as_view()),
#     path('getactive/', ActivePackages.as_view()),
#     path('purchase/', PackagePurchaseService.as_view()),
#     path('renew/', VoucherRenewService.as_view()),
#     path('connection-details/', get_csrf_token),
#     path('announcements/', AnnouncementView.as_view()),
#     path('activeads/', ActiveAdsAPIView.as_view(), name='active-ads'),
# ]
from django.urls import path
from .views.network_views import NetworkInfoView
from .services.csrf import get_csrf_token

urlpatterns = [
    
    # Network information endpoint
    path('network-info/', NetworkInfoView.as_view(), name='network-info'),
    path('cross/', get_csrf_token),
    # Health check endpoint (for captive portal detection)
    path('network-health/', NetworkInfoView.as_view(), name='network-health'),
]