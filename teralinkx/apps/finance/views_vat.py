# apps/finance/views_vat.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.utils import timezone
from finance.models_vat import VATReturn
import csv
import io


class VATReturnListView(APIView):
    """List all VAT returns"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        returns = VATReturn.objects.all()
        data = [_serialize(r) for r in returns]
        return Response({'count': len(data), 'results': data})


class VATReturnCalculateView(APIView):
    """Calculate VAT return for a specific month"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        year  = request.data.get('year',  timezone.now().year)
        month = request.data.get('month', timezone.now().month)

        try:
            vat_return = VATReturn.calculate_for_period(int(year), int(month))
            return Response(_serialize(vat_return))
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class VATReturnDetailView(APIView):
    """Get, file, or mark paid a VAT return"""
    permission_classes = [IsAuthenticated]

    def get(self, request, return_id):
        try:
            r = VATReturn.objects.get(id=return_id)
            return Response(_serialize(r))
        except VATReturn.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, return_id):
        try:
            r = VATReturn.objects.get(id=return_id)
            action = request.data.get('action')

            if action == 'file':
                r.mark_filed(request.user, request.data.get('kra_reference', ''))
                return Response({'message': 'VAT return filed', 'status': r.status})
            elif action == 'mark_paid':
                r.mark_paid()
                return Response({'message': 'VAT marked as paid', 'status': r.status})
            else:
                return Response({'error': 'action must be file or mark_paid'}, status=status.HTTP_400_BAD_REQUEST)

        except VATReturn.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


class VATReturnExportView(APIView):
    """Export VAT return as CSV for KRA iTax upload"""
    permission_classes = [IsAuthenticated]

    def get(self, request, return_id):
        try:
            r = VATReturn.objects.get(id=return_id)
        except VATReturn.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(['VAT-3 Return', f'{r.period_month:02d}/{r.period_year}'])
        writer.writerow([])
        writer.writerow(['Section', 'Description', 'Amount (KES)'])
        writer.writerow(['Output VAT', 'VAT charged on sales to customers', float(r.output_vat)])
        writer.writerow(['Total Sales', 'Gross sales (incl. VAT)', float(r.total_sales)])
        writer.writerow([])
        writer.writerow(['Input VAT', 'VAT paid on purchases/expenses', float(r.input_vat)])
        writer.writerow(['Total Purchases', 'Gross purchases (incl. VAT)', float(r.total_purchases)])
        writer.writerow([])
        writer.writerow(['Net VAT Payable', 'Output VAT minus Input VAT', float(r.net_vat)])
        writer.writerow([])
        writer.writerow(['Status', r.get_status_display()])
        writer.writerow(['KRA Reference', r.kra_reference or 'Not filed'])

        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="VAT-Return-{r.period_year}-{r.period_month:02d}.csv"'
        return response


class VATSummaryView(APIView):
    """VAT dashboard summary — current year overview"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year = int(request.query_params.get('year', timezone.now().year))
        returns = VATReturn.objects.filter(period_year=year).order_by('period_month')

        total_output = sum(r.output_vat for r in returns)
        total_input  = sum(r.input_vat for r in returns)
        total_net    = sum(r.net_vat for r in returns)

        # Filing deadline: 20th of following month
        current_month = timezone.now().month
        current_year  = timezone.now().year
        next_deadline_month = current_month + 1 if current_month < 12 else 1
        next_deadline_year  = current_year if current_month < 12 else current_year + 1

        return Response({
            'year': year,
            'total_output_vat': float(total_output),
            'total_input_vat':  float(total_input),
            'total_net_vat':    float(total_net),
            'next_filing_deadline': f'20/{next_deadline_month:02d}/{next_deadline_year}',
            'months': [_serialize(r) for r in returns],
            'unfiled_count': sum(1 for r in returns if r.status in ['draft', 'calculated'])
        })


def _serialize(r):
    return {
        'id': r.id,
        'period': f'{r.period_month:02d}/{r.period_year}',
        'period_month': r.period_month,
        'period_year': r.period_year,
        'output_vat': float(r.output_vat),
        'total_sales': float(r.total_sales),
        'input_vat': float(r.input_vat),
        'total_purchases': float(r.total_purchases),
        'net_vat': float(r.net_vat),
        'status': r.status,
        'status_display': r.get_status_display(),
        'filed_at': r.filed_at.isoformat() if r.filed_at else None,
        'kra_reference': r.kra_reference,
        'filing_deadline': f'20/{(r.period_month % 12) + 1:02d}/{r.period_year if r.period_month < 12 else r.period_year + 1}',
    }
