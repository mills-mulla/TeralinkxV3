"""
Reconciliation API Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
from django.utils import timezone
from finance.reconciliation_service import reconcile_payments
from finance.models_reconciliation import ReconciliationJob, ReconciliationMatch


class ReconciliationJobCreateView(APIView):
    """Create or list reconciliation jobs"""
    
    def get(self, request):
        jobs = ReconciliationJob.objects.all().order_by('-created_at')[:20]
        data = [{
            'job_id': j.job_id,
            'status': j.status,
            'period_start': j.period_start.isoformat(),
            'period_end': j.period_end.isoformat(),
            'total_items': j.total_items,
            'matched_items': j.matched_items,
            'auto_match_rate': j.auto_match_rate,
            'average_confidence': j.average_confidence,
            'created_at': j.created_at.isoformat()
        } for j in jobs]
        return Response({'count': len(data), 'results': data})
    
    def post(self, request):
        period_start = request.data.get('period_start')
        period_end = request.data.get('period_end')
        source_items = request.data.get('source_items', [])
        
        if not period_start or not period_end:
            return Response({
                'error': 'period_start and period_end required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Parse dates
        try:
            period_start = datetime.strptime(period_start, '%Y-%m-%d').date()
            period_end = datetime.strptime(period_end, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Process reconciliation
        job = reconcile_payments(
            period_start=period_start,
            period_end=period_end,
            source_items=source_items,
            initiated_by=request.user
        )
        
        return Response({
            'job_id': job.job_id,
            'status': job.status,
            'total_items': job.total_items,
            'matched_items': job.matched_items,
            'review_items': job.review_items,
            'unmatched_items': job.unmatched_items,
            'auto_match_rate': job.auto_match_rate,
            'average_confidence': job.average_confidence
        })


class ReconciliationJobDetailView(APIView):
    """Get reconciliation job details"""
    
    def get(self, request, job_id):
        try:
            job = ReconciliationJob.objects.get(job_id=job_id)
        except ReconciliationJob.DoesNotExist:
            return Response({
                'error': 'Job not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'job_id': job.job_id,
            'status': job.status,
            'period_start': job.period_start.isoformat(),
            'period_end': job.period_end.isoformat(),
            'total_items': job.total_items,
            'matched_items': job.matched_items,
            'review_items': job.review_items,
            'unmatched_items': job.unmatched_items,
            'auto_match_rate': job.auto_match_rate,
            'average_confidence': job.average_confidence,
            'created_at': job.created_at.isoformat(),
            'completed_at': job.completed_at.isoformat() if job.completed_at else None
        })


class ReconciliationReviewQueueView(APIView):
    """Get items needing review"""
    
    def get(self, request):
        job_id = request.query_params.get('job_id')
        
        if job_id:
            try:
                job = ReconciliationJob.objects.get(job_id=job_id)
                matches = ReconciliationMatch.get_review_queue(job=job)
            except ReconciliationJob.DoesNotExist:
                return Response({
                    'error': 'Job not found'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            matches = ReconciliationMatch.get_review_queue()
        
        data = []
        for match in matches[:50]:  # Limit to 50
            transaction = match.transaction
            data.append({
                'id': match.id,
                'source_reference': match.source_reference,
                'source_amount': float(match.source_amount),
                'source_date': match.source_date.isoformat(),
                'source_customer_info': match.source_customer_info,
                'transaction': {
                    'id': transaction.transaction_id if transaction else None,
                    'amount': float(transaction.amount) if transaction else None,
                    'customer': transaction.user.account if transaction and transaction.user else None
                } if transaction else None,
                'confidence_score': match.confidence_score,
                'match_factors': match.match_factors,
                'created_at': match.created_at.isoformat()
            })
        
        return Response({
            'count': len(data),
            'results': data
        })


class ReconciliationMatchApproveView(APIView):
    """Approve reconciliation match"""
    
    def post(self, request, match_id):
        try:
            match = ReconciliationMatch.objects.get(id=match_id)
        except ReconciliationMatch.DoesNotExist:
            return Response({
                'error': 'Match not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        match.approve_match(request.user)
        
        return Response({
            'message': 'Match approved',
            'match_id': match.id,
            'status': match.status
        })


class ReconciliationMatchRejectView(APIView):
    """Reject reconciliation match"""
    
    def post(self, request, match_id):
        try:
            match = ReconciliationMatch.objects.get(id=match_id)
        except ReconciliationMatch.DoesNotExist:
            return Response({
                'error': 'Match not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        notes = request.data.get('notes', '')
        match.reject_match(request.user, notes)
        
        return Response({
            'message': 'Match rejected',
            'match_id': match.id,
            'status': match.status
        })


class ReconciliationStatsView(APIView):
    """Get reconciliation statistics"""
    
    def get(self, request):
        # Last 30 days stats
        cutoff = timezone.now() - timedelta(days=30)
        
        jobs = ReconciliationJob.objects.filter(created_at__gte=cutoff)
        
        total_jobs = jobs.count()
        total_items = sum(j.total_items for j in jobs)
        total_matched = sum(j.matched_items for j in jobs)
        total_review = sum(j.review_items for j in jobs)
        
        avg_auto_match_rate = sum(j.auto_match_rate or 0 for j in jobs) / max(total_jobs, 1)
        
        avg_confidence = sum(j.average_confidence or 0 for j in jobs) / max(total_jobs, 1)
        
        return Response({
            'period': '30_days',
            'total_jobs': total_jobs,
            'total_items': total_items,
            'total_matched': total_matched,
            'total_review': total_review,
            'avg_auto_match_rate': round(avg_auto_match_rate, 2),
            'avg_confidence': round(avg_confidence, 2),
            'pending_review': ReconciliationMatch.get_review_queue().count()
        })
