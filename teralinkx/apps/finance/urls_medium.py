# apps/finance/urls_medium.py
from django.urls import path
from .views_medium import (
    NotificationPrefsView, PendingApprovalsView,
    FinancialYearView,
    PettyCashView, PettyCashTransactionView,
    PurchaseOrderListView, PurchaseOrderDetailView,
    AuditLogView,
)

urlpatterns = [
    # 6.13 Notifications
    path('notifications/prefs/',    NotificationPrefsView.as_view(),  name='notification-prefs'),
    path('notifications/pending/',  PendingApprovalsView.as_view(),   name='pending-approvals'),

    # 6.14 Financial Year
    path('financial-year/',         FinancialYearView.as_view(),      name='financial-year'),

    # 6.15 Petty Cash
    path('petty-cash/',             PettyCashView.as_view(),          name='petty-cash-list'),
    path('petty-cash/<int:fund_id>/transactions/', PettyCashTransactionView.as_view(), name='petty-cash-txn'),

    # 6.16 Purchase Orders
    path('purchase-orders/',        PurchaseOrderListView.as_view(),  name='po-list'),
    path('purchase-orders/<int:po_id>/', PurchaseOrderDetailView.as_view(), name='po-detail'),

    # 6.17 Audit Trail
    path('audit-log/',              AuditLogView.as_view(),           name='audit-log'),
]
