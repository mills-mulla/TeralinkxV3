# api/views/clientsview.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Q, F
from django.utils import timezone
from core.models import ClientH, DispatchVoucher
from ..serializers.serializers import ClientSerializer, EligibleClientSerializer
import logging

logger = logging.getLogger(__name__)

class ClientViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = ClientH.objects.all().select_related('user')
    serializer_class = ClientSerializer
    
    @action(detail=False, methods=['get'])
    def eligible_for_refund(self, request):
        """Get clients eligible for refund (not expired and usage not exhausted)"""
        try:
            eligible_clients = DispatchVoucher.objects.filter(
                Q(dispatch_expiry__isnull=True) | Q(dispatch_expiry__gt=timezone.now()),
                Q(usage_limit__isnull=True) | 
                Q(total_download__lt=F('usage_limit') - F('total_upload'))
            ).select_related('clienth__user')
            
            serializer = EligibleClientSerializer(eligible_clients, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error fetching eligible clients: {e}")
            return Response(
                {'error': 'Failed to fetch eligible clients'}, 
                status=500
            )