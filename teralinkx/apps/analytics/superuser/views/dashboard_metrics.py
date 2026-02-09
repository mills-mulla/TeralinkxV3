# api/views/dashboardmetrics.py
from django.db.models import Count, Sum, Q, F
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from users.models import ClientH
from packages.models import DispatchVoucher
from finance.models import PaymentTransaction
import logging

logger = logging.getLogger(__name__)

class DashboardMetricsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            # Calculate date ranges
            today = timezone.now().date()
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)
            
            # Client metrics
            total_clients = ClientH.objects.count()
            new_clients_today = ClientH.objects.filter(
                created_at__date=today
            ).count()
            new_clients_7d = ClientH.objects.filter(
                created_at__date__gte=week_ago
            ).count()
            
            # Active users (clients with active vouchers)
            active_users = DispatchVoucher.objects.filter(
                expires_at__gt=timezone.now(),
                status='active'
            ).values('user').distinct().count()
            
            # Revenue metrics (from transactions)
            revenue_data = PaymentTransaction.objects.filter(
                result_code=0  # Successful transactions
            ).aggregate(
                total_revenue=Sum('amount'),
                total_orders=Count('id')
            )
            
            # Packages sold
            packages_sold = DispatchVoucher.objects.filter(
                activated_at__date__gte=month_ago
            ).count()
            
            # Active ratio (clients with active vouchers vs total clients)
            active_ratio = (active_users / total_clients * 100) if total_clients > 0 else 0
            
            metrics = {
                'totalClients': total_clients,
                'newClientsToday': new_clients_today,
                'newClients7d': new_clients_7d,
                'activeUsers': active_users,
                'totalRevenue': float(revenue_data['total_revenue'] or 0),
                'totalProcessedOrders': revenue_data['total_orders'] or 0,
                'totalPackagesSold': packages_sold,
                'activeRatio': round(active_ratio, 1),
                'clientGrowth': 12.5  # This could be calculated based on previous period
            }
            
            return Response(metrics)
            
        except Exception as e:
            logger.error(f"Error fetching dashboard metrics: {e}")
            return Response(
                {'error': 'Failed to fetch dashboard metrics'}, 
                status=500
            )

class RevenueAnalyticsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            period = request.GET.get('period', '7d')
            
            if period == '7d':
                days = 7
            elif period == '30d':
                days = 30
            else:  # 90d
                days = 90
                
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days-1)
            
            daily_revenue = []
            for i in range(days):
                date = start_date + timedelta(days=i)
                day_revenue = PaymentTransaction.objects.filter(
                    transaction_time__date=date,
                    result_code=0
                ).aggregate(total=Sum('amount'))['total'] or 0
                
                daily_revenue.append({
                    'date': date.isoformat(),
                    'revenue': float(day_revenue)
                })
            
            return Response({
                'period': period,
                'data': daily_revenue
            })
            
        except Exception as e:
            logger.error(f"Error fetching revenue analytics: {e}")
            return Response(
                {'error': 'Failed to fetch revenue analytics'}, 
                status=500
            )

class ClientGrowthView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            period = request.GET.get('period', '30d')
            
            if period == '7d':
                days = 7
            elif period == '30d':
                days = 30
            else:  # 90d
                days = 90
                
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days-1)
            
            daily_growth = []
            for i in range(days):
                date = start_date + timedelta(days=i)
                daily_signups = ClientH.objects.filter(
                    created_at__date=date
                ).count()
                
                daily_growth.append({
                    'date': date.isoformat(),
                    'signups': daily_signups
                })
            
            return Response({
                'period': period,
                'data': daily_growth
            })
            
        except Exception as e:
            logger.error(f"Error fetching client growth: {e}")
            return Response(
                {'error': 'Failed to fetch client growth data'}, 
                status=500
            )