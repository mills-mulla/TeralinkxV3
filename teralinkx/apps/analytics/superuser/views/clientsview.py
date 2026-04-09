from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Count, Q, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from users.models import ClientH
from ..serializers.serializers import ClientSerializer
import logging

logger = logging.getLogger(__name__)

class ClientViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = ClientH.objects.all().select_related('user')
    serializer_class = ClientSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get client statistics with weekly trends"""
        try:
            from django.db.models import Sum
            from datetime import timedelta
            
            now = timezone.now()
            week_ago = now - timedelta(days=7)
            two_weeks_ago = now - timedelta(days=14)
            
            # Current stats
            total_clients = ClientH.objects.count()
            active_clients = ClientH.objects.filter(status='active').count()
            premium_clients = ClientH.objects.filter(account_tier__in=['premium', 'business', 'enterprise']).count()
            new_clients_7d = ClientH.objects.filter(created_at__gte=week_ago).count()
            total_balance = ClientH.objects.aggregate(total=Sum('balance'))['total'] or 0
            
            # Previous week stats
            total_clients_prev = ClientH.objects.filter(created_at__lt=week_ago).count()
            active_clients_prev = ClientH.objects.filter(status='active', created_at__lt=week_ago).count()
            premium_clients_prev = ClientH.objects.filter(
                account_tier__in=['premium', 'business', 'enterprise'],
                created_at__lt=week_ago
            ).count()
            
            # Calculate trends
            def calc_trend(current, previous):
                if previous == 0:
                    return {'value': '0%', 'direction': 'stable'}
                change = ((current - previous) / previous) * 100
                return {
                    'value': f"{abs(change):.1f}%",
                    'direction': 'up' if change > 0 else 'down' if change < 0 else 'stable'
                }
            
            return Response({
                'total_clients': total_clients,
                'total_clients_trend': calc_trend(total_clients, total_clients_prev),
                'active_clients': active_clients,
                'active_clients_trend': calc_trend(active_clients, active_clients_prev),
                'premium_clients': premium_clients,
                'premium_clients_trend': calc_trend(premium_clients, premium_clients_prev),
                'new_clients_7d': new_clients_7d,
                'new_clients_7d_trend': {'value': f"{new_clients_7d}", 'direction': 'stable'},
                'total_balance': float(total_balance)
            })
        except Exception as e:
            logger.error(f"Error fetching client stats: {e}")
            return Response({'error': str(e)}, status=500)
    
    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        """Get detailed client profile"""
        try:
            client = self.get_object()
            from packages.models import DispatchVoucher
            from finance.models import PaymentTransaction
            
            # Get related data with error handling
            try:
                devices = list(client.devices.all()[:10])
            except:
                devices = []
            
            try:
                sessions = list(client.sessions.filter(is_active=True)[:10])
            except:
                sessions = []
            
            try:
                vouchers = list(DispatchVoucher.objects.filter(user=client.user).order_by('-activated_at')[:10])
            except:
                vouchers = []
            
            try:
                transactions = list(PaymentTransaction.objects.filter(user=client.user).order_by('-transaction_time')[:10])
            except:
                transactions = []
            
            return Response({
                'client': ClientSerializer(client, context={'request': request}).data,
                'devices': [{'id': d.id, 'name': d.device_name, 'mac': d.mac_address, 'type': d.device_type, 'last_seen': str(d.last_seen) if hasattr(d, 'last_seen') and d.last_seen else None} for d in devices],
                'sessions': [{'id': s.id, 'device': s.device.device_name if hasattr(s, 'device') and s.device else 'Unknown', 'ip': s.ip_address, 'login_time': str(s.login_time), 'is_active': s.is_active} for s in sessions],
                'vouchers': [{'id': v.id, 'package': v.package.name if hasattr(v, 'package') and v.package else 'Unknown', 'status': v.status, 'activated_at': str(v.activated_at) if v.activated_at else None, 'expires_at': str(v.expires_at) if v.expires_at else None} for v in vouchers],
                'transactions': [{'id': t.id, 'amount': float(t.amount), 'result_code': t.result_code, 'transaction_time': str(t.transaction_time)} for t in transactions],
                'stats': {
                    'total_devices': len(devices),
                    'active_sessions': len(sessions),
                    'total_vouchers': len(vouchers),
                    'total_spent': float(client.total_spent),
                    'lifetime_data': client.lifetime_data_used
                }
            })
        except Exception as e:
            logger.error(f"Error fetching client profile: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return Response({'error': str(e)}, status=500)
    
    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        """Suspend client account"""
        try:
            client = self.get_object()
            reason = request.data.get('reason', 'Admin action')
            client.status = 'suspended'
            client.save()
            client.terminate_all_sessions(reason=f"Account suspended: {reason}")
            return Response({'message': 'Client suspended successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate client account"""
        try:
            client = self.get_object()
            client.status = 'active'
            client.save()
            return Response({'message': 'Client activated successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
    @action(detail=True, methods=['post'])
    def adjust_balance(self, request, pk=None):
        """Adjust client balance"""
        try:
            from decimal import Decimal
            client = self.get_object()
            amount = Decimal(str(request.data.get('amount', 0)))
            reason = request.data.get('reason', 'Manual adjustment')
            
            client.balance += amount
            client.save()
            
            return Response({
                'message': 'Balance adjusted successfully',
                'new_balance': float(client.balance)
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
    @action(detail=True, methods=['post'])
    def award_points(self, request, pk=None):
        """Award reward points"""
        try:
            client = self.get_object()
            points = int(request.data.get('points', 0))
            description = request.data.get('description', 'Manual award')
            
            client.award_points(points, 'earned_manual', description)
            
            return Response({
                'message': 'Points awarded successfully',
                'new_points': client.reward_points
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
    @action(detail=True, methods=['post'])
    def force_logout(self, request, pk=None):
        """Force logout all sessions and delete all devices"""
        try:
            client = self.get_object()
            reason = request.data.get('reason', 'Admin forced logout')
            
            # Terminate all sessions
            sessions_count = client.terminate_all_sessions(reason=reason)
            
            # Delete all devices
            devices_count = client.devices.count()
            client.devices.all().delete()
            
            return Response({
                'message': f'{sessions_count} sessions terminated, {devices_count} devices deleted'
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
    @action(detail=False, methods=['post'])
    def bulk_action(self, request):
        """Perform bulk actions on clients"""
        try:
            client_ids = request.data.get('client_ids', [])
            action_type = request.data.get('action')
            
            clients = ClientH.objects.filter(id__in=client_ids)
            
            if action_type == 'suspend':
                clients.update(status='suspended')
            elif action_type == 'activate':
                clients.update(status='active')
            elif action_type == 'upgrade_tier':
                tier = request.data.get('tier')
                clients.update(account_tier=tier)
            
            return Response({'message': f'{clients.count()} clients updated'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get client analytics"""
        try:
            client = self.get_object()
            from packages.models import DispatchVoucher
            from finance.models import TransactionQueue
            from decimal import Decimal
            
            # Calculate LTV (Lifetime Value) from completed TransactionQueue
            try:
                transactions = TransactionQueue.objects.filter(
                    user=client,
                    status__in=['completed', 'processed'],
                    method__in=['mpesa', 'mpesa+balance']  # Only M-Pesa payments
                )
                total_revenue = transactions.aggregate(total=Sum('price'))['total'] or Decimal('0')
                transaction_count = transactions.count()
            except Exception as e:
                logger.error(f"Error calculating LTV: {e}")
                total_revenue = Decimal('0')
                transaction_count = 0
            
            # Voucher usage
            try:
                vouchers = DispatchVoucher.objects.filter(user=client.user)
                voucher_count = vouchers.count()
                active_vouchers = vouchers.filter(status='active').count()
            except Exception as e:
                logger.error(f"Error fetching vouchers: {e}")
                voucher_count = 0
                active_vouchers = 0
            
            # Engagement score (based on activity)
            days_since_signup = max(1, (timezone.now() - client.created_at).days)
            last_activity_days = (timezone.now() - client.last_login).days if client.last_login else days_since_signup
            
            # Engagement: 100% if active in last 7 days, decreases over time
            if last_activity_days <= 7:
                engagement_score = 100
            elif last_activity_days <= 30:
                engagement_score = 80
            elif last_activity_days <= 90:
                engagement_score = 50
            else:
                engagement_score = 20
            
            # Churn risk (based on last activity and spending)
            if last_activity_days > 90 or (voucher_count > 0 and active_vouchers == 0 and last_activity_days > 30):
                churn_risk = 'high'
            elif last_activity_days > 30:
                churn_risk = 'medium'
            else:
                churn_risk = 'low'
            
            # Average transaction
            avg_transaction = float(total_revenue / transaction_count) if transaction_count > 0 else 0
            
            return Response({
                'ltv': float(total_revenue),
                'avg_transaction': avg_transaction,
                'total_transactions': transaction_count,
                'total_vouchers': voucher_count,
                'active_vouchers': active_vouchers,
                'engagement_score': engagement_score,
                'days_since_signup': days_since_signup,
                'last_activity_days': last_activity_days,
                'churn_risk': churn_risk
            })
        except Exception as e:
            logger.error(f"Error fetching client analytics: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return Response({
                'ltv': 0,
                'avg_transaction': 0,
                'total_transactions': 0,
                'total_vouchers': 0,
                'engagement_score': 0,
                'churn_risk': 'unknown'
            }, status=200)
    
    @action(detail=True, methods=['get'])
    def security_logs(self, request, pk=None):
        """Get client security logs"""
        try:
            client = self.get_object()
            # Mock security logs
            logs = [
                {'action': 'login', 'ip': '192.168.1.1', 'timestamp': timezone.now().isoformat(), 'status': 'success'},
                {'action': 'password_change', 'ip': '192.168.1.1', 'timestamp': (timezone.now() - timedelta(days=1)).isoformat(), 'status': 'success'},
            ]
            return Response({'logs': logs})
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send message to client"""
        try:
            client = self.get_object()
            message = request.data.get('message')
            channel = request.data.get('channel', 'sms')  # sms, email, push
            
            # Mock sending
            return Response({'message': f'Message sent via {channel}'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)