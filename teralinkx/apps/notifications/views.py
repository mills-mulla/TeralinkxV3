# apps/notifications/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q

from .models import Notification


class MarkNotificationReadView(APIView):
    """Mark a notification as read"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, notification_id):
        try:
            user = request.user
            
            # Get the notification
            notification = Notification.objects.filter(
                id=notification_id,
                user=user
            ).first()
            
            if not notification:
                return Response(
                    {"error": "Notification not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Mark as read
            notification.mark_as_read()
            
            return Response(
                {"message": "Notification marked as read"},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {"error": "Failed to mark notification as read", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AnnouncementListView(APIView):
    """Get active announcements"""
    
    def get(self, request):
        from django.core.cache import cache
        
        try:
            # Check cache first (5 minute cache)
            cache_key = 'global_announcements'
            cached = cache.get(cache_key)
            
            if cached:
                return Response(cached, status=status.HTTP_200_OK)
            
            now = timezone.now()
            
            # Optimized query - only fetch needed fields
            announcements = Notification.objects.filter(
                scope='global',
                is_archived=False
            ).filter(
                Q(expires_at__isnull=True) | Q(expires_at__gt=now)
            ).only(
                'id', 'title', 'message', 'priority',
                'notification_type', 'scope', 'created_at',
                'expires_at', 'action_url', 'action_text'
            ).order_by('-priority', '-created_at')[:10]
            
            # Serialize announcements
            data = [{
                'id': a.id,
                'title': a.title or '',
                'message': a.message or '',
                'content': a.message or '',
                'priority': a.priority or 'medium',
                'notification_type': a.notification_type,
                'scope': a.scope or 'global',
                'created_at': a.created_at.isoformat() if a.created_at else None,
                'expires_at': a.expires_at.isoformat() if a.expires_at else None,
                'action_url': a.action_url or '',
                'action_text': a.action_text or '',
                'is_active': True,
            } for a in announcements]
            
            # Cache for 5 minutes
            cache.set(cache_key, data, 300)
            
            return Response(data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": "Failed to fetch announcements", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PublicAnnouncementListView(APIView):
    """Get public announcements (no auth required)"""
    permission_classes = []
    
    def get(self, request):
        try:
            now = timezone.now()
            
            # Only show global maintenance/system/security announcements
            announcements = Notification.objects.filter(
                scope='global',
                notification_type__in=['maintenance', 'system', 'security'],
                is_archived=False
            ).filter(
                Q(expires_at__isnull=True) | Q(expires_at__gt=now)
            ).order_by('-priority', '-created_at')[:5]
            
            data = [{
                'id': a.id,
                'title': a.title or '',
                'message': a.message or '',
                'priority': a.priority or 'medium',
                'notification_type': a.notification_type,
                'scope': 'global',
                'created_at': a.created_at.isoformat() if a.created_at else None,
                'expires_at': a.expires_at.isoformat() if a.expires_at else None,
            } for a in announcements]
            
            return Response(data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response([], status=status.HTTP_200_OK)
