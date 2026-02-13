# apps/ads/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('activeads/', views.ActiveAdsView.as_view(), name='active-ads'),
    path('track/', views.track_ad_interaction, name='track-ad-interaction'),
    path('manage/', views.AdvertisementManagementView.as_view(), name='ads-manage'),
    path('manage/<int:pk>/', views.AdvertisementDetailView.as_view(), name='ads-detail'),
]