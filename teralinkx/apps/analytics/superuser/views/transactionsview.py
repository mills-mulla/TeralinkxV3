# api/views/transactionsview.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
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
        p = self.request.query_params
        if p.get('status'):
            queryset = queryset.filter(status=p['status'])
        if p.get('payment_method'):
            queryset = queryset.filter(payment_method=p['payment_method'])
        if p.get('created_at__gte'):
            queryset = queryset.filter(created_at__date__gte=p['created_at__gte'])
        if p.get('created_at__lte'):
            queryset = queryset.filter(created_at__date__lte=p['created_at__lte'])
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
        p = self.request.query_params
        if p.get('transaction_type'):
            queryset = queryset.filter(transaction_type=p['transaction_type'])
        if p.get('created_at__gte'):
            queryset = queryset.filter(created_at__date__gte=p['created_at__gte'])
        if p.get('created_at__lte'):
            queryset = queryset.filter(created_at__date__lte=p['created_at__lte'])
        return queryset


class TransactionQueueViewSet(viewsets.ModelViewSet):
    """ViewSet for Transaction Queue with admin CRUD and M-Pesa query actions."""
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = TransactionQueue.objects.all()
    serializer_class = TransactionQueueSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['initiator', 'package', 'checkout_request_id']
    ordering_fields = ['id', 'created_at', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        p = self.request.query_params
        if p.get('status'):
            queryset = queryset.filter(status=p['status'])
        if p.get('queue_type'):
            queryset = queryset.filter(queue_type=p['queue_type'])
        if p.get('created_at__gte'):
            queryset = queryset.filter(created_at__date__gte=p['created_at__gte'])
        if p.get('created_at__lte'):
            queryset = queryset.filter(created_at__date__lte=p['created_at__lte'])
        return queryset

    @action(detail=False, methods=['get'])
    def failure_analytics(self, request):
        """Return failure breakdown for the analytics tab."""
        days = int(request.query_params.get('days', 30))
        data = TransactionQueue.get_failed_transactions_report(days=days)
        return Response(data)

    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Mark a failed transaction back to pending for retry."""
        if not self._can_edit(request):
            return Response({'error': 'Insufficient permissions'}, status=403)
        txn = self.get_object()
        if txn.status != 'failed':
            return Response({'error': 'Only failed transactions can be retried'}, status=400)
        if txn.retry_count >= txn.max_retries:
            return Response({'error': f'Max retries ({txn.max_retries}) reached'}, status=400)
        success = txn.mark_for_retry()
        if success:
            self._log_audit(request, txn, 'update',
                f'Manual retry by {request.user.username} (attempt {txn.retry_count}/{txn.max_retries})')
            return Response({'id': txn.id, 'status': txn.status, 'retry_count': txn.retry_count})
        return Response({'error': 'Retry not eligible'}, status=400)

    def _can_edit(self, request):
        """superadmin or finance_manager can edit."""
        return (
            request.user.is_superuser or
            request.user.groups.filter(name__in=['finance_manager']).exists()
        )

    def _log_audit(self, request, txn, action, description):
        try:
            from finance.models_medium import AuditLog
            AuditLog.objects.create(
                model_name='TransactionQueue',
                record_id=txn.id,
                action=action,
                changed_by=request.user.username,
                description=description,
            )
        except Exception:
            pass

    @action(detail=True, methods=['post'])
    def query_mpesa(self, request, pk=None):
        """Query M-Pesa for real status of a stuck transaction. finance_manager+."""
        if not self._can_edit(request):
            return Response({'error': 'Insufficient permissions'}, status=403)

        txn = self.get_object()

        if not txn.checkout_request_id:
            return Response({'error': 'No checkout_request_id — cannot query M-Pesa'}, status=400)

        try:
            import json as _json
            from finance.queryDaraja import query_stk_status
            result = query_stk_status(txn.checkout_request_id)
            if hasattr(result, 'content'):
                result = _json.loads(result.content.decode())

            result_code = str(result.get('ResultCode', ''))
            RESULT_MESSAGES = {
                '0':    'Payment confirmed by M-Pesa',
                '4999': 'Still processing on M-Pesa — try again in 30 seconds',
                '1032': 'Cancelled by customer',
                '1037': 'Customer phone unreachable — timed out',
                '2001': 'Wrong M-Pesa PIN',
                '1':    'Insufficient M-Pesa balance',
                '1019': 'Transaction expired',
            }
            message = RESULT_MESSAGES.get(result_code, result.get('ResultDesc', f'Code {result_code}'))

            self._log_audit(request, txn, 'update',
                f'Admin queried M-Pesa: ResultCode={result_code} — {message}')

            if result_code == '0':
                # Credit balance instead of activating voucher
                from finance.tasks import _credit_balance_for_payment
                amount_credited = _credit_balance_for_payment(txn, result, request.user.username)
                return Response({
                    'result_code': result_code,
                    'message': message,
                    'action_taken': f'balance_credited_kes_{amount_credited}',
                    'mpesa_response': result,
                })

            return Response({
                'result_code': result_code,
                'message': message,
                'mpesa_response': result,
            })

        except Exception as e:
            return Response({'error': str(e)}, status=500)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        Manual status override. finance_manager can set completed/failed.
        superadmin can set any status.
        Always requires a reason note.
        """
        if not self._can_edit(request):
            return Response({'error': 'Insufficient permissions'}, status=403)

        txn = self.get_object()
        new_status = request.data.get('status')
        note = request.data.get('note', '').strip()

        if not new_status:
            return Response({'error': 'status is required'}, status=400)
        if not note:
            return Response({'error': 'note is required — document why you are overriding'}, status=400)

        allowed_statuses = ['completed', 'processed', 'failed', 'pending']
        if not request.user.is_superuser:
            allowed_statuses = ['completed', 'processed', 'failed']

        if new_status not in allowed_statuses:
            return Response({'error': f'Cannot set status to {new_status}'}, status=400)

        old_status = txn.status

        if new_status in ('completed', 'processed'):
            txn.status = new_status
            txn.completed_at = timezone.now()
            txn.failure_reason = ''
            txn.save(update_fields=['status', 'completed_at', 'failure_reason'])
        elif new_status == 'failed':
            txn.mark_failed(
                reason=f'[Manual override by {request.user.username}] {note}',
                error_code='ADMIN_OVERRIDE',
                failure_category='admin_action',
                increment_retry=False
            )
            # Refund credit if mixed payment
            from finance.tasks import _refund_credit_if_needed
            _refund_credit_if_needed(txn)
        else:
            txn.status = new_status
            txn.save(update_fields=['status'])

        self._log_audit(request, txn, 'update',
            f'Status changed {old_status} → {new_status} by {request.user.username}. Note: {note}')

        return Response({
            'id': txn.id,
            'old_status': old_status,
            'new_status': txn.status,
            'note': note,
        })


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
        p = self.request.query_params
        if p.get('transaction_type'):
            queryset = queryset.filter(transaction_type=p['transaction_type'])
        if p.get('created_at__gte'):
            queryset = queryset.filter(created_at__date__gte=p['created_at__gte'])
        if p.get('created_at__lte'):
            queryset = queryset.filter(created_at__date__lte=p['created_at__lte'])
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