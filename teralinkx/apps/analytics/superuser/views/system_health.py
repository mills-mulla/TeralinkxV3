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
            
            # 3. Redis/Cache Health
            try:
                from django.core.cache import cache
                cache.set('health_check', 'ok', 10)
                cache_status = 'healthy' if cache.get('health_check') == 'ok' else 'warning'
                health_data['cache_response'] = 'OK'
                health_data['cache_status'] = cache_status
            except:
                health_data['cache_response'] = 'Error'
                health_data['cache_status'] = 'critical'
            
            # 4. Disk Usage
            try:
                disk = psutil.disk_usage('/')
                disk_percent = disk.percent
                health_data['disk_usage'] = f"{disk_percent}%"
                health_data['disk_status'] = 'healthy' if disk_percent < 70 else 'warning' if disk_percent < 85 else 'critical'
            except:
                health_data['disk_usage'] = 'N/A'
                health_data['disk_status'] = 'unknown'
            
            # 5. Memory Usage
            try:
                memory = psutil.virtual_memory()
                mem_percent = memory.percent
                health_data['memory_usage'] = f"{mem_percent}%"
                health_data['memory_status'] = 'healthy' if mem_percent < 70 else 'warning' if mem_percent < 85 else 'critical'
            except:
                health_data['memory_usage'] = 'N/A'
                health_data['memory_status'] = 'unknown'
            
            # 6. Payment Gateway Health (check recent transaction success rate)
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
            
            # 7. Failed Queue Items (system processing health)
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
                'cache_response': 'Error',
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
        
        try:
            # Get active and recent promotions with performance metrics
            promotions = FeaturedPromotion.objects.filter(
                is_active=True
            ).order_by('-start_date')[:10]
            
            experiments = []
            for promo in promotions:
                # Calculate metrics
                views = promo.views or 0
                clicks = promo.clicks or 0
                conversions = promo.conversions or 0
                
                # Calculate conversion rate
                conv_rate = (conversions / views * 100) if views > 0 else 0
                
                # Calculate revenue (conversions * final_price)
                revenue = conversions * float(promo.final_price)
                
                # Determine status
                now = timezone.now()
                if promo.end_date < now:
                    status = 'completed'
                elif promo.start_date > now:
                    status = 'draft'
                elif promo.is_live:
                    status = 'running'
                else:
                    status = 'paused'
                
                # Determine winner based on conversion rate
                winner = promo.promotion_type if conv_rate > 15 else 'Control'
                
                # Calculate confidence (simple heuristic based on sample size)
                confidence = min(95, int((views / 100) * 10)) if views > 0 else 0
                
                experiments.append({
                    'id': promo.id,
                    'name': promo.name,
                    'status': status,
                    'start_date': promo.start_date.strftime('%Y-%m-%d'),
                    'variants': [{
                        'name': promo.promotion_type,
                        'participants': views,
                        'conversions': conversions,
                        'conversion_rate': round(conv_rate, 2),
                        'revenue': revenue
                    }],
                    'winner': winner,
                    'confidence': confidence
                })
            
            return Response({'experiments': experiments})
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error fetching A/B tests: {e}")
            return Response({'experiments': []}, status=200)


class CustomerHealthView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        from users.models import ClientH
        from packages.models import DispatchVoucher
        from django.db.models import Count, Sum, Max, Q
        
        try:
            health_scores = []
            clients = ClientH.objects.all()[:100]  # Limit to 100 for performance
            
            for client in clients:
                # Calculate health score components
                last_activity = client.queue_items.filter(
                    method='mpesa',
                    status__in=['completed', 'processed']
                ).aggregate(Max('created_at'))['created_at__max']
                
                total_purchases = client.queue_items.filter(
                    method='mpesa',
                    status__in=['completed', 'processed']
                ).count()
                
                total_spent = client.queue_items.filter(
                    method='mpesa',
                    status__in=['completed', 'processed']
                ).aggregate(Sum('price'))['price__sum'] or 0
                
                # Engagement score (0-100) based on recency
                if last_activity:
                    days_since_activity = (timezone.now() - last_activity).days
                    engagement = max(0, 100 - (days_since_activity * 10))
                else:
                    engagement = 0
                    days_since_activity = 999
                
                # Usage score (0-100) based on purchase frequency
                usage = min(100, total_purchases * 20)
                
                # Payment score (0-100) based on total spent
                payment = min(100, int(float(total_spent) / 50))
                
                # Overall health score
                health_score = round((engagement + usage + payment) / 3)
                
                # Risk level
                if health_score >= 75:
                    risk = 'low'
                elif health_score >= 50:
                    risk = 'medium'
                elif health_score >= 25:
                    risk = 'high'
                else:
                    risk = 'critical'
                
                health_scores.append({
                    'user_id': client.id,
                    'username': client.display_name or client.user.username,
                    'health_score': health_score,
                    'engagement_score': round(engagement),
                    'usage_score': round(usage),
                    'payment_score': round(payment),
                    'risk_level': risk,
                    'last_activity': last_activity.isoformat() if last_activity else None,
                    'total_purchases': total_purchases,
                    'total_spent': float(total_spent)
                })
            
            # Sort by health score descending
            health_scores.sort(key=lambda x: x['health_score'], reverse=True)
            
            # Summary
            summary = {
                'avg_health_score': round(sum([s['health_score'] for s in health_scores]) / len(health_scores)) if health_scores else 0,
                'low_risk': len([s for s in health_scores if s['risk_level'] == 'low']),
                'medium_risk': len([s for s in health_scores if s['risk_level'] == 'medium']),
                'high_risk': len([s for s in health_scores if s['risk_level'] == 'high']),
                'critical_risk': len([s for s in health_scores if s['risk_level'] == 'critical'])
            }
            
            return Response({
                'health_scores': health_scores,
                'summary': summary
            })
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error fetching customer health: {e}")
            return Response({
                'health_scores': [],
                'summary': {
                    'avg_health_score': 0,
                    'low_risk': 0,
                    'medium_risk': 0,
                    'high_risk': 0,
                    'critical_risk': 0
                }
            }, status=200)


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
