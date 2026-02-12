import time
import requests
from django.db import connection
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from analytics.models import ActiveSession

class SystemHealthView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            health_data = {}
            
            # 1. Database Response Time
            db_start = time.time()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            db_time = round((time.time() - db_start) * 1000, 2)
            health_data['database_response'] = f"{db_time}ms"
            health_data['database_status'] = 'healthy' if db_time < 100 else 'warning' if db_time < 500 else 'critical'
            
            # 2. Internet Connectivity (ping external service)
            internet_start = time.time()
            try:
                response = requests.get('https://www.google.com', timeout=5)
                internet_time = round((time.time() - internet_start) * 1000, 2)
                health_data['internet_response'] = f"{internet_time}ms"
                health_data['internet_status'] = 'healthy' if response.status_code == 200 else 'warning'
            except:
                health_data['internet_response'] = 'Timeout'
                health_data['internet_status'] = 'critical'
            
            # 3. Active Sessions
            active_sessions = ActiveSession.objects.filter(is_authenticated=True).count()
            health_data['active_sessions'] = active_sessions
            health_data['sessions_status'] = 'healthy'
            
            # 4. System Uptime (mock - would need actual server uptime)
            health_data['uptime'] = '99.9%'
            health_data['uptime_status'] = 'healthy'
            
            return Response(health_data)
            
        except Exception as e:
            return Response({
                'error': str(e),
                'database_response': 'Error',
                'database_status': 'critical',
                'internet_response': 'Error',
                'internet_status': 'critical',
                'active_sessions': 0,
                'sessions_status': 'critical',
                'uptime': 'Unknown',
                'uptime_status': 'critical'
            }, status=500)
