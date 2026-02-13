from django.urls import path
from .views import RevenueStreamAPIView, ExpenseAPIView, InvestmentAPIView, DepartmentAPIView

urlpatterns = [
    path('revenue-streams/', RevenueStreamAPIView.as_view(), name='revenue-streams'),
    path('expenses/', ExpenseAPIView.as_view(), name='expenses'),
    path('investments/', InvestmentAPIView.as_view(), name='investments'),
    path('departments/', DepartmentAPIView.as_view(), name='departments'),
]
