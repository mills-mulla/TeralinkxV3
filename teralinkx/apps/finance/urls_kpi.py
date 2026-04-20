# apps/finance/urls_kpi.py
from django.urls import path
from .views_kpi import KPISummaryView, WeeklySummaryView, RefreshKPIView, CashFlowForecastView, RevenueComparisonView

urlpatterns = [
    path('summary/', KPISummaryView.as_view(), name='kpi-summary'),
    path('weekly-summary/', WeeklySummaryView.as_view(), name='weekly-summary'),
    path('refresh/', RefreshKPIView.as_view(), name='kpi-refresh'),
    path('cash-flow/forecast/', CashFlowForecastView.as_view(), name='cashflow-forecast'),
    path('revenue-comparison/', RevenueComparisonView.as_view(), name='revenue-comparison'),
]
