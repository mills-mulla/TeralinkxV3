# apps/core/auth_health.py - Token Health Check Endpoint
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.conf import settings
from django.utils import timezone
from django.core.cache import caches
import logging

logger = logging.getLogger(__name__)

class TokenHealthCheckView(APIView):
    """
    Lightweight endpoint for frontend to check token health.
    Used by frontend for proactive token validation and backend restart detection.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Quick health check that validates token and returns backend status.
        """
        try:
            user = request.user
            
            # Get backend version info
            backend_version = getattr(settings, 'BACKEND_VERSION', 'unknown')
            jwt_version = getattr(settings, 'JWT_SECRET_VERSION', 'v1')
            
            # Check if user has valid session
            has_valid_session = hasattr(user, 'clienth') and user.clienth is not None
            
            # Get token expiry info if available
            token_info = {}
            if hasattr(request, 'auth') and request.auth:
                try:
                    # Extract token expiry from JWT
                    import jwt
                    from django.conf import settings
                    
                    token_payload = jwt.decode(
                        str(request.auth), 
                        settings.SECRET_KEY, 
                        algorithms=['HS256'],
                        options={"verify_signature": False}
                    )
                    
                    token_info = {
                        'expires_at': token_payload.get('exp'),
                        'issued_at': token_payload.get('iat'),
                        'user_id': token_payload.get('user_id'),
                        'token_type': token_payload.get('token_type', 'access')
                    }
                except Exception as e:
                    logger.warning(f"Could not decode token info: {e}")
            
            # Response with health status
            response_data = {
                'status': 'healthy',
                'timestamp': timezone.now().isoformat(),
                'backend_version': backend_version,
                'jwt_version': jwt_version,
                'user_authenticated': True,
                'has_valid_session': has_valid_session,
                'user_id': user.id,
                'username': user.username,
                'token_info': token_info
            }
            
            # Add custom headers for frontend detection
            response = Response(response_data, status=status.HTTP_200_OK)
            response['X-Backend-Version'] = backend_version
            response['X-Token-Version'] = jwt_version
            response['X-Health-Check'] = 'ok'
            
            return response
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return Response({
                'status': 'error',
                'error': 'Health check failed',
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BackendStatusView(APIView):
    """
    Public endpoint to check backend status and version.
    Used by frontend to detect backend restarts without authentication.
    """
    permission_classes = []  # No authentication required
    
    def get(self, request):
        """
        Return backend status and version info.
        """
        try:
            backend_version = getattr(settings, 'BACKEND_VERSION', 'unknown')
            jwt_version = getattr(settings, 'JWT_SECRET_VERSION', 'v1')
            
            # Check if Redis is available
            redis_status = 'unknown'
            try:
                cache = caches['default']
                cache.set('health_check', 'ok', timeout=10)
                test_value = cache.get('health_check')
                redis_status = 'healthy' if test_value == 'ok' else 'unhealthy'
            except Exception as e:
                redis_status = 'unhealthy'
                logger.warning(f"Redis health check failed: {e}")
            
            response_data = {
                'status': 'online',
                'timestamp': timezone.now().isoformat(),
                'backend_version': backend_version,
                'jwt_version': jwt_version,
                'redis_status': redis_status,
                'services': {
                    'authentication': 'available',
                    'token_refresh': 'available',
                    'device_auth': 'available'
                }
            }
            
            response = Response(response_data, status=status.HTTP_200_OK)
            response['X-Backend-Version'] = backend_version
            response['X-Token-Version'] = jwt_version
            response['X-Service-Status'] = 'online'
            
            return response
            
        except Exception as e:
            logger.error(f"Backend status check error: {e}")
            return Response({
                'status': 'error',
                'error': 'Backend status check failed',
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SessionBackupService:
    """
    Service for backing up and restoring user sessions to Redis.
    """
    
    @staticmethod
    def backup_session(user_id, session_data):
        """Backup session data to Redis"""
        try:
            cache = caches['sessions']
            cache_key = f"session_backup:{user_id}"
            
            backup_data = {
                'user_id': user_id,
                'session_data': session_data,
                'backup_time': timezone.now().isoformat(),
                'backend_version': getattr(settings, 'BACKEND_VERSION', 'unknown')
            }
            
            cache.set(cache_key, backup_data, timeout=86400)  # 24 hours
            logger.info(f"Session backed up for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Session backup failed for user {user_id}: {e}")
            return False
    
    @staticmethod
    def restore_session(user_id):
        """Restore session from backup"""
        try:
            cache = caches['sessions']
            cache_key = f"session_backup:{user_id}"
            
            backup_data = cache.get(cache_key)
            if backup_data:
                logger.info(f"Session restored for user {user_id}")
                return backup_data['session_data']
            
            return None
            
        except Exception as e:
            logger.error(f"Session restore failed for user {user_id}: {e}")
            return None
    
    @staticmethod
    def clear_session_backup(user_id):
        """Clear session backup"""
        try:
            cache = caches['sessions']
            cache_key = f"session_backup:{user_id}"
            cache.delete(cache_key)
            logger.info(f"Session backup cleared for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Session backup clear failed for user {user_id}: {e}")
            return False