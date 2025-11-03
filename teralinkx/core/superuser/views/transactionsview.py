# api/views/transactionsview.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Q
from core.models import Transaction
from ..serializers.serializers import TransactionSerializer 

class TransactionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    
    def get_queryset(self):
        queryset = Transaction.objects.all()
        
        # Search functionality
        search_term = self.request.query_params.get('search', None)
        if search_term:
            queryset = queryset.filter(
                Q(transaction_id__icontains=search_term) |
                Q(initiator__icontains=search_term) |
                Q(result_desc__icontains=search_term)
            )
        
        return queryset.order_by('-transaction_time')