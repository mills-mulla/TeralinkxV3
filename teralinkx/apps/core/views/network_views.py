from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils import timezone

class NetworkInfoView(APIView):
    """
    API endpoint to get client's network information
    Used for network detection and validation
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        Get client's network information
        """
        try:
            # Get client IP
            client_ip = self._get_client_ip(request)
            
            # Get MAC from URL params (MikroTik passes this)
            client_mac = request.GET.get('mac') or request.GET.get('client_mac')
            
            response_data = {
                'ip': client_ip,
                'mac': client_mac,
                'timestamp': timezone.now().isoformat(),
                'status': 'ok'
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'ip': None,
                'mac': None,
                'timestamp': timezone.now().isoformat(),
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_200_OK)
    
    def _get_client_ip(self, request):
        """Get client IP from request"""
        # Check X-Forwarded-For (proxy/load balancer)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
            if self._is_valid_ip(ip):
                return ip
        
        # Check REMOTE_ADDR
        remote_addr = request.META.get('REMOTE_ADDR')
        if remote_addr and self._is_valid_ip(remote_addr):
            return remote_addr
        
        # Check URL parameters (MikroTik)
        ip_param = request.GET.get('ip') or request.GET.get('client_ip')
        if ip_param and self._is_valid_ip(ip_param):
            return ip_param
        
        return None
    
    def _is_valid_ip(self, ip):
        """Validate IP address format"""
        if not ip or ip.lower() in ['unknown', 'none', 'null', '']:
            return False
        
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            
            for part in parts:
                if not part.isdigit():
                    return False
                num = int(part)
                if num < 0 or num > 255:
                    return False
            
            # Exclude loopback
            if ip in ['0.0.0.0', '127.0.0.1', '255.255.255.255']:
                return False
            
            return True
        except Exception:
            return False