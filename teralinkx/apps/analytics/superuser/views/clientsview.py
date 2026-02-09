from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from users.models import ClientH
from ..serializers.serializers import ClientSerializer
import logging

logger = logging.getLogger(__name__)

class ClientViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = ClientH.objects.all().select_related('user')
    serializer_class = ClientSerializer