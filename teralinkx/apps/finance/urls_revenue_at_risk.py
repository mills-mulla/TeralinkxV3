"""
Revenue at Risk URL Configuration
Add these to your main finance urls.py
"""
from django.urls import path
from finance.views_revenue_at_risk import (
    revenue_at_risk_summary,
    top_at_risk_accounts,
    retention_effectiveness,
    relocated_customers,
    automated_offers_stats,
)

# Revenue at Risk Dashboard URLs
urlpatterns = [
    path('', revenue_at_risk_summary, name='revenue-at-risk-summary'),
    path('top-accounts/', top_at_risk_accounts, name='top-at-risk-accounts'),
    path('effectiveness/', retention_effectiveness, name='retention-effectiveness'),
    path('relocated/', relocated_customers, name='relocated-customers'),
    path('offers/', automated_offers_stats, name='automated-offers-stats'),
]
