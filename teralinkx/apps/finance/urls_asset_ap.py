# apps/finance/urls_asset_ap.py
from django.urls import path
from .views_asset_ap import (
    AssetListView, AssetDetailView,
    VendorInvoiceListView, VendorInvoiceDetailView, APAgingView
)

urlpatterns = [
    path('assets/',                    AssetListView.as_view(),          name='asset-list'),
    path('assets/<int:asset_id>/',     AssetDetailView.as_view(),        name='asset-detail'),
    path('ap/',                        VendorInvoiceListView.as_view(),   name='ap-list'),
    path('ap/aging/',                  APAgingView.as_view(),             name='ap-aging'),
    path('ap/<int:inv_id>/',           VendorInvoiceDetailView.as_view(), name='ap-detail'),
]
