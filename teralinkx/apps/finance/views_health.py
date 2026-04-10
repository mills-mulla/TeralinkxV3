# apps/finance/views_health.py
"""
Health Check API Views
Provides health check endpoints for monitoring.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils import timezone
from .health_checks import HealthCheckService
import logging

logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    """
    System health check endpoint
    GET /api/health/
    """
    permission_classes = [AllowAny]  # Allow monitoring tools without auth
    
    def get(self, request):
        """Get system health status"""
        health = HealthCheckService.get_system_health()
        
        # Return 200 if healthy, 503 if unhealthy
        http_status = status.HTTP_200_OK if health['status'] in ['healthy', 'degraded'] else status.HTTP_503_SERVICE_UNAVAILABLE
        
        return Response(health, status=http_status)


class ReadinessCheckView(APIView):
    """
    Readiness check for Kubernetes/load balancers
    GET /api/ready/
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Check if service is ready to accept traffic"""
        # Check critical services only
        db_check = HealthCheckService.check_database()
        redis_check = HealthCheckService.check_redis()
        
        is_ready = (
            db_check['status'] == 'healthy' and
            redis_check['status'] == 'healthy'
        )
        
        if is_ready:
            return Response({
                'status': 'ready',
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'not_ready',
                'timestamp': timezone.now().isoformat(),
                'checks': {
                    'database': db_check,
                    'redis': redis_check
                }
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class LivenessCheckView(APIView):
    """
    Liveness check for Kubernetes
    GET /api/alive/
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Check if service is alive"""
        return Response({
            'status': 'alive',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)


class MetricsView(APIView):
    """
    Prometheus-compatible metrics endpoint
    GET /api/metrics/
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get Prometheus metrics"""
        from finance.models import PaymentTransaction, TransactionQueue
        from finance.models_churn import ChurnPrediction
        from django.db.models import Count, Sum, Avg
        
        try:
            # Payment metrics
            total_transactions = PaymentTransaction.objects.count()
            completed_transactions = PaymentTransaction.objects.filter(
                status='completed'
            ).count()
            
            # Queue metrics
            pending_queue = TransactionQueue.objects.filter(
                status='pending'
            ).count()
            
            failed_queue = TransactionQueue.objects.filter(
                status='failed'
            ).count()
            
            # Churn metrics
            high_risk_customers = ChurnPrediction.objects.filter(
                risk_level__in=['high', 'critical'],
                is_active=True
            ).count()
            
            metrics = {
                'finance_transactions_total': total_transactions,
                'finance_transactions_completed': completed_transactions,
                'finance_queue_pending': pending_queue,
                'finance_queue_failed': failed_queue,
                'finance_churn_high_risk': high_risk_customers,
                'timestamp': timezone.now().isoformat()
            }
            
            return Response(metrics, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Metrics collection failed: {e}")
            return Response({
                'error': 'Metrics collection failed',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
