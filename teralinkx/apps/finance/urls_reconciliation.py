"""
Reconciliation URL Routes
"""
from django.urls import path
from finance.views_reconciliation import (
    ReconciliationJobCreateView,
    ReconciliationJobDetailView,
    ReconciliationReviewQueueView,
    ReconciliationMatchApproveView,
    ReconciliationMatchRejectView,
    ReconciliationStatsView
)

urlpatterns = [
    path('reconciliation/jobs/', ReconciliationJobCreateView.as_view(), name='reconciliation-create'),
    path('reconciliation/jobs/<str:job_id>/', ReconciliationJobDetailView.as_view(), name='reconciliation-detail'),
    path('reconciliation/review-queue/', ReconciliationReviewQueueView.as_view(), name='reconciliation-review'),
    path('reconciliation/matches/<int:match_id>/approve/', ReconciliationMatchApproveView.as_view(), name='reconciliation-approve'),
    path('reconciliation/matches/<int:match_id>/reject/', ReconciliationMatchRejectView.as_view(), name='reconciliation-reject'),
    path('reconciliation/stats/', ReconciliationStatsView.as_view(), name='reconciliation-stats'),
]
