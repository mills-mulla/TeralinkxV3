# apps/finance/views_pl.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from finance.models_pl import PLStatement, ForexGainLoss


def _pl(p):
    return {
        'id': p.id,
        'period_label': p.period_label,
        'period_type': p.period_type,
        'period_start': p.period_start.isoformat(),
        'period_end': p.period_end.isoformat(),
        'gross_revenue': float(p.gross_revenue),
        'vat_collected': float(p.vat_collected),
        'net_revenue': float(p.net_revenue),
        'total_expenses': float(p.total_expenses),
        'depreciation': float(p.depreciation),
        'payroll_cost': float(p.payroll_cost),
        'forex_gain_loss': float(p.forex_gain_loss),
        'gross_profit': float(p.gross_profit),
        'net_profit': float(p.net_profit),
        'profit_margin': p.profit_margin,
        'expense_breakdown': p.expense_breakdown,
        'revenue_breakdown': p.revenue_breakdown,
    }


class PLStatementView(APIView):
    """Generate or retrieve P&L statement"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        period_type = request.query_params.get('period_type', 'monthly')
        year = int(request.query_params.get('year', timezone.now().year))
        month = request.query_params.get('month')
        quarter = request.query_params.get('quarter')

        # Auto-generate if not exists
        try:
            if period_type == 'monthly' and month:
                pl = PLStatement.generate(year, month=int(month))
            elif period_type == 'quarterly' and quarter:
                pl = PLStatement.generate(year, quarter=int(quarter))
            else:
                pl = PLStatement.generate(year)
            return Response(_pl(pl))
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PLHistoryView(APIView):
    """List P&L statements"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        period_type = request.query_params.get('period_type', 'monthly')
        qs = PLStatement.objects.filter(period_type=period_type)[:24]
        return Response({'count': qs.count(), 'results': [_pl(p) for p in qs]})


class ForexExposureView(APIView):
    """Currency exposure and forex gain/loss summary"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.db.models import Sum
        from finance.models import Expense

        # Unrealized forex exposure (expenses in foreign currency not yet settled)
        unrealized = ForexGainLoss.objects.filter(is_realized=False)
        realized = ForexGainLoss.objects.filter(is_realized=True)

        total_unrealized = unrealized.aggregate(total=Sum('kes_amount'))['total'] or 0
        total_realized_gl = realized.aggregate(total=Sum('gain_loss'))['total'] or 0

        # USD expenses (bandwidth costs)
        from finance.models import Currency
        usd = Currency.objects.filter(code='USD').first()
        usd_exposure = 0
        if usd:
            usd_expenses = Expense.objects.filter(
                currency=usd,
                approval_status__in=['approved', 'paid']
            ).aggregate(total=Sum('amount'))['total'] or 0
            usd_exposure = float(usd_expenses)

        return Response({
            'usd_exposure': usd_exposure,
            'total_unrealized_kes': float(total_unrealized),
            'total_realized_gain_loss': float(total_realized_gl),
            'unrealized_count': unrealized.count(),
            'recent_forex': [{
                'id': f.id,
                'ref': f.transaction_ref,
                'type': f.transaction_type,
                'currency': f.original_currency.code,
                'original_amount': float(f.original_amount),
                'kes_amount': float(f.kes_amount),
                'gain_loss': float(f.gain_loss),
                'is_realized': f.is_realized,
                'date': f.transaction_date.isoformat(),
            } for f in ForexGainLoss.objects.select_related('original_currency').order_by('-transaction_date')[:20]]
        })
