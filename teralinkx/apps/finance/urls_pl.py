# apps/finance/urls_pl.py
from django.urls import path
from .views_pl import PLStatementView, PLHistoryView, ForexExposureView

urlpatterns = [
    path('pl/',         PLStatementView.as_view(), name='pl-statement'),
    path('pl/history/', PLHistoryView.as_view(),   name='pl-history'),
    path('pl/forex/',   ForexExposureView.as_view(), name='forex-exposure'),
]
