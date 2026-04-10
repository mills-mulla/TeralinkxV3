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
