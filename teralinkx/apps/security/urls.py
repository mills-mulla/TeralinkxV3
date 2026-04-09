# urls.py
from django.urls import path
from security.auth_views import (
    MeView,
    AuthOptionsView,
    RequestOTPView,
    VerifyOTPView,
    PasswordLoginView,
    CompleteSignupView,
    LogoutView
)

urlpatterns = [
    # User profile (existing)
    path('auth/me/', MeView.as_view(), name='me'),
    
    # New authentication endpoints
    path('auth/options/', AuthOptionsView.as_view(), name='auth_options'),
    path('auth/request-otp/', RequestOTPView.as_view(), name='request_otp'),
    path('auth/verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('auth/password-login/', PasswordLoginView.as_view(), name='password_login'),
    path('auth/complete-signup/', CompleteSignupView.as_view(), name='complete_signup'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
]