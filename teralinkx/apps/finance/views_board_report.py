# apps/finance/views_board_report.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.http import HttpResponse
from .models_board_report import BoardReport
from .board_report_service import BoardReportService
from .board_report_export import BoardReportExporter
import logging

logger = logging.getLogger(__name__)


class GenerateBoardReportView(APIView):
    """Generate monthly board report"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        year = request.data.get('year')
        month = request.data.get('month')
        
        if not year or not month:
            # Default to last month
            last_month = timezone.now().replace(day=1) - timezone.timedelta(days=1)
            year = last_month.year
            month = last_month.month
        
        try:
            report = BoardReportService.generate_monthly_report(int(year), int(month))
            
            return Response({
                'message': 'Board report generated successfully',
                'report_id': report.id,
                'report_period': report.report_period_display,
                'status': report.status,
                'generation_time_seconds': report.generation_time_seconds
            })
        except Exception as e:
            return Response(
                {'error': f'Failed to generate report: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BoardReportDetailView(APIView):
    """Get board report details"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, report_id):
        try:
            report = BoardReport.objects.get(id=report_id)
            
            return Response({
                'id': report.id,
                'report_period': report.report_period_display,
                'status': report.status,
                'financial_performance': report.financial_performance,
                'customer_metrics': report.customer_metrics,
                'operational_metrics': report.operational_metrics,
                'risk_register': report.risk_register,
                'cash_flow_forecast': report.cash_flow_forecast,
                'executive_summary': report.executive_summary,
                'key_highlights': report.key_highlights,
                'challenges': report.challenges,
                'recommendations': report.recommendations,
                'generated_at': report.created_at.isoformat(),
                'generation_time_seconds': report.generation_time_seconds
            })
        except BoardReport.DoesNotExist:
            return Response(
                {'error': 'Report not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class BoardReportListView(APIView):
    """List all board reports"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        reports = BoardReport.objects.all()[:12]  # Last 12 months
        
        return Response({
            'reports': [
                {
                    'id': report.id,
                    'report_period': report.report_period_display,
                    'status': report.status,
                    'generated_at': report.created_at.isoformat(),
                    'revenue': report.financial_performance.get('revenue', {}).get('current', 0),
                    'net_profit': report.financial_performance.get('net_profit', 0)
                }
                for report in reports
            ]
        })


class BoardReportApproveView(APIView):
    """Approve board report"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, report_id):
        try:
            report = BoardReport.objects.get(id=report_id)
            report.mark_approved(request.user)
            
            return Response({
                'message': 'Report approved successfully',
                'status': report.status,
                'approved_at': report.approved_at.isoformat()
            })
        except BoardReport.DoesNotExist:
            return Response(
                {'error': 'Report not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class LatestBoardReportView(APIView):
    """Get latest board report"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        report = BoardReport.get_latest()
        
        if not report:
            return Response(
                {'message': 'No board reports available'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({
            'id': report.id,
            'report_period': report.report_period_display,
            'status': report.status,
            'financial_performance': report.financial_performance,
            'customer_metrics': report.customer_metrics,
            'operational_metrics': report.operational_metrics,
            'risk_register': report.risk_register,
            'cash_flow_forecast': report.cash_flow_forecast,
            'executive_summary': report.executive_summary,
            'key_highlights': report.key_highlights,
            'challenges': report.challenges,
            'recommendations': report.recommendations,
            'generated_at': report.created_at.isoformat()
        })


class BoardReportExportPDFView(APIView):
    """Export board report as PDF"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, report_id):
        try:
            report = BoardReport.objects.get(id=report_id)
            
            # Generate PDF
            pdf_buffer = BoardReportExporter.export_to_pdf(report)
            
            # Return as downloadable file
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="board_report_{report.report_period_display}.pdf"'
            
            logger.info(f"PDF export generated for report {report_id}")
            return response
            
        except BoardReport.DoesNotExist:
            return Response(
                {'error': 'Report not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error exporting PDF for report {report_id}: {e}")
            return Response(
                {'error': f'Failed to export PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BoardReportExportPPTXView(APIView):
    """Export board report as PowerPoint"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, report_id):
        try:
            report = BoardReport.objects.get(id=report_id)
            
            # Generate PowerPoint
            pptx_buffer = BoardReportExporter.export_to_pptx(report)
            
            # Return as downloadable file
            response = HttpResponse(
                pptx_buffer.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation'
            )
            response['Content-Disposition'] = f'attachment; filename="board_report_{report.report_period_display}.pptx"'
            
            logger.info(f"PowerPoint export generated for report {report_id}")
            return response
            
        except BoardReport.DoesNotExist:
            return Response(
                {'error': 'Report not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ImportError as e:
            return Response(
                {'error': 'PowerPoint export requires python-pptx library'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Error exporting PowerPoint for report {report_id}: {e}")
            return Response(
                {'error': f'Failed to export PowerPoint: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BoardReportEmailView(APIView):
    """Send board report via email"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, report_id):
        try:
            report = BoardReport.objects.get(id=report_id)
            
            # Get recipient emails from request
            recipient_emails = request.data.get('recipients', [])
            if not recipient_emails:
                return Response(
                    {'error': 'No recipient emails provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            include_pdf = request.data.get('include_pdf', True)
            include_pptx = request.data.get('include_pptx', True)
            
            # Send email
            success = BoardReportExporter.send_board_report_email(
                report,
                recipient_emails,
                include_pdf=include_pdf,
                include_pptx=include_pptx
            )
            
            if success:
                return Response({
                    'message': f'Board report sent to {len(recipient_emails)} recipients',
                    'recipients': recipient_emails
                })
            else:
                return Response(
                    {'error': 'Failed to send email'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
        except BoardReport.DoesNotExist:
            return Response(
                {'error': 'Report not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error sending board report email for report {report_id}: {e}")
            return Response(
                {'error': f'Failed to send email: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
