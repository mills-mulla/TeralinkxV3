# apps/finance/urls_board_report.py
from django.urls import path
from .views_board_report import (
    GenerateBoardReportView,
    BoardReportDetailView,
    BoardReportListView,
    BoardReportApproveView,
    LatestBoardReportView,
    BoardReportExportPDFView,
    BoardReportExportPPTXView,
    BoardReportEmailView
)

urlpatterns = [
    path('generate/', GenerateBoardReportView.as_view(), name='generate-board-report'),
    path('latest/', LatestBoardReportView.as_view(), name='latest-board-report'),
    path('list/', BoardReportListView.as_view(), name='list-board-reports'),
    path('<int:report_id>/', BoardReportDetailView.as_view(), name='board-report-detail'),
    path('<int:report_id>/approve/', BoardReportApproveView.as_view(), name='approve-board-report'),
    path('<int:report_id>/export/pdf/', BoardReportExportPDFView.as_view(), name='export-board-report-pdf'),
    path('<int:report_id>/export/pptx/', BoardReportExportPPTXView.as_view(), name='export-board-report-pptx'),
    path('<int:report_id>/email/', BoardReportEmailView.as_view(), name='email-board-report'),
]
