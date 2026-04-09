"""
URL configuration for teralinkx project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path , include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('django_prometheus.urls')),
    path('service/', admin.site.urls),
    path('api/',include('users.urls')),
    path('api/',include('packages.urls')),
    path('api/',include('finance.urls')),
    path('api/',include('core.urls')),
    path('api/',include('security.urls')),
    path('api/ads/',include('ads.urls')),
    path('api/notifications/',include('notifications.urls')),
    path('suapi/', include('analytics.superuser.urls')),
    path('locations/', include('locations.urls')),  # Add locations URLs
    path('__debug__/', include('debug_toolbar.urls')), 
]
urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]

# Optional includes for when packages are available
try:
    from django_prometheus import urls as prometheus_urls
    urlpatterns.insert(0, path('', include('django_prometheus.urls')))
except ImportError:
    pass

try:
    import debug_toolbar
    urlpatterns.append(path('__debug__/', include('debug_toolbar.urls')))
except ImportError:
    pass

try:
    import silk
    urlpatterns.append(path('silk/', include('silk.urls', namespace='silk')))
except ImportError:
    pass
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# Auth Resilience URLs
from django.urls import include
urlpatterns += [
    path('api/', include('core.urls_auth_resilience')),
]

# Auth Resilience URLs
from django.urls import include
urlpatterns += [
    path('api/', include('core.urls_auth_resilience')),
]
