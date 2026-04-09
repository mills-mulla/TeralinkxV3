from django.urls import path
from .views import (
    RevenueStreamAPIView, ExpenseAPIView, InvestmentAPIView, DepartmentAPIView,
    FinancialMetricsAPIView, PackagePerformanceAPIView, 
    TransactionStatsAPIView, UnifiedTransactionsAPIView
)

urlpatterns = [
    path('revenue-streams/', RevenueStreamAPIView.as_view(), name='revenue-streams'),
    path('revenue-streams/<int:pk>/', RevenueStreamAPIView.as_view(), name='revenue-stream-detail'),
    path('expenses/', ExpenseAPIView.as_view(), name='expenses'),
    path('expenses/<int:pk>/', ExpenseAPIView.as_view(), name='expense-detail'),
    path('investments/', InvestmentAPIView.as_view(), name='investments'),
    path('investments/<int:pk>/', InvestmentAPIView.as_view(), name='investment-detail'),
    path('departments/', DepartmentAPIView.as_view(), name='departments'),
    path('departments/<int:pk>/', DepartmentAPIView.as_view(), name='department-detail'),
    
    # New Analytics Endpoints
    path('metrics/', FinancialMetricsAPIView.as_view(), name='financial-metrics'),
    path('package-performance/', PackagePerformanceAPIView.as_view(), name='package-performance'),
    path('transaction-stats/', TransactionStatsAPIView.as_view(), name='transaction-stats'),
    path('transactions/', UnifiedTransactionsAPIView.as_view(), name='unified-transactions'),
]
