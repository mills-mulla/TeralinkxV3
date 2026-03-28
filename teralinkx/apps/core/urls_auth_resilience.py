# apps/core/urls_auth_resilience.py - Auth Resilience URL Configuration
from django.urls import path
from .auth_health import TokenHealthCheckView, BackendStatusView
from .enhanced_device_auth import EnhancedDeviceAutoAuthView

urlpatterns = [
    # Token health monitoring endpoints
    path('auth/health-check/', TokenHealthCheckView.as_view(), name='token_health_check'),
    path('status/', BackendStatusView.as_view(), name='backend_status'),
    
    # Enhanced device authentication
    path('auth/enhanced-device/', EnhancedDeviceAutoAuthView.as_view(), name='enhanced_device_auth'),
]