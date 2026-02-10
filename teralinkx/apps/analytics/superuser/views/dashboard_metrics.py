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

class PackageSalesView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            from packages.models import PackageType
            sales = DispatchVoucher.objects.values('package__name').annotate(
                count=Count('id'),
                revenue=Sum('price_paid')
            ).order_by('-count')[:10]
            
            return Response({'data': list(sales)})
        except Exception as e:
            logger.error(f"Error fetching package sales: {e}")
            return Response({'error': 'Failed to fetch package sales'}, status=500)

class LocationPerformanceView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            from locations.models import Location
            performance = DispatchVoucher.objects.values('location__name').annotate(
                sales=Count('id'),
                revenue=Sum('price_paid')
            ).order_by('-sales')[:10]
            
            return Response({'data': list(performance)})
        except Exception as e:
            logger.error(f"Error fetching location performance: {e}")
            return Response({'error': 'Failed to fetch location performance'}, status=500)

class PaymentMethodsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            methods = PaymentTransaction.objects.filter(result_code=0).values('payment_method').annotate(
                count=Count('id'),
                total=Sum('amount')
            ).order_by('-count')
            
            return Response({'data': list(methods)})
        except Exception as e:
            logger.error(f"Error fetching payment methods: {e}")
            return Response({'error': 'Failed to fetch payment methods'}, status=500)

class RecentActivityView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            activities = []
            
            # Recent transactions
            transactions = PaymentTransaction.objects.filter(result_code=0).order_by('-transaction_time')[:5]
            for t in transactions:
                activities.append({
                    'type': 'payment',
                    'description': f'Payment of KSh {t.amount}',
                    'user': t.phone_number,
                    'time': t.transaction_time.isoformat()
                })
            
            # Recent signups
            signups = ClientH.objects.order_by('-created_at')[:5]
            for s in signups:
                activities.append({
                    'type': 'signup',
                    'description': 'New user registered',
                    'user': s.user.username,
                    'time': s.created_at.isoformat()
                })
            
            # Sort by time
            activities.sort(key=lambda x: x['time'], reverse=True)
            
            return Response({'data': activities[:10]})
        except Exception as e:
            logger.error(f"Error fetching recent activity: {e}")
            return Response({'error': 'Failed to fetch recent activity'}, status=500)

class VoucherStatusView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            now = timezone.now()
            active = DispatchVoucher.objects.filter(expires_at__gt=now, status='active').count()
            expired = DispatchVoucher.objects.filter(expires_at__lte=now).count()
            pending = DispatchVoucher.objects.filter(status='pending').count()
            
            return Response({
                'active': active,
                'expired': expired,
                'pending': pending,
                'total': active + expired + pending
            })
        except Exception as e:
            logger.error(f"Error fetching voucher status: {e}")
            return Response({'error': 'Failed to fetch voucher status'}, status=500)

class HourlyUsageView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            from analytics.models import ActiveSession
            from django.db.models.functions import ExtractHour
            
            usage = ActiveSession.objects.annotate(
                hour=ExtractHour('login_time')
            ).values('hour').annotate(count=Count('id')).order_by('hour')
            
            hourly_data = [0] * 24
            for item in usage:
                hourly_data[item['hour']] = item['count']
            
            return Response({'data': hourly_data})
        except Exception as e:
            logger.error(f"Error fetching hourly usage: {e}")
            return Response({'error': 'Failed to fetch hourly usage'}, status=500)

class ConversionFunnelView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            total_users = ClientH.objects.count()
            users_with_vouchers = DispatchVoucher.objects.values('user').distinct().count()
            active_users = DispatchVoucher.objects.filter(
                expires_at__gt=timezone.now(), status='active'
            ).values('user').distinct().count()
            
            return Response({
                'signups': total_users,
                'purchased': users_with_vouchers,
                'active': active_users,
                'conversion_rate': round((users_with_vouchers / total_users * 100) if total_users > 0 else 0, 1)
            })
        except Exception as e:
            logger.error(f"Error fetching conversion funnel: {e}")
            return Response({'error': 'Failed to fetch conversion funnel'}, status=500)

class DeviceBreakdownView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            from analytics.models import UserDevice
            devices = UserDevice.objects.values('device_type').annotate(count=Count('id')).order_by('-count')
            return Response({'data': list(devices)})
        except Exception as e:
            logger.error(f"Error fetching device breakdown: {e}")
            return Response({'error': 'Failed to fetch device breakdown'}, status=500)

class RewardTierDistributionView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            tiers = ClientH.objects.values('reward_tier').annotate(count=Count('id')).order_by('reward_tier')
            return Response({'data': list(tiers)})
        except Exception as e:
            logger.error(f"Error fetching reward tiers: {e}")
            return Response({'error': 'Failed to fetch reward tiers'}, status=500)

class SessionMetricsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            from analytics.models import ActiveSession
            from django.db.models import Avg
            
            metrics = ActiveSession.objects.aggregate(
                avg_duration=Avg(F('logout_time') - F('login_time')),
                total_sessions=Count('id')
            )
            
            return Response({
                'avg_duration_minutes': 45,  # Mock for now
                'total_sessions': metrics['total_sessions'] or 0,
                'active_now': ActiveSession.objects.filter(is_authenticated=True).count()
            })
        except Exception as e:
            logger.error(f"Error fetching session metrics: {e}")
            return Response({'error': 'Failed to fetch session metrics'}, status=500)

class RefundMetricsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            from finance.models import Refund
            total_refunds = Refund.objects.count()
            total_amount = Refund.objects.aggregate(total=Sum('amount'))['total'] or 0
            pending = Refund.objects.filter(status='pending').count()
            
            return Response({
                'total_refunds': total_refunds,
                'total_amount': float(total_amount),
                'pending': pending,
                'refund_rate': 2.3  # Mock percentage
            })
        except Exception as e:
            logger.error(f"Error fetching refund metrics: {e}")
            return Response({'error': 'Failed to fetch refund metrics'}, status=500)