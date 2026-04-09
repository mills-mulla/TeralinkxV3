"""
Minimal URL configuration for checking multi-location status
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('locations/', include('locations.urls')),  # Multi-location URLs
]