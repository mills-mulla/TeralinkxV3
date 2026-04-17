# apps/finance/urls_bank_billing.py
from django.urls import path
from .views_bank_billing import (
    BankStatementUploadView, BankStatementEntriesView,
    RecurringBillingListView, RecurringBillingDetailView, ProcessBillingView
)

urlpatterns = [
    path('bank-statements/',                      BankStatementUploadView.as_view(),   name='bank-statement-list'),
    path('bank-statements/<int:statement_id>/',   BankStatementEntriesView.as_view(),  name='bank-statement-entries'),
    path('recurring-billing/',                    RecurringBillingListView.as_view(),  name='recurring-billing-list'),
    path('recurring-billing/process/',            ProcessBillingView.as_view(),        name='recurring-billing-process'),
    path('recurring-billing/<int:billing_id>/',   RecurringBillingDetailView.as_view(), name='recurring-billing-detail'),
]
