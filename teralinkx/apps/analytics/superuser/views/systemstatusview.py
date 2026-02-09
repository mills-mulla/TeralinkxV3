# api/views/systemstatusview.py
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from analytics.models import ActiveSession
from finance.models import PaymentTransaction
import logging

logger = logging.getLogger(__name__)

class SystemStatusView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            # Active sessions count
            active_sessions = ActiveSession.objects.filter(is_authenticated=True).count()
            
            # Recent transactions count (last hour)
            hour_ago = timezone.now() - timedelta(hours=1)
            recent_transactions = PaymentTransaction.objects.filter(
                transaction_time__gte=hour_ago
            ).count()
            
            # Error rate (failed transactions in last hour)
            failed_transactions = PaymentTransaction.objects.filter(
                transaction_time__gte=hour_ago,
                result_code__gt=0
            ).count()
            
            total_transactions = recent_transactions or 1  # Avoid division by zero
            error_rate = (failed_transactions / total_transactions) * 100
            
            status_data = {
                'activeSessions': active_sessions,
                'recentTransactions': recent_transactions,
                'errorRate': round(error_rate, 1),
                'uptime': '99.9%',  # This would come from monitoring system
                'apiResponseTime': '124ms'  # Mock data for now
            }
            
            return Response(status_data)
            
        except Exception as e:
            logger.error(f"Error fetching system status: {e}")
            return Response(
                {'error': 'Failed to fetch system status'}, 
                status=500
            )