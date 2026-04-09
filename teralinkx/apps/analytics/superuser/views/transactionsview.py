# api/views/transactionsview.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Q, Sum, Count, Avg
from finance.models import PaymentTransaction, BalanceTransaction, TransactionQueue
from packages.models import PointTransaction
from ..serializers.transaction_serializers import (
    PaymentTransactionSerializer,
    BalanceTransactionSerializer,
    TransactionQueueSerializer,
    PointTransactionSerializer
)
import logging

logger = logging.getLogger(__name__)


class PaymentTransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for Payment Transactions"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = PaymentTransaction.objects.all()
    serializer_class = PaymentTransactionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['transaction_id', 'initiator', 'result_desc']
    ordering_fields = ['id', 'created_at', 'amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by payment method
        method = self.request.query_params.get('payment_method', None)
        if method:
            queryset = queryset.filter(payment_method=method)
        
        return queryset


class BalanceTransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for Balance Transactions"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = BalanceTransaction.objects.all()
    serializer_class = BalanceTransactionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__account', 'description', 'reference']
    ordering_fields = ['id', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by transaction type
        txn_type = self.request.query_params.get('transaction_type', None)
        if txn_type:
            queryset = queryset.filter(transaction_type=txn_type)
        
        return queryset


class TransactionQueueViewSet(viewsets.ModelViewSet):
    """ViewSet for Transaction Queue"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = TransactionQueue.objects.all()
    serializer_class = TransactionQueueSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['initiator', 'package', 'checkout_request_id']
    ordering_fields = ['id', 'created_at', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by queue type
        queue_type = self.request.query_params.get('queue_type', None)
        if queue_type:
            queryset = queryset.filter(queue_type=queue_type)
        
        return queryset


class PointTransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for Point Transactions"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = PointTransaction.objects.all()
    serializer_class = PointTransactionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__account', 'description']
    ordering_fields = ['id', 'created_at', 'points']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by transaction type
        txn_type = self.request.query_params.get('transaction_type', None)
        if txn_type:
            queryset = queryset.filter(transaction_type=txn_type)
        
        return queryset


class TransactionStatsViewSet(viewsets.ViewSet):
    """Combined transaction statistics"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get comprehensive transaction statistics"""
        try:
            # Payment transaction stats
            payment_stats = PaymentTransaction.objects.aggregate(
                total_revenue=Sum('amount_base'),
                completed_count=Count('id', filter=Q(status='completed')),
                avg_transaction=Avg('amount_base')
            )
            
            # Queue stats
            queue_stats = TransactionQueue.objects.aggregate(
                pending_count=Count('id', filter=Q(status='pending')),
                processing_count=Count('id', filter=Q(status='processing')),
                failed_count=Count('id', filter=Q(status='failed')),
                completed_count=Count('id', filter=Q(status='completed'))
            )
            
            # Balance transaction stats
            balance_stats = BalanceTransaction.objects.aggregate(
                total_credits=Sum('credit'),
                total_debits=Sum('debit'),
                transaction_count=Count('id')
            )
            
            # Point transaction stats
            point_stats = PointTransaction.objects.aggregate(
                total_points_earned=Sum('points', filter=Q(points__gt=0)),
                total_points_spent=Sum('points', filter=Q(points__lt=0)),
                transaction_count=Count('id')
            )
            
            return Response({
                'total_revenue': payment_stats['total_revenue'] or 0,
                'completed_count': payment_stats['completed_count'] or 0,
                'pending_count': queue_stats['pending_count'] or 0,
                'failed_count': queue_stats['failed_count'] or 0,
                'avg_transaction': payment_stats['avg_transaction'] or 0,
                'balance_credits': balance_stats['total_credits'] or 0,
                'balance_debits': balance_stats['total_debits'] or 0,
                'points_earned': point_stats['total_points_earned'] or 0,
                'points_spent': abs(point_stats['total_points_spent'] or 0)
            })
        except Exception as e:
            logger.error(f"Error fetching transaction stats: {e}")
            return Response({'error': str(e)}, status=500)


# Legacy compatibility
class TransactionViewSet(PaymentTransactionViewSet):
    """Legacy transaction viewset - redirects to PaymentTransactionViewSet"""
    pass