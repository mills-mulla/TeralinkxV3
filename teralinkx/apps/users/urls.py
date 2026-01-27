# urls.py
from django.urls import path
from .client import (
    ClientView, 
    TokenRefreshView, 
    LogoutView, 
    TokenVerifyView,
    SessionValidationView
)
from .get_client import GetClientView
urlpatterns = [
    # Client authentication
    path('client/', ClientView.as_view(), name='client_auth'),
    # JWT endpoints
    path('getclient/', GetClientView.as_view(), name='get_client'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('session/validate/', SessionValidationView.as_view(), name='session_validate'),
]