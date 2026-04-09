from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone

class HealthCheckView(APIView):
    """
    Lightweight health check endpoint for frontend connection status
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            "status": "ok",
            "timestamp": timezone.now().isoformat(),
            "service": "teralinkx-api"
        }, status=200)
