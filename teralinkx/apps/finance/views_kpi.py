# apps/finance/views_kpi.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from .models_kpi import KPISnapshot, WeeklySummary
from .kpi_service import KPICalculationService


class KPISummaryView(APIView):
    """Executive KPI dashboard - <100ms response time"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get latest snapshot
        snapshot = KPISnapshot.get_latest()
        
        # If no snapshot exists or is stale (>10 min), trigger async refresh
        if not snapshot or snapshot.is_stale:
            # Trigger async refresh (would use Celery in production)
            try:
                snapshot = KPICalculationService.generate_kpi_snapshot()
            except Exception as e:
                return Response(
                    {'error': f'Failed to generate KPI snapshot: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # Calculate change percentages
        customer_change_pct = 0
        if snapshot.active_customers_last_month > 0:
            customer_change_pct = (
                (snapshot.active_customers - snapshot.active_customers_last_month) 
                / snapshot.active_customers_last_month * 100
            )
        
        cash_change_pct = 0
        if snapshot.cash_position_30d_ago > 0:
            cash_change_pct = (
                (snapshot.cash_position - snapshot.cash_position_30d_ago) 
                / snapshot.cash_position_30d_ago * 100
            )
        
        return Response({
            'mrr_current':              float(snapshot.mrr_current),
            'mrr_last_month':           float(snapshot.mrr_last_month),
            'mrr_target':               float(snapshot.mrr_target),
            'mrr_growth_pct':           float(snapshot.mrr_growth_pct),
            'active_customers':         snapshot.active_customers,
            'active_customers_last_month': snapshot.active_customers_last_month,
            'new_customers_30d':        snapshot.new_customers_30d,
            'churn_rate_30d':           float(snapshot.churn_rate_30d),
            'cash_position':            float(snapshot.cash_position),
            'cash_position_30d_ago':    float(snapshot.cash_position_30d_ago),
            'total_receivables':        float(snapshot.total_receivables),
            'outstanding_receivables':  snapshot.outstanding_receivables,
            'network_uptime_7d':        float(snapshot.network_uptime_7d),
            'revenue_at_risk':          float(snapshot.revenue_at_risk),
            'high_risk_customers':      snapshot.high_risk_customers,
            'meta': {
                'computed_at':          snapshot.timestamp.isoformat(),
                'computation_time_ms':  snapshot.computed_in_ms,
                'age_seconds':          int(snapshot.age_seconds),
                'is_fresh':             not snapshot.is_stale
            }
        })


class WeeklySummaryView(APIView):
    """Get weekly executive summary"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        summary = WeeklySummary.get_latest()
        
        if not summary:
            return Response(
                {'message': 'No weekly summary available yet'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({
            'week_start': summary.week_start.isoformat(),
            'week_end': summary.week_end.isoformat(),
            'generated_at': summary.generated_at.isoformat(),
            'top_wins': summary.top_wins,
            'top_risks': summary.top_risks,
            'budget_status': summary.budget_status,
            'budget_summary': summary.budget_summary,
            'churn_risk_summary': summary.churn_risk_summary,
            'metrics': {
                'weekly_revenue': float(summary.weekly_revenue),
                'new_customers': summary.weekly_new_customers,
                'churned_customers': summary.weekly_churned_customers
            }
        })


class RefreshKPIView(APIView):
    """Manually trigger KPI refresh"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            snapshot = KPICalculationService.generate_kpi_snapshot()
            return Response({
                'message': 'KPI snapshot refreshed successfully',
                'computed_at': snapshot.timestamp.isoformat(),
                'computation_time_ms': snapshot.computed_in_ms
            })
        except Exception as e:
            return Response(
                {'error': f'Failed to refresh KPI: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CashFlowForecastView(APIView):
    """Return latest active cash flow forecast for the Revenue Forecast chart."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from .models_cashflow import CashFlowForecast
        scenario = request.query_params.get('scenario', 'optimistic')
        forecast = CashFlowForecast.objects.filter(
            is_active=True, scenario=scenario
        ).order_by('-forecast_date').first()

        if not forecast:
            # fallback to any active forecast
            forecast = CashFlowForecast.objects.filter(is_active=True).order_by('-forecast_date').first()

        if not forecast:
            return Response({'forecast_data': [], 'total_forecasted': 0, 'average_daily': 0})

        return Response({
            'scenario':               forecast.scenario,
            'period_start':           forecast.period_start.isoformat(),
            'period_end':             forecast.period_end.isoformat(),
            'forecast_data':          forecast.forecast_data,
            'total_forecasted':       float(forecast.total_forecasted),
            'average_daily':          float(forecast.average_daily),
            'model_accuracy':         forecast.model_accuracy,
            'confidence_interval':    forecast.confidence_interval,
            'training_data_size':     forecast.training_data_size,
            'has_weekly_seasonality': forecast.has_weekly_seasonality,
            'has_monthly_seasonality':forecast.has_monthly_seasonality,
        })


class RevenueComparisonView(APIView):
    """Period-over-period revenue comparison with insights. All calculations backend."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from finance.models import TransactionQueue
        from django.db.models import Sum, Count, Avg
        from django.utils import timezone
        from datetime import timedelta
        from dateutil.relativedelta import relativedelta
        from decimal import Decimal

        period = request.query_params.get('period', 'week')  # week|month|quarter|year
        now = timezone.now()

        def get_range(offset):
            """Return (start, end) for a given period offset (0=current, 1=previous)."""
            if period == 'week':
                end = now - timedelta(weeks=offset)
                start = end - timedelta(weeks=1)
            elif period == 'month':
                end = (now - relativedelta(months=offset)).replace(
                    day=1, hour=0, minute=0, second=0, microsecond=0)
                start = end
                end = start + relativedelta(months=1)
            elif period == 'quarter':
                q = (now.month - 1) // 3
                q_start = now.replace(month=q*3+1, day=1, hour=0, minute=0, second=0, microsecond=0)
                start = q_start - relativedelta(months=3*offset)
                end = start + relativedelta(months=3)
            elif period == 'year':
                start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0) - relativedelta(years=offset)
                end = start + relativedelta(years=1)
            else:
                end = now - timedelta(weeks=offset)
                start = end - timedelta(weeks=1)
            return start, end

        def get_stats(start, end):
            qs = TransactionQueue.objects.filter(
                created_at__gte=start, created_at__lt=end,
                status__in=['completed', 'processed']
            )
            agg = qs.aggregate(
                total=Sum('price'),
                count=Count('id'),
                avg=Avg('price')
            )
            return {
                'revenue': float(agg['total'] or 0),
                'transactions': agg['count'] or 0,
                'avg_transaction': float(agg['avg'] or 0),
                'start': start.isoformat(),
                'end': end.isoformat(),
            }

        def get_daily_breakdown(start, end):
            """Daily revenue within a period for sparkline."""
            from django.db.models.functions import TruncDate
            rows = TransactionQueue.objects.filter(
                created_at__gte=start, created_at__lt=end,
                status__in=['completed', 'processed']
            ).annotate(day=TruncDate('created_at')).values('day').annotate(
                total=Sum('price'), count=Count('id')
            ).order_by('day')
            return [{'date': str(r['day']), 'revenue': float(r['total'] or 0), 'transactions': r['count']} for r in rows]

        current_start, current_end = get_range(0)
        previous_start, previous_end = get_range(1)

        current = get_stats(current_start, current_end)
        previous = get_stats(previous_start, previous_end)
        current['daily'] = get_daily_breakdown(current_start, current_end)
        previous['daily'] = get_daily_breakdown(previous_start, previous_end)

        # Calculate change
        rev_change = current['revenue'] - previous['revenue']
        rev_change_pct = (rev_change / previous['revenue'] * 100) if previous['revenue'] > 0 else 0
        txn_change_pct = ((current['transactions'] - previous['transactions']) / previous['transactions'] * 100) if previous['transactions'] > 0 else 0

        # Auto-generate insights
        insights = []
        if rev_change_pct > 10:
            insights.append(f"Revenue up {rev_change_pct:.1f}% — strong growth this {period}.")
        elif rev_change_pct < -10:
            insights.append(f"Revenue down {abs(rev_change_pct):.1f}% — investigate drop in transactions.")
        elif abs(rev_change_pct) <= 5:
            insights.append(f"Revenue stable ({rev_change_pct:+.1f}%) — consistent performance.")

        if txn_change_pct > 15:
            insights.append(f"Transaction volume up {txn_change_pct:.1f}% — more customers paying.")
        elif txn_change_pct < -15:
            insights.append(f"Transaction volume down {abs(txn_change_pct):.1f}% — fewer payments processed.")

        if current['avg_transaction'] > previous['avg_transaction'] * 1.1:
            insights.append(f"Average transaction value increased — customers upgrading packages.")
        elif current['avg_transaction'] < previous['avg_transaction'] * 0.9:
            insights.append(f"Average transaction value dropped — possible downgrade trend.")

        if not insights:
            insights.append(f"No significant changes this {period}.")

        # Build multi-period trend (last 8 periods)
        trend = []
        for i in range(7, -1, -1):
            s, e = get_range(i)
            stats = get_stats(s, e)
            label = s.strftime('%d %b' if period == 'week' else '%b %Y' if period in ['month', 'quarter'] else '%Y')
            trend.append({'label': label, 'revenue': stats['revenue'], 'transactions': stats['transactions']})

        return Response({
            'period': period,
            'current': current,
            'previous': previous,
            'change': {
                'revenue': rev_change,
                'revenue_pct': round(rev_change_pct, 1),
                'transactions_pct': round(txn_change_pct, 1),
                'direction': 'up' if rev_change >= 0 else 'down',
            },
            'insights': insights,
            'trend': trend,
        })
