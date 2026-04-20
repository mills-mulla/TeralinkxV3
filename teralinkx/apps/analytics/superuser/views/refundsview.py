# api/views/refundsview.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Q, F, Sum, Count
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
import logging
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from analytics.models import RefundLog, DowntimeRecord
from packages.models import DispatchVoucher
from users.models import ClientH
from ..serializers.serializers import RefundLogSerializer, DowntimeRecordSerializer

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class RefundViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = RefundLog.objects.all()
    serializer_class = RefundLogSerializer
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get refund statistics"""
        try:
            total_refunded = RefundLog.objects.aggregate(
                total=Sum('refund_amount')
            )['total'] or 0
            
            eligible_clients = self.get_eligible_clients().count()
            
            pending_refunds = DispatchVoucher.objects.filter(
                Q(dispatch_expiry__isnull=True) | Q(dispatch_expiry__gt=timezone.now()),
                Q(usage_limit__isnull=True) | 
                Q(total_download__lt=F('usage_limit') - F('total_upload'))
            ).count()
            
            avg_refund = RefundLog.objects.aggregate(
                avg=Sum('refund_amount') / Count('id')
            )['avg'] or 0
            
            return Response({
                'eligible_clients': eligible_clients,
                'total_refunded': float(total_refunded),
                'pending_refunds': pending_refunds,
                'average_refund': float(avg_refund)
            })
            
        except Exception as e:
            logger.error(f"Error fetching refund stats: {e}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def eligible_clients(self, request):
        """Get all eligible clients for refund"""
        try:
            clients = self.get_eligible_clients()
            
            client_data = []
            for client in clients:
                # Find the related ClientH by account number
                clienth = None
                username = 'N/A'
                current_balance = 0.0
                email = 'N/A'
                status = 'unknown'
                
                try:
                    # Look up ClientH by account number
                    clienth = ClientH.objects.filter(account=client.dispatch_account).first()
                    if clienth:
                        username = clienth.user.username if clienth.user else 'N/A'
                        current_balance = float(clienth.balance) if clienth.balance else 0.0
                        email = clienth.user.email if clienth and clienth.user else 'N/A'
                        status = clienth.status if clienth.status else 'unknown'
                except Exception as e:
                    logger.warning(f"Error fetching ClientH for {client.dispatch_account}: {e}")
                
                client_data.append({
                    'dispatch_account': client.dispatch_account,
                    'username': username,
                    'dispatch_price': float(client.dispatch_price),
                    'dispatch_package_duration': client.dispatch_package_duration,
                    'current_balance': current_balance,
                    'usage_limit': float(client.usage_limit) if client.usage_limit else None,
                    'total_download': float(client.total_download) if client.total_download else 0.0,
                    'total_upload': float(client.total_upload) if client.total_upload else 0.0,
                    'dispatch_expiry': client.dispatch_expiry,
                    'status': status
                })
            
            return Response(client_data)
            
        except Exception as e:
            logger.error(f"Error fetching eligible clients: {e}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def client_details(self, request, account=None):
        """Get detailed information for a specific client"""
        try:
            client = DispatchVoucher.objects.filter(dispatch_account=account).first()
            if not client:
                return Response(
                    {'error': 'Client not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Find the related ClientH by account number
            clienth = None
            username = 'N/A'
            current_balance = 0.0
            email = 'N/A'
            status = 'unknown'
            
            try:
                clienth = ClientH.objects.filter(account=account).first()
                if clienth:
                    username = clienth.user.username if clienth.user else 'N/A'
                    current_balance = float(clienth.balance) if clienth.balance else 0.0
                    email = clienth.user.email if clienth.user else 'N/A'
                    status = clienth.status if clienth.status else 'unknown'
            except Exception as e:
                logger.warning(f"Error fetching ClientH for {account}: {e}")
            
            client_data = {
                'dispatch_account': client.dispatch_account,
                'username': username,
                'email': email,
                'dispatch_price': float(client.dispatch_price),
                'dispatch_package_duration': client.dispatch_package_duration,
                'current_balance': current_balance,
                'usage_limit': float(client.usage_limit) if client.usage_limit else None,
                'total_download': float(client.total_download) if client.total_download else 0.0,
                'total_upload': float(client.total_upload) if client.total_upload else 0.0,
                'dispatch_expiry': client.dispatch_expiry,
                'status': status
            }
            
            return Response(client_data)
            
        except Exception as e:
            logger.error(f"Error fetching client details: {e}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def preview(self, request):
        """Preview refund amount without processing — keeps frontend fast."""
        try:
            account = request.data.get('account')
            downtime_minutes = int(request.data.get('downtime_minutes', 0))
            if not account or downtime_minutes <= 0:
                return Response({'error': 'account and downtime_minutes required'},
                                status=status.HTTP_400_BAD_REQUEST)
            client = DispatchVoucher.objects.filter(dispatch_account=account).first()
            if not client:
                return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
            if not self.is_client_eligible(client):
                return Response({'eligible': False, 'error': 'Client not eligible'},
                                status=status.HTTP_400_BAD_REQUEST)
            amount = self.calculate_refund_amount(client, downtime_minutes)
            clienth = ClientH.objects.filter(account=account).first()
            return Response({
                'account': account,
                'username': clienth.user.username if clienth and clienth.user else account,
                'downtime_minutes': downtime_minutes,
                'refund_amount': float(amount),
                'package_price': float(client.dispatch_price),
                'duration': client.dispatch_package_duration,
                'eligible': True,
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def process_individual(self, request):
        """Process individual refund"""
        try:
            account = request.data.get('account')
            downtime_minutes = int(request.data.get('downtime_minutes', 0))
            refund_type = request.data.get('refund_type', 'individual')
            
            if not account or downtime_minutes <= 0:
                return Response(
                    {'error': 'Account and valid downtime minutes are required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get client details
            client = DispatchVoucher.objects.filter(dispatch_account=account).first()
            if not client:
                return Response(
                    {'error': 'Client not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check eligibility
            if not self.is_client_eligible(client):
                return Response(
                    {'error': 'Client is not eligible for refund'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Find the ClientH
            clienth = ClientH.objects.filter(account=account).first()
            if not clienth:
                return Response(
                    {'error': 'ClientH record not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Calculate refund amount
            refund_amount = self.calculate_refund_amount(client, downtime_minutes)
            
            if refund_amount > 0:
                with transaction.atomic():
                    # Update client balance
                    clienth.balance += refund_amount
                    clienth.save()
                    
                    # Log the refund
                    RefundLog.objects.create(
                        account=account,
                        refund_amount=refund_amount,
                        downtime_minutes=downtime_minutes,
                        refund_type=refund_type
                    )
                
                return Response({
                    'success': True,
                    'refund_amount': float(refund_amount),
                    'message': f'Refund processed successfully for {account}'
                })
            else:
                return Response({
                    'success': True,
                    'refund_amount': 0,
                    'message': 'No refund applicable for this downtime period'
                })
                
        except Exception as e:
            logger.error(f"Error processing individual refund: {e}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def batch_refund(self, request):
        """Process batch refund for all eligible clients"""
        try:
            downtime_minutes = int(request.data.get('downtime_minutes', 0))
            
            if downtime_minutes <= 0:
                return Response(
                    {'error': 'Valid downtime minutes are required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            eligible_clients = self.get_eligible_clients()
            results = []
            total_refunded = 0
            
            with transaction.atomic():
                for client in eligible_clients:
                    refund_amount = self.calculate_refund_amount(client, downtime_minutes)
                    
                    # Find the ClientH for this dispatch account
                    clienth = ClientH.objects.filter(account=client.dispatch_account).first()
                    username = clienth.user.username if clienth and clienth.user else 'N/A'
                    
                    if refund_amount > 0 and clienth:
                        # Update client balance
                        clienth.balance += refund_amount
                        clienth.save()
                        
                        # Log refund
                        RefundLog.objects.create(
                            account=client.dispatch_account,
                            refund_amount=refund_amount,
                            downtime_minutes=downtime_minutes,
                            refund_type='batch'
                        )
                        
                        total_refunded += refund_amount
                        results.append({
                            'account': client.dispatch_account,
                            'username': username,
                            'refund_amount': float(refund_amount),
                            'status': '✅ Success'
                        })
                    else:
                        status_msg = '⚠️ No refund applicable' if refund_amount == 0 else '❌ ClientH not found'
                        results.append({
                            'account': client.dispatch_account,
                            'username': username,
                            'refund_amount': 0,
                            'status': status_msg
                        })
            
            return Response({
                'success': True,
                'total_refunded': float(total_refunded),
                'processed_count': len(results),
                'results': results
            })
            
        except Exception as e:
            logger.error(f"Error processing batch refund: {e}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get refund history"""
        try:
            limit = int(request.GET.get('limit', 50))
            refunds = RefundLog.objects.all().order_by('-created_at')[:limit]
            
            serializer = self.get_serializer(refunds, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error fetching refund history: {e}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def recent_downtimes(self, request):
        """Get recent downtime records"""
        try:
            limit = int(request.GET.get('limit', 10))
            downtimes = DowntimeRecord.objects.all().order_by('-start_time')[:limit]
            
            serializer = DowntimeRecordSerializer(downtimes, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error fetching recent downtimes: {e}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def record_downtime(self, request):
        """Record a new downtime occurrence"""
        try:
            serializer = DowntimeRecordSerializer(data=request.data)
            if serializer.is_valid():
                downtime = serializer.save()
                return Response({
                    'success': True,
                    'message': 'Downtime recorded successfully',
                    'downtime_id': downtime.id
                })
            else:
                return Response(
                    {'error': serializer.errors}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Error recording downtime: {e}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Helper methods
    def get_eligible_clients(self):
        """Get all eligible clients for refund"""
        # Remove select_related since there's no direct relationship
        return DispatchVoucher.objects.filter(
            Q(dispatch_expiry__isnull=True) | Q(dispatch_expiry__gt=timezone.now()),
            Q(usage_limit__isnull=True) | 
            Q(total_download__lt=F('usage_limit') - F('total_upload'))
        )
    
    def is_client_eligible(self, client):
        """Check if a client is eligible for refund"""
        if client.dispatch_expiry and client.dispatch_expiry < timezone.now():
            return False
        
        if client.usage_limit:
            total_usage = (client.total_download or 0) + (client.total_upload or 0)
            if total_usage >= client.usage_limit:
                return False
        
        return True
    
    def calculate_refund_amount(self, client, downtime_minutes):
        """Calculate refund amount based on business logic"""
        MIN_DOWNTIME_FOR_REFUND = 10
        EXTRA_REFUND_THRESHOLD = 15
        EXTRA_REFUND_PERCENTAGE = 0.2
        
        if downtime_minutes < MIN_DOWNTIME_FOR_REFUND:
            return 0
        
        package_price = float(client.dispatch_price)
        duration_str = client.dispatch_package_duration
        usage_limit = float(client.usage_limit) if client.usage_limit else None
        total_download = float(client.total_download) if client.total_download else 0
        total_upload = float(client.total_upload) if client.total_upload else 0
        
        # Parse duration
        days = self._extract_days_from_duration(duration_str)
        total_usage = total_download + total_upload
        
        if usage_limit is not None:
            # LIMITED USAGE PACKAGE: Refund based on unused portion
            unused_percentage = 1 - (total_usage / usage_limit)
            unused_percentage = max(0, min(1, unused_percentage))
            
            effective_package_value = package_price * unused_percentage
            total_minutes = 60 * 24 * days
            downtime_ratio = downtime_minutes / total_minutes
            
            refund_amount = effective_package_value * downtime_ratio
        else:
            # UNLIMITED USAGE PACKAGE: Refund based on cost per minute
            if days <= 1:
                refund_per_minute = package_price / 60
                refund_amount = refund_per_minute * downtime_minutes
            else:
                total_minutes = 60 * 24 * days
                refund_per_minute = package_price / total_minutes
                refund_amount = refund_per_minute * downtime_minutes
        
        # Apply extra refund for extended downtime
        if downtime_minutes > EXTRA_REFUND_THRESHOLD:
            additional_refund = max(0, refund_amount * EXTRA_REFUND_PERCENTAGE)
            refund_amount += additional_refund
        
        # Round to nearest whole number with minimum 1 KES
        final_amount = max(1, round(refund_amount))
        
        return final_amount
    
    def _extract_days_from_duration(self, duration_str):
        """Extract number of days from duration string"""
        try:
            if duration_str:
                if 'day' in str(duration_str):
                    days_str = str(duration_str).split(' day')[0]
                    return int(days_str) if days_str.strip().isdigit() else 1
                else:
                    return 1
            else:
                return 30
        except:
            return 30