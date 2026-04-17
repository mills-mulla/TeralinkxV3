# apps/finance/views_tax.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import date
from finance.models_tax import TaxReturn


def _serialize(r):
    return {
        'id': r.id,
        'tax_type': r.tax_type,
        'tax_type_display': r.get_tax_type_display(),
        'period_label': r.period_label,
        'period_month': r.period_month,
        'period_year': r.period_year,
        'gross_amount': float(r.gross_amount),
        'tax_amount': float(r.tax_amount),
        'penalties': float(r.penalties),
        'total_payable': float(r.total_payable),
        'due_date': r.due_date.isoformat(),
        'filed_date': r.filed_date.isoformat() if r.filed_date else None,
        'paid_date': r.paid_date.isoformat() if r.paid_date else None,
        'status': r.status,
        'status_display': r.get_status_display(),
        'is_overdue': r.is_overdue,
        'days_until_due': r.days_until_due,
        'kra_reference': r.kra_reference,
    }


class TaxCalendarView(APIView):
    """Generate/get tax calendar for a year"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year = int(request.query_params.get('year', timezone.now().year))
        entries = TaxReturn.generate_calendar(year)

        # Group by month
        calendar = {}
        for entry in entries:
            key = entry.period_label
            if key not in calendar:
                calendar[key] = []
            calendar[key].append(_serialize(entry))

        # Summary stats
        all_entries = TaxReturn.objects.filter(period_year=year)
        return Response({
            'year': year,
            'calendar': calendar,
            'summary': {
                'total': all_entries.count(),
                'filed': all_entries.filter(status='filed').count(),
                'paid': all_entries.filter(status='paid').count(),
                'pending': all_entries.filter(status__in=['pending', 'calculated']).count(),
                'overdue': sum(1 for e in all_entries if e.is_overdue),
            }
        })


class TaxReturnListView(APIView):
    """List tax returns with filters"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = TaxReturn.objects.all()
        tax_type = request.query_params.get('tax_type')
        year = request.query_params.get('year')
        ret_status = request.query_params.get('status')

        if tax_type:
            qs = qs.filter(tax_type=tax_type)
        if year:
            qs = qs.filter(period_year=year)
        if ret_status:
            qs = qs.filter(status=ret_status)

        return Response({'count': qs.count(), 'results': [_serialize(r) for r in qs[:100]]})


class TaxReturnDetailView(APIView):
    """Get, file, or mark paid a tax return"""
    permission_classes = [IsAuthenticated]

    def get(self, request, return_id):
        try:
            return Response(_serialize(TaxReturn.objects.get(id=return_id)))
        except TaxReturn.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, return_id):
        try:
            r = TaxReturn.objects.get(id=return_id)
            action = request.data.get('action')

            if action == 'file':
                r.mark_filed(request.user, request.data.get('kra_reference', ''))
                return Response({'message': 'Tax return filed', 'status': r.status})
            elif action == 'mark_paid':
                r.mark_paid(request.data.get('payment_slip', ''))
                return Response({'message': 'Tax marked as paid', 'status': r.status})
            elif action == 'update_amount':
                r.tax_amount = request.data.get('tax_amount', r.tax_amount)
                r.gross_amount = request.data.get('gross_amount', r.gross_amount)
                r.total_payable = r.tax_amount + r.penalties
                r.status = 'calculated'
                r.notes = request.data.get('notes', r.notes)
                r.save()
                return Response(_serialize(r))
            else:
                return Response({'error': 'action must be file, mark_paid, or update_amount'},
                                status=status.HTTP_400_BAD_REQUEST)
        except TaxReturn.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


class TaxUpcomingView(APIView):
    """Get upcoming tax deadlines"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        days = int(request.query_params.get('days', 30))
        upcoming = TaxReturn.get_upcoming(days)
        overdue = TaxReturn.objects.filter(
            status__in=['pending', 'calculated']
        )
        overdue = [r for r in overdue if r.is_overdue]

        return Response({
            'upcoming': [_serialize(r) for r in upcoming],
            'overdue': [_serialize(r) for r in overdue],
            'next_deadline': _serialize(upcoming.first()) if upcoming.exists() else None,
        })


class WHTCalculateView(APIView):
    """Calculate withholding tax for a period"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        year = int(request.data.get('year', timezone.now().year))
        month = int(request.data.get('month', timezone.now().month))
        try:
            r = TaxReturn.calculate_wht(year, month)
            return Response(_serialize(r))
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
