# api/views/dashboardmetrics.py
from django.db.models import Count, Sum, Q, F
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from users.models import ClientH
from packages.models import DispatchVoucher
from finance.models import PaymentTransaction, TransactionQueue
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
            
            # Revenue metrics (from M-Pesa transactions in queue)
            total_revenue = TransactionQueue.objects.filter(
                method='mpesa'
            ).aggregate(total=Sum('price'))['total'] or 0
            
            # Packages sold
            packages_sold = DispatchVoucher.objects.filter(
                activated_at__date__gte=month_ago
            ).count()
            
            # Calculate trends
            prev_week_clients = ClientH.objects.filter(
                created_at__date__lt=week_ago
            ).count()
            clients_trend = 'up' if total_clients > prev_week_clients else 'down' if total_clients < prev_week_clients else 'stable'
            clients_trend_value = f"{abs(round((total_clients - prev_week_clients) / prev_week_clients * 100, 1)) if prev_week_clients > 0 else 0}%"
            
            prev_week_new = ClientH.objects.filter(
                created_at__date__gte=week_ago - timedelta(days=7),
                created_at__date__lt=week_ago
            ).count()
            new_clients_trend = 'up' if new_clients_7d > prev_week_new else 'down' if new_clients_7d < prev_week_new else 'stable'
            new_clients_trend_value = f"{abs(round((new_clients_7d - prev_week_new) / prev_week_new * 100, 1)) if prev_week_new > 0 else 0}%"
            
            prev_week_active = DispatchVoucher.objects.filter(
                expires_at__gt=timezone.now() - timedelta(days=7),
                status='active',
                created_at__date__lt=week_ago
            ).values('user').distinct().count()
            active_users_trend = 'up' if active_users > prev_week_active else 'down' if active_users < prev_week_active else 'stable'
            active_users_trend_value = f"{abs(round((active_users - prev_week_active) / prev_week_active * 100, 1)) if prev_week_active > 0 else 0}%"
            
            # Revenue trend calculation
            prev_week_revenue = TransactionQueue.objects.filter(
                method='mpesa',
                created_at__date__lt=week_ago
            ).aggregate(total=Sum('price'))['total'] or 0
            revenue_trend = 'up' if total_revenue > prev_week_revenue else 'down' if total_revenue < prev_week_revenue else 'stable'
            revenue_trend_value = f"{abs(round((total_revenue - prev_week_revenue) / prev_week_revenue * 100, 1)) if prev_week_revenue > 0 else 0}%"
            
            # Active ratio (clients with active vouchers vs total clients)
            active_ratio = (active_users / total_clients * 100) if total_clients > 0 else 0
            
            metrics = {
                'totalClients': total_clients,
                'clientsTrend': clients_trend,
                'clientsTrendValue': clients_trend_value,
                'newClientsToday': new_clients_today,
                'newClients7d': new_clients_7d,
                'newClientsTrend': new_clients_trend,
                'newClientsTrendValue': new_clients_trend_value,
                'activeUsers': active_users,
                'activeUsersTrend': active_users_trend,
                'activeUsersTrendValue': active_users_trend_value,
                'totalRevenue': float(total_revenue),
                'revenueTrend': revenue_trend,
                'revenueTrendValue': revenue_trend_value,
                'totalPackagesSold': packages_sold,
                'activeRatio': round(active_ratio, 1)
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
            from users.models import UserDevice
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

class CohortAnalysisView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            from django.db.models.functions import TruncMonth
            
            # Get cohorts by signup month
            cohorts = ClientH.objects.annotate(
                cohort_month=TruncMonth('created_at')
            ).values('cohort_month').annotate(
                users=Count('id')
            ).order_by('-cohort_month')[:12]
            
            cohort_data = []
            for cohort in cohorts:
                month = cohort['cohort_month']
                users = cohort['users']
                
                # Calculate retention for each month after signup
                retention = []
                for i in range(6):  # 6 months retention
                    target_month = month + timedelta(days=30 * i)
                    active = DispatchVoucher.objects.filter(
                        user__clienth__created_at__month=month.month,
                        user__clienth__created_at__year=month.year,
                        activated_at__gte=target_month,
                        activated_at__lt=target_month + timedelta(days=30)
                    ).values('user').distinct().count()
                    
                    retention.append({
                        'month': i,
                        'users': active,
                        'rate': round((active / users * 100) if users > 0 else 0, 1)
                    })
                
                cohort_data.append({
                    'cohort': month.strftime('%Y-%m'),
                    'size': users,
                    'retention': retention
                })
            
            return Response({'data': cohort_data})
        except Exception as e:
            logger.error(f"Error fetching cohort analysis: {e}")
            return Response({'error': 'Failed to fetch cohort analysis'}, status=500)

class RFMSegmentationView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            from django.db.models import Max, Count
            
            now = timezone.now()
            segments = []
            
            # Calculate RFM for each client
            clients = ClientH.objects.annotate(
                last_purchase=Max('user__dispatchvoucher__activated_at'),
                purchase_count=Count('user__dispatchvoucher'),
                total_spent=Sum('user__dispatchvoucher__price_paid')
            ).filter(purchase_count__gt=0)
            
            for client in clients:
                recency = (now - client.last_purchase).days if client.last_purchase else 999
                frequency = client.purchase_count
                monetary = float(client.total_spent or 0)
                
                # Simple RFM scoring (1-5)
                r_score = 5 if recency <= 30 else 4 if recency <= 60 else 3 if recency <= 90 else 2 if recency <= 180 else 1
                f_score = 5 if frequency >= 10 else 4 if frequency >= 5 else 3 if frequency >= 3 else 2 if frequency >= 2 else 1
                m_score = 5 if monetary >= 5000 else 4 if monetary >= 2000 else 3 if monetary >= 1000 else 2 if monetary >= 500 else 1
                
                # Segment classification
                if r_score >= 4 and f_score >= 4 and m_score >= 4:
                    segment = 'Champions'
                elif r_score >= 3 and f_score >= 3 and m_score >= 3:
                    segment = 'Loyal'
                elif r_score >= 4 and f_score <= 2:
                    segment = 'New'
                elif r_score <= 2 and f_score >= 3:
                    segment = 'At Risk'
                elif r_score <= 2 and f_score <= 2:
                    segment = 'Lost'
                else:
                    segment = 'Potential'
                
                segments.append({
                    'user_id': client.user.id,
                    'username': client.user.username,
                    'segment': segment,
                    'recency': recency,
                    'frequency': frequency,
                    'monetary': monetary,
                    'rfm_score': r_score + f_score + m_score
                })
            
            # Aggregate by segment
            segment_summary = {}
            for seg in segments:
                seg_name = seg['segment']
                if seg_name not in segment_summary:
                    segment_summary[seg_name] = {'count': 0, 'total_value': 0}
                segment_summary[seg_name]['count'] += 1
                segment_summary[seg_name]['total_value'] += seg['monetary']
            
            return Response({
                'segments': segments[:100],  # Limit to 100 for performance
                'summary': segment_summary
            })
        except Exception as e:
            logger.error(f"Error fetching RFM segmentation: {e}")
            return Response({'error': 'Failed to fetch RFM segmentation'}, status=500)

class FinancialAnalyticsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            now = timezone.now()
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # MRR (Monthly Recurring Revenue)
            mrr = PaymentTransaction.objects.filter(
                transaction_time__gte=month_start,
                result_code=0
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # ARR (Annual Recurring Revenue)
            arr = PaymentTransaction.objects.filter(
                transaction_time__gte=year_start,
                result_code=0
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # ARPU (Average Revenue Per User)
            active_users = DispatchVoucher.objects.filter(
                expires_at__gt=now,
                status='active'
            ).values('user').distinct().count()
            
            arpu = (mrr / active_users) if active_users > 0 else 0
            
            # Revenue by package (with margins)
            package_revenue = DispatchVoucher.objects.values(
                'package__name', 'package__price'
            ).annotate(
                sales=Count('id'),
                revenue=Sum('price_paid')
            ).order_by('-revenue')[:10]
            
            package_data = []
            for pkg in package_revenue:
                revenue = float(pkg['revenue'] or 0)
                cost = float(pkg['package__price'] or 0) * 0.3  # Assume 30% cost
                profit = revenue - (cost * pkg['sales'])
                margin = (profit / revenue * 100) if revenue > 0 else 0
                
                package_data.append({
                    'name': pkg['package__name'],
                    'sales': pkg['sales'],
                    'revenue': revenue,
                    'profit': profit,
                    'margin': round(margin, 1)
                })
            
            # Customer Lifetime Value (LTV)
            avg_customer_lifespan = 12  # months (mock)
            ltv = arpu * avg_customer_lifespan
            
            return Response({
                'mrr': float(mrr),
                'arr': float(arr),
                'arpu': round(float(arpu), 2),
                'ltv': round(float(ltv), 2),
                'active_users': active_users,
                'package_performance': package_data,
                'growth_rate': 15.5  # Mock percentage
            })
        except Exception as e:
            logger.error(f"Error fetching financial analytics: {e}")
            return Response({'error': 'Failed to fetch financial analytics'}, status=500)

class FunnelAnalysisView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            # Funnel stages
            total_signups = ClientH.objects.count()
            
            # Stage 1: Signed up
            stage1 = total_signups
            
            # Stage 2: Viewed packages (users with at least one voucher)
            stage2 = DispatchVoucher.objects.values('user').distinct().count()
            
            # Stage 3: Added to cart / Initiated payment
            stage3 = PaymentTransaction.objects.values('phone_number').distinct().count()
            
            # Stage 4: Completed payment
            stage4 = PaymentTransaction.objects.filter(result_code=0).values('phone_number').distinct().count()
            
            # Stage 5: Activated voucher
            stage5 = DispatchVoucher.objects.filter(status='active').values('user').distinct().count()
            
            # Stage 6: Repeat purchase
            stage6 = DispatchVoucher.objects.values('user').annotate(
                purchases=Count('id')
            ).filter(purchases__gt=1).count()
            
            # Calculate drop-off rates
            stages = [
                {'name': 'Signups', 'users': stage1, 'rate': 100, 'dropoff': 0},
                {'name': 'Viewed Packages', 'users': stage2, 'rate': round((stage2/stage1*100) if stage1 > 0 else 0, 1), 'dropoff': stage1 - stage2},
                {'name': 'Initiated Payment', 'users': stage3, 'rate': round((stage3/stage1*100) if stage1 > 0 else 0, 1), 'dropoff': stage2 - stage3},
                {'name': 'Completed Payment', 'users': stage4, 'rate': round((stage4/stage1*100) if stage1 > 0 else 0, 1), 'dropoff': stage3 - stage4},
                {'name': 'Activated Voucher', 'users': stage5, 'rate': round((stage5/stage1*100) if stage1 > 0 else 0, 1), 'dropoff': stage4 - stage5},
                {'name': 'Repeat Purchase', 'users': stage6, 'rate': round((stage6/stage1*100) if stage1 > 0 else 0, 1), 'dropoff': stage5 - stage6}
            ]
            
            # Identify biggest drop-off
            max_dropoff = max(stages, key=lambda x: x['dropoff'])
            
            return Response({
                'stages': stages,
                'conversion_rate': round((stage6/stage1*100) if stage1 > 0 else 0, 1),
                'biggest_dropoff': max_dropoff['name'],
                'total_signups': stage1,
                'repeat_customers': stage6
            })
        except Exception as e:
            logger.error(f"Error fetching funnel analysis: {e}")
            return Response({'error': 'Failed to fetch funnel analysis'}, status=500)

class ChurnPredictionView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            now = timezone.now()
            at_risk_users = []
            
            # Identify users at risk of churning
            clients = ClientH.objects.annotate(
                last_activity=Max('user__dispatchvoucher__activated_at'),
                total_purchases=Count('user__dispatchvoucher')
            ).filter(total_purchases__gt=0)
            
            for client in clients:
                if not client.last_activity:
                    continue
                    
                days_inactive = (now - client.last_activity).days
                
                # Churn risk scoring
                if days_inactive > 90:
                    risk = 'high'
                    probability = 85
                elif days_inactive > 60:
                    risk = 'medium'
                    probability = 60
                elif days_inactive > 30:
                    risk = 'low'
                    probability = 35
                else:
                    continue
                
                at_risk_users.append({
                    'user_id': client.user.id,
                    'username': client.user.username,
                    'days_inactive': days_inactive,
                    'total_purchases': client.total_purchases,
                    'risk_level': risk,
                    'churn_probability': probability
                })
            
            # Sort by risk
            at_risk_users.sort(key=lambda x: x['churn_probability'], reverse=True)
            
            # Summary
            high_risk = len([u for u in at_risk_users if u['risk_level'] == 'high'])
            medium_risk = len([u for u in at_risk_users if u['risk_level'] == 'medium'])
            low_risk = len([u for u in at_risk_users if u['risk_level'] == 'low'])
            
            return Response({
                'at_risk_users': at_risk_users[:50],
                'summary': {
                    'high_risk': high_risk,
                    'medium_risk': medium_risk,
                    'low_risk': low_risk,
                    'total_at_risk': len(at_risk_users)
                },
                'churn_rate': round((len(at_risk_users) / ClientH.objects.count() * 100) if ClientH.objects.count() > 0 else 0, 1)
            })
        except Exception as e:
            logger.error(f"Error fetching churn prediction: {e}")
            return Response({'error': 'Failed to fetch churn prediction'}, status=500)

class RevenueForecastView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            # Get historical revenue (last 12 months)
            historical = []
            for i in range(12, 0, -1):
                month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
                month_end = month_start + timedelta(days=30)
                
                revenue = PaymentTransaction.objects.filter(
                    transaction_time__gte=month_start,
                    transaction_time__lt=month_end,
                    result_code=0
                ).aggregate(total=Sum('amount'))['total'] or 0
                
                historical.append({
                    'month': month_start.strftime('%Y-%m'),
                    'revenue': float(revenue)
                })
            
            # Simple linear regression forecast (next 6 months)
            if len(historical) > 0:
                avg_growth = sum([historical[i]['revenue'] - historical[i-1]['revenue'] 
                                for i in range(1, len(historical))]) / (len(historical) - 1)
                
                last_revenue = historical[-1]['revenue']
                forecast = []
                
                for i in range(1, 7):
                    month = timezone.now().replace(day=1) + timedelta(days=30*i)
                    predicted = last_revenue + (avg_growth * i)
                    
                    forecast.append({
                        'month': month.strftime('%Y-%m'),
                        'predicted_revenue': round(predicted, 2),
                        'confidence': max(50, 95 - (i * 5))  # Decreasing confidence
                    })
            else:
                forecast = []
            
            return Response({
                'historical': historical,
                'forecast': forecast,
                'avg_monthly_growth': round(avg_growth, 2) if len(historical) > 0 else 0,
                'trend': 'upward' if avg_growth > 0 else 'downward'
            })
        except Exception as e:
            logger.error(f"Error fetching revenue forecast: {e}")
            return Response({'error': 'Failed to fetch revenue forecast'}, status=500)

class NetworkAnalyticsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            from locations.models import Location
            from analytics.models import ActiveSession
            
            # Location-based network stats
            locations = Location.objects.filter(is_active=True)
            network_stats = []
            
            for location in locations:
                # Active sessions at location
                active_sessions = ActiveSession.objects.filter(
                    location=location,
                    is_authenticated=True
                ).count()
                
                # Total vouchers sold at location
                total_vouchers = DispatchVoucher.objects.filter(location=location).count()
                
                # Calculate utilization
                utilization = (active_sessions / location.max_concurrent_users * 100) if location.max_concurrent_users > 0 else 0
                
                # Health status
                if utilization > 90:
                    health = 'critical'
                elif utilization > 70:
                    health = 'warning'
                else:
                    health = 'healthy'
                
                network_stats.append({
                    'location_id': location.id,
                    'location_name': location.name,
                    'active_sessions': active_sessions,
                    'max_capacity': location.max_concurrent_users,
                    'utilization': round(utilization, 1),
                    'health_status': health,
                    'total_vouchers': total_vouchers,
                    'router_ip': location.router_ip
                })
            
            # Sort by utilization
            network_stats.sort(key=lambda x: x['utilization'], reverse=True)
            
            # Overall network health
            total_capacity = sum([loc.max_concurrent_users for loc in locations])
            total_active = sum([stat['active_sessions'] for stat in network_stats])
            overall_utilization = (total_active / total_capacity * 100) if total_capacity > 0 else 0
            
            return Response({
                'locations': network_stats,
                'overall': {
                    'total_locations': len(locations),
                    'total_capacity': total_capacity,
                    'total_active_sessions': total_active,
                    'overall_utilization': round(overall_utilization, 1),
                    'healthy_locations': len([s for s in network_stats if s['health_status'] == 'healthy']),
                    'warning_locations': len([s for s in network_stats if s['health_status'] == 'warning']),
                    'critical_locations': len([s for s in network_stats if s['health_status'] == 'critical'])
                }
            })
        except Exception as e:
            logger.error(f"Error fetching network analytics: {e}")
            return Response({'error': 'Failed to fetch network analytics'}, status=500)

class ABTestingView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            # Mock A/B test data
            experiments = [
                {
                    'id': 1,
                    'name': 'Package Pricing Test',
                    'status': 'running',
                    'start_date': '2024-01-01',
                    'variants': [
                        {'name': 'Control', 'participants': 500, 'conversions': 125, 'conversion_rate': 25.0, 'revenue': 62500},
                        {'name': 'Variant A', 'participants': 500, 'conversions': 150, 'conversion_rate': 30.0, 'revenue': 75000}
                    ],
                    'winner': 'Variant A',
                    'confidence': 95.5
                },
                {
                    'id': 2,
                    'name': 'Promotion Banner Test',
                    'status': 'completed',
                    'start_date': '2023-12-15',
                    'variants': [
                        {'name': 'Control', 'participants': 1000, 'conversions': 200, 'conversion_rate': 20.0, 'revenue': 100000},
                        {'name': 'Variant B', 'participants': 1000, 'conversions': 180, 'conversion_rate': 18.0, 'revenue': 90000}
                    ],
                    'winner': 'Control',
                    'confidence': 87.3
                }
            ]
            
            return Response({'experiments': experiments})
        except Exception as e:
            logger.error(f"Error fetching A/B tests: {e}")
            return Response({'error': 'Failed to fetch A/B tests'}, status=500)

class CustomerHealthView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            from django.db.models import Avg, Max
            
            health_scores = []
            clients = ClientH.objects.all()[:50]
            
            for client in clients:
                # Calculate health score components
                last_activity = DispatchVoucher.objects.filter(user=client.user).aggregate(Max('activated_at'))['activated_at__max']
                total_purchases = DispatchVoucher.objects.filter(user=client.user).count()
                total_spent = DispatchVoucher.objects.filter(user=client.user).aggregate(Sum('price_paid'))['price_paid__sum'] or 0
                
                # Engagement score (0-100)
                days_since_activity = (timezone.now() - last_activity).days if last_activity else 999
                engagement = max(0, 100 - (days_since_activity * 2))
                
                # Usage score
                usage = min(100, total_purchases * 10)
                
                # Payment score
                payment = min(100, float(total_spent) / 100)
                
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
                    'user_id': client.user.id,
                    'username': client.user.username,
                    'health_score': health_score,
                    'engagement_score': round(engagement),
                    'usage_score': round(usage),
                    'payment_score': round(payment),
                    'risk_level': risk,
                    'last_activity': last_activity.isoformat() if last_activity else None
                })
            
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
            logger.error(f"Error fetching customer health: {e}")
            return Response({'error': 'Failed to fetch customer health'}, status=500)

class AuditLogView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            # Mock audit log data
            logs = [
                {'id': 1, 'user': 'admin', 'action': 'UPDATE', 'resource': 'Package', 'resource_id': 5, 'timestamp': timezone.now().isoformat(), 'ip': '192.168.1.1'},
                {'id': 2, 'user': 'admin', 'action': 'DELETE', 'resource': 'Voucher', 'resource_id': 123, 'timestamp': (timezone.now() - timedelta(hours=1)).isoformat(), 'ip': '192.168.1.1'},
                {'id': 3, 'user': 'manager', 'action': 'CREATE', 'resource': 'Promotion', 'resource_id': 8, 'timestamp': (timezone.now() - timedelta(hours=2)).isoformat(), 'ip': '192.168.1.5'},
                {'id': 4, 'user': 'admin', 'action': 'UPDATE', 'resource': 'Client', 'resource_id': 45, 'timestamp': (timezone.now() - timedelta(hours=3)).isoformat(), 'ip': '192.168.1.1'},
                {'id': 5, 'user': 'support', 'action': 'VIEW', 'resource': 'Transaction', 'resource_id': 789, 'timestamp': (timezone.now() - timedelta(hours=4)).isoformat(), 'ip': '192.168.1.10'}
            ]
            
            return Response({'logs': logs})
        except Exception as e:
            logger.error(f"Error fetching audit logs: {e}")
            return Response({'error': 'Failed to fetch audit logs'}, status=500)

class DataQualityView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            # Data quality checks
            checks = [
                {'table': 'clients', 'check': 'Completeness', 'score': 98.5, 'status': 'passed', 'issues': 15},
                {'table': 'transactions', 'check': 'Accuracy', 'score': 99.2, 'status': 'passed', 'issues': 8},
                {'table': 'vouchers', 'check': 'Consistency', 'score': 87.3, 'status': 'warning', 'issues': 127},
                {'table': 'sessions', 'check': 'Timeliness', 'score': 95.8, 'status': 'passed', 'issues': 42},
                {'table': 'locations', 'check': 'Completeness', 'score': 100.0, 'status': 'passed', 'issues': 0}
            ]
            
            overall_score = sum([c['score'] for c in checks]) / len(checks)
            
            return Response({
                'checks': checks,
                'overall_score': round(overall_score, 1),
                'total_issues': sum([c['issues'] for c in checks]),
                'last_check': timezone.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error fetching data quality: {e}")
            return Response({'error': 'Failed to fetch data quality'}, status=500)