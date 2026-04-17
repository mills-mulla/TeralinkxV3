# apps/finance/urls_ar.py
from django.urls import path
from .views_ar import ARAgingView, CollectionQueueView, CollectionCaseDetailView, ARRefreshView

urlpatterns = [
    path('ar/aging/',              ARAgingView.as_view(),           name='ar-aging'),
    path('ar/collection/',         CollectionQueueView.as_view(),   name='ar-collection'),
    path('ar/collection/refresh/', ARRefreshView.as_view(),         name='ar-refresh'),
    path('ar/collection/<int:case_id>/', CollectionCaseDetailView.as_view(), name='ar-case-detail'),
]
