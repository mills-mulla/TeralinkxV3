# apps/finance/urls_budget.py
from django.urls import path
from .views_budget import (
    BudgetUtilizationView,
    BudgetVarianceView,
    BudgetTrendsView,
    BudgetAlertsView,
    DepartmentComparisonView,
    BudgetDashboardView
)

urlpatterns = [
    path('utilization/', BudgetUtilizationView.as_view(), name='budget-utilization'),
    path('variance/', BudgetVarianceView.as_view(), name='budget-variance'),
    path('trends/', BudgetTrendsView.as_view(), name='budget-trends'),
    path('alerts/', BudgetAlertsView.as_view(), name='budget-alerts'),
    path('comparison/', DepartmentComparisonView.as_view(), name='department-comparison'),
    path('dashboard/', BudgetDashboardView.as_view(), name='budget-dashboard'),
]
