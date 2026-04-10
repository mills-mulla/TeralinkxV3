# apps/finance/health_checks.py
"""
Health Check System
Monitors system health for production deployment.
"""
from django.db import connection
from django.core.cache import cache
from django.utils import timezone
import redis
import logging

logger = logging.getLogger(__name__)


class HealthCheckService:
    """Service for system health monitoring"""
    
    @staticmethod
    def check_database():
        """Check database connectivity"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                row = cursor.fetchone()
                return {
                    'status': 'healthy' if row[0] == 1 else 'unhealthy',
                    'message': 'Database connection successful',
                    'response_time_ms': 0
                }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                'status': 'unhealthy',
                'message': f'Database error: {str(e)}',
                'response_time_ms': 0
            }
    
    @staticmethod
    def check_redis():
        """Check Redis connectivity"""
        try:
            # Test cache
            test_key = 'health_check_test'
            test_value = 'ok'
            cache.set(test_key, test_value, 10)
            result = cache.get(test_key)
            cache.delete(test_key)
            
            return {
                'status': 'healthy' if result == test_value else 'unhealthy',
                'message': 'Redis connection successful',
                'response_time_ms': 0
            }
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                'status': 'unhealthy',
                'message': f'Redis error: {str(e)}',
                'response_time_ms': 0
            }
    
    @staticmethod
    def check_celery():
        """Check Celery worker status"""
        try:
            from celery import current_app
            
            # Check if workers are active
            inspect = current_app.control.inspect()
            active_workers = inspect.active()
            
            if active_workers:
                worker_count = len(active_workers)
                return {
                    'status': 'healthy',
                    'message': f'{worker_count} Celery workers active',
                    'workers': list(active_workers.keys())
                }
            else:
                return {
                    'status': 'unhealthy',
                    'message': 'No Celery workers found',
                    'workers': []
                }
        except Exception as e:
            logger.error(f"Celery health check failed: {e}")
            return {
                'status': 'unhealthy',
                'message': f'Celery error: {str(e)}',
                'workers': []
            }
    
    @staticmethod
    def check_timescaledb():
        """Check TimescaleDB extension"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT extname FROM pg_extension WHERE extname = 'timescaledb'")
                result = cursor.fetchone()
                
                if result:
                    return {
                        'status': 'healthy',
                        'message': 'TimescaleDB extension active',
                        'extension': result[0]
                    }
                else:
                    return {
                        'status': 'warning',
                        'message': 'TimescaleDB extension not found',
                        'extension': None
                    }
        except Exception as e:
            logger.error(f"TimescaleDB health check failed: {e}")
            return {
                'status': 'unhealthy',
                'message': f'TimescaleDB error: {str(e)}',
                'extension': None
            }
    
    @staticmethod
    def check_kpi_cache():
        """Check KPI cache freshness"""
        try:
            from finance.models_kpi import KPISnapshot
            
            latest_snapshot = KPISnapshot.objects.latest('timestamp')
            age_seconds = (timezone.now() - latest_snapshot.timestamp).total_seconds()
            
            # KPI should be refreshed every 5 minutes
            is_fresh = age_seconds < 600  # 10 minutes threshold
            
            return {
                'status': 'healthy' if is_fresh else 'warning',
                'message': f'KPI cache age: {age_seconds:.0f}s',
                'age_seconds': age_seconds,
                'last_update': latest_snapshot.timestamp.isoformat()
            }
        except Exception as e:
            logger.error(f"KPI cache health check failed: {e}")
            return {
                'status': 'unhealthy',
                'message': f'KPI cache error: {str(e)}',
                'age_seconds': None
            }
    
    @staticmethod
    def check_payment_gateway():
        """Check payment gateway configuration"""
        try:
            from finance.models import PaymentGateway
            
            active_gateways = PaymentGateway.objects.filter(
                status='active'
            ).count()
            
            default_gateway = PaymentGateway.objects.filter(
                is_default=True
            ).first()
            
            if active_gateways > 0 and default_gateway:
                return {
                    'status': 'healthy',
                    'message': f'{active_gateways} active payment gateways',
                    'active_count': active_gateways,
                    'default_gateway': default_gateway.name
                }
            else:
                return {
                    'status': 'warning',
                    'message': 'No active payment gateways configured',
                    'active_count': active_gateways,
                    'default_gateway': None
                }
        except Exception as e:
            logger.error(f"Payment gateway health check failed: {e}")
            return {
                'status': 'unhealthy',
                'message': f'Payment gateway error: {str(e)}',
                'active_count': 0
            }
    
    @staticmethod
    def get_system_health():
        """Get complete system health status"""
        checks = {
            'database': HealthCheckService.check_database(),
            'redis': HealthCheckService.check_redis(),
            'celery': HealthCheckService.check_celery(),
            'timescaledb': HealthCheckService.check_timescaledb(),
            'kpi_cache': HealthCheckService.check_kpi_cache(),
            'payment_gateway': HealthCheckService.check_payment_gateway()
        }
        
        # Determine overall status
        statuses = [check['status'] for check in checks.values()]
        
        if all(s == 'healthy' for s in statuses):
            overall_status = 'healthy'
        elif any(s == 'unhealthy' for s in statuses):
            overall_status = 'unhealthy'
        else:
            overall_status = 'degraded'
        
        return {
            'status': overall_status,
            'timestamp': timezone.now().isoformat(),
            'checks': checks
        }
