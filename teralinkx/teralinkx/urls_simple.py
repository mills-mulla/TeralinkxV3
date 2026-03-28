"""
Simplified URL configuration for checking multi-location status
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/', include('packages.urls')),
    path('api/', include('finance.urls')),
    path('api/', include('core.urls')),
    path('api/', include('security.urls')),
    path('api/ads/', include('ads.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('suapi/', include('analytics.superuser.urls')),
    path('locations/', include('locations.urls')),  # Multi-location URLs
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)