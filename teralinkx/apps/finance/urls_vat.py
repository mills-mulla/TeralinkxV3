# apps/finance/urls_vat.py
from django.urls import path
from .views_vat import (
    VATReturnListView, VATReturnCalculateView,
    VATReturnDetailView, VATReturnExportView, VATSummaryView
)

urlpatterns = [
    path('vat/',                          VATReturnListView.as_view(),    name='vat-list'),
    path('vat/calculate/',                VATReturnCalculateView.as_view(), name='vat-calculate'),
    path('vat/summary/',                  VATSummaryView.as_view(),       name='vat-summary'),
    path('vat/<int:return_id>/',          VATReturnDetailView.as_view(),  name='vat-detail'),
    path('vat/<int:return_id>/export/',   VATReturnExportView.as_view(),  name='vat-export'),
]
