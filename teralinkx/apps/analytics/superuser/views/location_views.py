# views/location_views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Count
from locations.models import Location
from ..serializers.location_serializers import LocationSerializer
import logging

logger = logging.getLogger(__name__)


class LocationViewSet(viewsets.ModelViewSet):
    """ViewSet for Location model"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'address', 'city', 'region']
    ordering_fields = ['id', 'name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by region
        region = self.request.query_params.get('region', None)
        if region:
            queryset = queryset.filter(region=region)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get location statistics"""
        try:
            total_locations = Location.objects.count()
            active_locations = Location.objects.filter(is_active=True).count()
            
            # Locations by region
            by_region = Location.objects.values('region').annotate(
                count=Count('id')
            )
            
            # Top locations by client count
            top_locations = Location.objects.annotate(
                client_count=Count('home_users')
            ).order_by('-client_count')[:10]
            
            return Response({
                'total_locations': total_locations,
                'active_locations': active_locations,
                'by_region': list(by_region),
                'top_locations': LocationSerializer(top_locations, many=True).data
            })
        except Exception as e:
            logger.error(f"Error fetching location stats: {e}")
            return Response({'error': str(e)}, status=500)
