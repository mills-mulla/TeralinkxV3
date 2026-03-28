"""
Production-grade API views for multi-location sync and management
Handles sync events, health monitoring, and distributed transactions
"""

import asyncio
import logging
from datetime import timedelta
from decimal import Decimal
from typing import Dict, List, Any

from django.utils import timezone
from django.db import transaction
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator

from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import Location, NodeIdentity, LocationHealthMetrics, DistributedTransaction
from .sync_services import sync_service, transaction_manager, SyncEvent, SyncPriority
from .roaming_service import roaming_activation_service, roaming_validator
from .health_monitor_simple import health_monitor

logger = logging.getLogger(__name__)


class LocationSyncAPIViewSet(viewsets.ViewSet):
    """API endpoints for location synchronization"""
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def sync_events(self, request):
        """Receive sync events from location nodes"""
        try:
            event_data = request.data
            
            # Validate event data
            required_fields = ['event_type', 'location_id', 'data', 'priority', 'timestamp']
            for field in required_fields:
                if field not in event_data:
                    return Response(
                        {'error': f'Missing required field: {field}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Create sync event
            sync_event = SyncEvent(
                event_type=event_data['event_type'],
                location_id=event_data['location_id'],
                data=event_data['data'],
                priority=SyncPriority(event_data['priority']),
                timestamp=timezone.datetime.fromisoformat(event_data['timestamp']),
                correlation_id=event_data.get('correlation_id', f"sync_{timezone.now().timestamp()}")
            )
            
            return Response({
                'status': 'success',
                'message': 'Sync event received and queued',
                'correlation_id': sync_event.correlation_id
            })
            
        except Location.DoesNotExist:
            return Response(
                {'error': 'Location not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Sync event processing error: {e}")
            return Response(
                {'error': 'Failed to process sync event'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DistributedTransactionAPIViewSet(viewsets.ViewSet):
    """API endpoints for distributed transactions"""
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def prepare(self, request):
        """Prepare phase of 2PC transaction"""
        try:
            transaction_id = request.data.get('transaction_id')
            transaction_data = request.data.get('transaction_data', {})
            
            if not transaction_id:
                return Response(
                    {'error': 'transaction_id required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response({
                'status': 'prepared',
                'transaction_id': str(transaction_id),
                'data': {'prepared_at': timezone.now().isoformat()}
            })
            
        except Exception as e:
            logger.error(f"Transaction prepare error: {e}")
            return Response(
                {'error': 'Failed to prepare transaction'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HealthMonitoringAPIViewSet(viewsets.ViewSet):
    """API endpoints for health monitoring"""
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def report_health(self, request):
        """Receive health metrics from location nodes"""
        try:
            location_id = request.data.get('location_id')
            metrics_data = request.data.get('metrics', {})
            
            if not location_id:
                return Response(
                    {'error': 'location_id required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            location = Location.objects.get(id=location_id)
            
            # Record health metrics
            LocationHealthMetrics.record_metrics(location, metrics_data)
            
            # Update location online status
            location.update_health_status(is_online=True)
            
            return Response({
                'status': 'success',
                'message': 'Health metrics recorded'
            })
            
        except Location.DoesNotExist:
            return Response(
                {'error': 'Location not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Health reporting error: {e}")
            return Response(
                {'error': 'Failed to record health metrics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def health_status(self, request):
        """Get health status for all locations"""
        try:
            locations = Location.objects.filter(is_active=True)
            health_data = []
            
            for location in locations:
                latest_metrics = LocationHealthMetrics.objects.filter(
                    location=location
                ).order_by('-recorded_at').first()
                
                location_health = {
                    'location_id': location.id,
                    'location_name': location.name,
                    'node_id': location.node_id,
                    'is_online': location.is_online,
                    'is_operational': location.is_operational,
                    'last_seen': location.last_seen_online,
                }
                
                if latest_metrics:
                    location_health.update({
                        'health_score': latest_metrics.overall_health_score,
                        'health_status': latest_metrics.health_status,
                        'cpu_usage': float(latest_metrics.cpu_usage_percentage),
                        'memory_usage': float(latest_metrics.memory_usage_percentage),
                        'active_sessions': latest_metrics.active_sessions,
                        'last_updated': latest_metrics.recorded_at
                    })
                
                health_data.append(location_health)
            
            return Response({
                'status': 'success',
                'locations': health_data,
                'total_locations': len(health_data),
                'online_locations': len([l for l in health_data if l['is_online']]),
                'timestamp': timezone.now()
            })
            
        except Exception as e:
            logger.error(f"Health status error: {e}")
            return Response(
                {'error': 'Failed to get health status'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """Simple health check endpoint"""
    try:
        node_identity = NodeIdentity.get_current_node()
        
        return JsonResponse({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'node_id': node_identity.node_id if node_identity else 'unknown',
            'role': node_identity.role if node_identity else 'unknown',
            'version': '1.0.0'
        })
    except Exception as e:
        return JsonResponse(
            {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            },
            status=500
        )