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
from packages.rewards_views import get_reward_summary, get_available_rewards, redeem_reward, get_point_history, get_user_coupons

urlpatterns = [
    path('', include('django_prometheus.urls')),
    path('admin/', admin.site.urls),
    path('api/',include('users.urls')),
    path('api/',include('packages.urls')),
    path('api/',include('finance.urls')),
    path('api/',include('core.urls')),
    path('api/',include('security.urls')),
    path('api/ads/',include('ads.urls')),
    path('api/notifications/',include('notifications.urls')),
    # Direct rewards endpoints to match frontend expectations
    path('api/rewards/summary/', get_reward_summary, name='reward-summary'),
    path('api/rewards/available/', get_available_rewards, name='available-rewards'),
    path('api/rewards/redeem/', redeem_reward, name='redeem-reward'),
    path('api/rewards/coupons/', get_user_coupons, name='user-coupons'),
    path('api/rewards/history/', get_point_history, name='point-history'),
    path('suapi/', include('analytics.superuser.urls')),
    path('__debug__/', include('debug_toolbar.urls')), 
   
]
urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)