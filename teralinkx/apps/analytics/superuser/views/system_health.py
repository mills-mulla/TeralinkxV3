import time
import requests
import psutil
from django.db import connection
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Q

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
            
            # 2. Internet Connectivity
            internet_start = time.time()
            try:
                response = requests.get('https://www.google.com', timeout=5)
                internet_time = round((time.time() - internet_start) * 1000, 2)
                health_data['internet_response'] = f"{internet_time}ms"
                health_data['internet_status'] = 'healthy' if response.status_code == 200 else 'warning'
            except:
                health_data['internet_response'] = 'Timeout'
                health_data['internet_status'] = 'critical'
            
            # 3. Active Network Sessions (RADIUS/Network sessions)
            from analytics.models import ActiveSession
            active_sessions = ActiveSession.objects.filter(
                is_authenticated=True,
                terminated_at__isnull=True
            ).count()
            health_data['active_sessions'] = active_sessions
            
            # 4. Redis/Cache Health
            try:
                from django.core.cache import cache
                cache.set('health_check', 'ok', 10)
                cache_status = 'healthy' if cache.get('health_check') == 'ok' else 'warning'
                health_data['cache_status'] = cache_status
            except:
                health_data['cache_status'] = 'unavailable'
            
            # 5. Disk Usage
            try:
                disk = psutil.disk_usage('/')
                disk_percent = disk.percent
                health_data['disk_usage'] = f"{disk_percent}%"
                health_data['disk_status'] = 'healthy' if disk_percent < 70 else 'warning' if disk_percent < 85 else 'critical'
            except:
                health_data['disk_usage'] = 'N/A'
                health_data['disk_status'] = 'unknown'
            
            # 6. Memory Usage
            try:
                memory = psutil.virtual_memory()
                mem_percent = memory.percent
                health_data['memory_usage'] = f"{mem_percent}%"
                health_data['memory_status'] = 'healthy' if mem_percent < 70 else 'warning' if mem_percent < 85 else 'critical'
            except:
                health_data['memory_usage'] = 'N/A'
                health_data['memory_status'] = 'unknown'
            
            # 7. Payment Gateway Health (check recent transaction success rate)
            from finance.models import PaymentTransaction
            last_hour = timezone.now() - timedelta(hours=1)
            recent_txns = PaymentTransaction.objects.filter(created_at__gte=last_hour)
            total_txns = recent_txns.count()
            if total_txns > 0:
                success_rate = (recent_txns.filter(status='completed').count() / total_txns) * 100
                health_data['payment_gateway'] = f"{round(success_rate, 1)}%"
                health_data['payment_status'] = 'healthy' if success_rate > 90 else 'warning' if success_rate > 70 else 'critical'
            else:
                health_data['payment_gateway'] = 'No data'
                health_data['payment_status'] = 'healthy'
            
            # 8. Failed Queue Items (system processing health)
            from finance.models import TransactionQueue
            failed_queue = TransactionQueue.objects.filter(
                status='failed',
                created_at__gte=last_hour
            ).count()
            health_data['failed_queue_items'] = failed_queue
            health_data['queue_status'] = 'healthy' if failed_queue < 5 else 'warning' if failed_queue < 20 else 'critical'
            
            return Response(health_data)
            
        except Exception as e:
            return Response({
                'error': str(e),
                'database_response': 'Error',
                'database_status': 'critical',
                'internet_response': 'Error',
                'internet_status': 'critical',
                'active_sessions': 0,
                'cache_status': 'critical',
                'disk_usage': 'Error',
                'disk_status': 'critical',
                'memory_usage': 'Error',
                'memory_status': 'critical',
                'payment_gateway': 'Error',
                'payment_status': 'critical',
                'failed_queue_items': 0,
                'queue_status': 'critical'
            }, status=500)


class ABTestingView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        from packages.models import FeaturedPromotion
        from django.db.models import Count, Avg, F
        
        # Get active promotions with performance metrics
        promotions = FeaturedPromotion.objects.filter(
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ).annotate(
            ctr=F('clicks') * 100.0 / F('views'),
            cvr=F('conversions') * 100.0 / F('clicks')
        )[:10]
        
        tests = []
        for promo in promotions:
            tests.append({
                'test_name': promo.name,
                'variant': promo.promotion_type,
                'views': promo.views,
                'clicks': promo.clicks,
                'conversions': promo.conversions,
                'ctr': round(promo.click_through_rate, 2),
                'cvr': round(promo.conversion_rate, 2),
                'status': 'active' if promo.is_live else 'ended'
            })
        
        return Response({'tests': tests})


class CustomerHealthView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        from users.models import ClientH
        from packages.models import DispatchVoucher
        from django.db.models import Count, Avg, Q, F
        
        total_clients = ClientH.objects.count()
        
        # Active clients (with active vouchers)
        active_clients = ClientH.objects.filter(
            dispatch_vouchers__status='active',
            dispatch_vouchers__expires_at__gt=timezone.now()
        ).distinct().count()
        
        # At-risk clients (no purchase in 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        at_risk = ClientH.objects.filter(
            last_seen__lt=thirty_days_ago,
            status='active'
        ).count()
        
        # Healthy clients (recent activity)
        seven_days_ago = timezone.now() - timedelta(days=7)
        healthy = ClientH.objects.filter(
            last_seen__gte=seven_days_ago
        ).count()
        
        # Calculate health score (0-100)
        if total_clients > 0:
            health_score = int((healthy / total_clients) * 100)
        else:
            health_score = 0
        
        return Response({
            'health_score': health_score,
            'total_clients': total_clients,
            'active_clients': active_clients,
            'healthy_clients': healthy,
            'at_risk_clients': at_risk,
            'churn_rate': round((at_risk / total_clients * 100) if total_clients > 0 else 0, 2)
        })


class AuditLogView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        from security.models import SecurityLog
        from django.db.models import Count
        
        # Get recent logs (last 100)
        recent_logs = SecurityLog.objects.select_related('user').order_by('-created_at')[:100]
        
        logs = []
        for log in recent_logs:
            logs.append({
                'timestamp': log.created_at.isoformat(),
                'user': log.user.account if log.user else 'System',
                'action': log.get_action_type_display(),
                'category': log.get_action_category_display(),
                'severity': log.severity,
                'description': log.description,
                'ip_address': log.ip_address,
                'is_suspicious': log.is_suspicious
            })
        
        # Get summary stats
        last_24h = timezone.now() - timedelta(hours=24)
        stats = SecurityLog.objects.filter(created_at__gte=last_24h).aggregate(
            total=Count('id'),
            critical=Count('id', filter=Q(severity='critical')),
            suspicious=Count('id', filter=Q(is_suspicious=True))
        )
        
        return Response({
            'logs': logs,
            'summary': {
                'total_24h': stats['total'],
                'critical_24h': stats['critical'],
                'suspicious_24h': stats['suspicious']
            }
        })


class DataQualityView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        from users.models import ClientH, UserDevice
        from packages.models import DispatchVoucher
        from finance.models import PaymentTransaction
        from django.db.models import Count, Q
        
        # Check data completeness
        total_clients = ClientH.objects.count()
        
        # Clients with complete profiles
        complete_profiles = ClientH.objects.exclude(
            Q(phone_number='') | Q(display_name='')
        ).count()
        
        # Devices with proper identification
        total_devices = UserDevice.objects.count()
        identified_devices = UserDevice.objects.exclude(
            Q(device_name='') | Q(device_type='other')
        ).count()
        
        # Vouchers with proper tracking
        total_vouchers = DispatchVoucher.objects.count()
        tracked_vouchers = DispatchVoucher.objects.exclude(
            transaction_id=''
        ).count()
        
        # Transactions with complete data
        total_transactions = PaymentTransaction.objects.count()
        complete_transactions = PaymentTransaction.objects.exclude(
            Q(initiator='') | Q(gateway_reference='')
        ).count()
        
        # Calculate quality scores
        profile_quality = (complete_profiles / total_clients * 100) if total_clients > 0 else 0
        device_quality = (identified_devices / total_devices * 100) if total_devices > 0 else 0
        voucher_quality = (tracked_vouchers / total_vouchers * 100) if total_vouchers > 0 else 0
        transaction_quality = (complete_transactions / total_transactions * 100) if total_transactions > 0 else 0
        
        # Overall quality score
        quality_score = int((profile_quality + device_quality + voucher_quality + transaction_quality) / 4)
        
        return Response({
            'quality_score': quality_score,
            'metrics': {
                'profile_completeness': round(profile_quality, 2),
                'device_identification': round(device_quality, 2),
                'voucher_tracking': round(voucher_quality, 2),
                'transaction_completeness': round(transaction_quality, 2)
            },
            'counts': {
                'total_clients': total_clients,
                'complete_profiles': complete_profiles,
                'total_devices': total_devices,
                'identified_devices': identified_devices
            }
        })
