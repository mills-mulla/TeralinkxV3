# apps/users/token_health.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class TokenHealthCheckAPIView(APIView):
    """
    Lightweight endpoint for frontend to check token health.
    Used by frontend monitoring to detect backend restarts and token issues.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Quick health check that validates token and returns minimal data.
        """
        try:
            # Get user and client info
            user = request.user
            client = user.client_profile
            
            # Get backend version/restart indicator
            backend_version = cache.get('backend_version', 'unknown')
            if not backend_version or backend_version == 'unknown':
                # Set initial version
                backend_version = timezone.now().strftime('%Y%m%d_%H%M%S')
                cache.set('backend_version', backend_version, timeout=86400)
            
            # Check token expiry
            token_exp = None
            if hasattr(request.auth, 'payload'):
                token_exp = request.auth.payload.get('exp')
            
            response_data = {
                'status': 'healthy',
                'user_id': user.id,
                'client_account': client.account,
                'backend_version': backend_version,
                'server_time': timezone.now().isoformat(),
                'token_expires_at': token_exp,
                'balance': float(client.balance),
                'account_status': client.status
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Token health check failed: {e}")
            return Response({
                'status': 'unhealthy',
                'error': 'Health check failed',
                'server_time': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BackendVersionAPIView(APIView):
    """
    Public endpoint to check backend version without authentication.
    Used to detect backend restarts.
    """
    permission_classes = []
    authentication_classes = []
    
    def get(self, request):
        """Get backend version identifier."""
        try:
            backend_version = cache.get('backend_version')
            if not backend_version:
                # Generate new version on first request after restart
                backend_version = timezone.now().strftime('%Y%m%d_%H%M%S')
                cache.set('backend_version', backend_version, timeout=86400)
                logger.info(f"🔄 New backend version generated: {backend_version}")
            
            return Response({
                'backend_version': backend_version,
                'server_time': timezone.now().isoformat(),
                'status': 'online'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Backend version check failed: {e}")
            return Response({
                'status': 'error',
                'server_time': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)