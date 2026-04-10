# apps/finance/management/commands/test_board_report_export.py
"""
Test Board Report Export Functionality
Tests PDF, PowerPoint, and email export features.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.finance.models_board_report import BoardReport
from apps.finance.board_report_service import BoardReportService
from apps.finance.board_report_export import BoardReportExporter
import os


class Command(BaseCommand):
    help = 'Test board report export functionality (PDF, PowerPoint, Email)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--report-id',
            type=int,
            help='Specific report ID to test (optional, will generate new if not provided)'
        )
        parser.add_argument(
            '--test-email',
            type=str,
            help='Email address to send test report to'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Board Report Export Test ===\n'))
        
        # Get or generate report
        report_id = options.get('report_id')
        
        if report_id:
            try:
                report = BoardReport.objects.get(id=report_id)
                self.stdout.write(f"✓ Using existing report: {report.report_period_display}")
            except BoardReport.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"✗ Report ID {report_id} not found"))
                return
        else:
            # Generate new report for last month
            last_month = timezone.now().replace(day=1) - timezone.timedelta(days=1)
            year = last_month.year
            month = last_month.month
            
            self.stdout.write(f"Generating report for {last_month.strftime('%B %Y')}...")
            report = BoardReportService.generate_monthly_report(year, month)
            self.stdout.write(self.style.SUCCESS(f"✓ Report generated (ID: {report.id})"))
        
        self.stdout.write(f"\nReport Details:")
        self.stdout.write(f"  Period: {report.report_period_display}")
        self.stdout.write(f"  Status: {report.status}")
        self.stdout.write(f"  Generated: {report.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        self.stdout.write(f"  Generation Time: {report.generation_time_seconds}s\n")
        
        # Test PDF Export
        self.stdout.write("Testing PDF Export...")
        try:
            pdf_buffer = BoardReportExporter.export_to_pdf(report)
            pdf_size = len(pdf_buffer.getvalue())
            
            # Save to file for inspection
            output_path = f'/tmp/board_report_{report.report_period_display}.pdf'
            with open(output_path, 'wb') as f:
                f.write(pdf_buffer.getvalue())
            
            self.stdout.write(self.style.SUCCESS(f"✓ PDF generated successfully"))
            self.stdout.write(f"  Size: {pdf_size:,} bytes")
            self.stdout.write(f"  Saved to: {output_path}\n")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ PDF export failed: {e}\n"))
        
        # Test PowerPoint Export
        self.stdout.write("Testing PowerPoint Export...")
        try:
            pptx_buffer = BoardReportExporter.export_to_pptx(report)
            pptx_size = len(pptx_buffer.getvalue())
            
            # Save to file for inspection
            output_path = f'/tmp/board_report_{report.report_period_display}.pptx'
            with open(output_path, 'wb') as f:
                f.write(pptx_buffer.getvalue())
            
            self.stdout.write(self.style.SUCCESS(f"✓ PowerPoint generated successfully"))
            self.stdout.write(f"  Size: {pptx_size:,} bytes")
            self.stdout.write(f"  Saved to: {output_path}\n")
        except ImportError:
            self.stdout.write(self.style.WARNING(
                "⚠ PowerPoint export requires python-pptx library\n"
                "  Install with: pip install python-pptx\n"
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ PowerPoint export failed: {e}\n"))
        
        # Test Email (if email provided)
        test_email = options.get('test_email')
        if test_email:
            self.stdout.write(f"Testing Email Delivery to {test_email}...")
            try:
                success = BoardReportExporter.send_board_report_email(
                    report,
                    [test_email],
                    include_pdf=True,
                    include_pptx=True
                )
                
                if success:
                    self.stdout.write(self.style.SUCCESS(f"✓ Email sent successfully to {test_email}\n"))
                else:
                    self.stdout.write(self.style.ERROR(f"✗ Email delivery failed\n"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ Email test failed: {e}\n"))
        else:
            self.stdout.write(self.style.WARNING(
                "⚠ Email test skipped (use --test-email to test email delivery)\n"
            ))
        
        # Summary
        self.stdout.write(self.style.SUCCESS('=== Test Complete ==='))
        self.stdout.write(f"\nAPI Endpoints Available:")
        self.stdout.write(f"  GET  /api/finance/board-reports/{report.id}/export/pdf/")
        self.stdout.write(f"  GET  /api/finance/board-reports/{report.id}/export/pptx/")
        self.stdout.write(f"  POST /api/finance/board-reports/{report.id}/email/")
        self.stdout.write(f"       Body: {{\"recipients\": [\"email@example.com\"]}}\n")
