"""
Churn Prediction URL Routes
"""
from django.urls import path
from finance.views_churn import (
    ChurnPredictionListView,
    GenerateChurnPredictionsView,
    RetentionTaskListView
)

urlpatterns = [
    path('churn-predictions/', ChurnPredictionListView.as_view(), name='churn-predictions'),
    path('churn-predictions/generate/', GenerateChurnPredictionsView.as_view(), name='generate-churn'),
    path('retention-tasks/', RetentionTaskListView.as_view(), name='retention-tasks'),
]
