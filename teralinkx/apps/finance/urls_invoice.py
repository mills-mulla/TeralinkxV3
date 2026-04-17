# apps/finance/urls_invoice.py
from django.urls import path
from .views_invoice import InvoiceListView, InvoiceDetailView, InvoiceDownloadView, InvoiceCreateView

urlpatterns = [
    path('invoices/',                    InvoiceListView.as_view(),    name='invoice-list'),
    path('invoices/create/',             InvoiceCreateView.as_view(),  name='invoice-create'),
    path('invoices/<int:invoice_id>/',   InvoiceDetailView.as_view(),  name='invoice-detail'),
    path('invoices/<int:invoice_id>/pdf/', InvoiceDownloadView.as_view(), name='invoice-pdf'),
]
