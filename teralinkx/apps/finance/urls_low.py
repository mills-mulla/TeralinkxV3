# apps/finance/urls_low.py
from django.urls import path
from .views_low import (
    PaymentAllocationView,
    SLAPolicyView, OutageEventView,
    RepaymentScheduleView,
    BranchView,
    InsurancePolicyView,
    DividendView,
    CLVCohortView,
)

urlpatterns = [
    # 6.18 Payment Allocation
    path('payment-allocation/',         PaymentAllocationView.as_view(),  name='payment-allocation'),

    # 6.19 SLA Credits
    path('sla/policies/',               SLAPolicyView.as_view(),          name='sla-policies'),
    path('sla/outages/',                OutageEventView.as_view(),        name='outage-list'),
    path('sla/outages/<int:event_id>/', OutageEventView.as_view(),        name='outage-detail'),

    # 6.20 Loan Repayment
    path('investments/<int:investment_id>/repayment/', RepaymentScheduleView.as_view(), name='repayment-schedule'),

    # 6.21 Multi-Branch
    path('branches/',                   BranchView.as_view(),             name='branch-list'),

    # 6.22 Insurance
    path('insurance/',                  InsurancePolicyView.as_view(),    name='insurance-list'),

    # 6.23 Dividends
    path('dividends/',                  DividendView.as_view(),           name='dividend-list'),
    path('dividends/<int:div_id>/',     DividendView.as_view(),           name='dividend-detail'),

    # 6.24 CLV Cohorts
    path('clv/cohorts/',                CLVCohortView.as_view(),          name='clv-cohorts'),
]
