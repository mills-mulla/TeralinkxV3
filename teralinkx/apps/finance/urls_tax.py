# apps/finance/urls_tax.py
from django.urls import path
from .views_tax import (
    TaxCalendarView, TaxReturnListView, TaxReturnDetailView,
    TaxUpcomingView, WHTCalculateView
)
from .views_reminder import ReminderListView, ReminderStatsView

urlpatterns = [
    path('tax/calendar/',              TaxCalendarView.as_view(),    name='tax-calendar'),
    path('tax/',                       TaxReturnListView.as_view(),  name='tax-list'),
    path('tax/upcoming/',              TaxUpcomingView.as_view(),    name='tax-upcoming'),
    path('tax/wht/calculate/',         WHTCalculateView.as_view(),   name='wht-calculate'),
    path('tax/<int:return_id>/',       TaxReturnDetailView.as_view(), name='tax-detail'),
    path('reminders/',                 ReminderListView.as_view(),   name='reminder-list'),
    path('reminders/stats/',           ReminderStatsView.as_view(),  name='reminder-stats'),
]
