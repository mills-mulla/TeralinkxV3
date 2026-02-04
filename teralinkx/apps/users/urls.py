# apps/users/urls.py
from django.urls import path
from .client import (
    ClientView, 
    TokenRefreshView, 
    LogoutView, 
    TokenVerifyView,
    SessionValidationView
)
from .get_client import GetClientView
from .dashboard import DashboardAPIView
from .profile_api import ProfileUpdateAPIView, ProfileDataAPIView
from .device_api import (
    DeviceListAPIView,
    DeviceUpdateAPIView, 
    DeviceBlockAPIView,
    DeviceUnblockAPIView,
    DeviceTrustAPIView,
    DeviceRemoveAPIView
)
from .device_auto_auth import DeviceAutoAuthAPIView, DeviceTrustAPIView as DeviceAutoTrustAPIView
from .image_api import ProfileImageUploadAPIView
from .passwordless_views import (
    AccountCheckView,
    PasswordlessAuthView,
    SetupPasswordView,
    VerifyOTPView
)

urlpatterns = [
    # Client authentication (existing)
    path('client/', ClientView.as_view(), name='client_auth'),
    
    # Passwordless authentication endpoints (NEW)
    path('account/check/', AccountCheckView.as_view(), name='account_check'),
    path('auth/passwordless/', PasswordlessAuthView.as_view(), name='passwordless_auth'),
    path('auth/device-auto/', DeviceAutoAuthAPIView.as_view(), name='device_auto_auth'),
    path('auth/device-trust/', DeviceAutoTrustAPIView.as_view(), name='device_auto_trust'),
    path('account/setup-password/', SetupPasswordView.as_view(), name='setup_password'),
    path('auth/verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    
    # Profile management endpoints (NEW)
    path('profile/update/', ProfileUpdateAPIView.as_view(), name='profile_update'),
    path('profile/data/', ProfileDataAPIView.as_view(), name='profile_data'),
    path('profile/image/', ProfileImageUploadAPIView.as_view(), name='profile_image'),
    
    # Device management endpoints (NEW)
    path('devices/', DeviceListAPIView.as_view(), name='device_list'),
    path('devices/<int:device_id>/update/', DeviceUpdateAPIView.as_view(), name='device_update'),
    path('devices/<int:device_id>/block/', DeviceBlockAPIView.as_view(), name='device_block'),
    path('devices/<int:device_id>/unblock/', DeviceUnblockAPIView.as_view(), name='device_unblock'),
    path('devices/<int:device_id>/trust/', DeviceTrustAPIView.as_view(), name='device_trust'),
    path('devices/<int:device_id>/remove/', DeviceRemoveAPIView.as_view(), name='device_remove'),
    
    # JWT endpoints (existing)
    path('getclient/', GetClientView.as_view(), name='get_client'),
    path('dashboard/', DashboardAPIView.as_view(), name='dashboard'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('session/validate/', SessionValidationView.as_view(), name='session_validate'),
]