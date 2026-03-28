"""
URL configuration for locations app APIs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api_views import (
    LocationSyncAPIViewSet,
    DistributedTransactionAPIViewSet,
    HealthMonitoringAPIViewSet,
    health_check
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'sync', LocationSyncAPIViewSet, basename='location-sync')
router.register(r'transactions', DistributedTransactionAPIViewSet, basename='distributed-transactions')
router.register(r'health', HealthMonitoringAPIViewSet, basename='health-monitoring')

app_name = 'locations'

urlpatterns = [
    # Health check endpoint (no auth required)
    path('health/', health_check, name='health-check'),
    
    # API endpoints
    path('api/', include(router.urls)),
]