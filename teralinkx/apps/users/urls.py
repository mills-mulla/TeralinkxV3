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
    path('account/setup-password/', SetupPasswordView.as_view(), name='setup_password'),
    path('auth/verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    
    # JWT endpoints (existing)
    path('getclient/', GetClientView.as_view(), name='get_client'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('session/validate/', SessionValidationView.as_view(), name='session_validate'),
]