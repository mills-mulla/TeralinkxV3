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
        try:
            print("DEBUG: Starting announcement fetch")
            now = timezone.now()
            print(f"DEBUG: Current time: {now}")
            
            # Get all global notifications (not just announcements)
            announcements = Notification.objects.filter(
                scope='global',
                is_archived=False
            ).filter(
                Q(expires_at__isnull=True) | Q(expires_at__gt=now)
            ).order_by('-priority', '-created_at')[:10]
            
            print(f"DEBUG: Query: scope=global, is_archived=False, not expired")
            print(f"DEBUG: All notifications count: {Notification.objects.count()}")
            print(f"DEBUG: Global notifications count: {Notification.objects.filter(scope='global').count()}")
            print(f"DEBUG: Non-archived count: {Notification.objects.filter(is_archived=False).count()}")
            
            print(f"DEBUG: Found {announcements.count()} announcements")
            
            # Serialize announcements
            data = []
            for announcement in announcements:
                print(f"DEBUG: Processing announcement {announcement.id}: {announcement.title}")
                try:
                    item = {
                        'id': announcement.id,
                        'title': announcement.title or '',
                        'message': announcement.message or '',
                        'content': announcement.message or '',
                        'priority': announcement.priority or 'medium',
                        'notification_type': announcement.notification_type,
                        'scope': announcement.scope or 'global',
                        'created_at': announcement.created_at.isoformat() if announcement.created_at else None,
                        'expires_at': announcement.expires_at.isoformat() if announcement.expires_at else None,
                        'action_url': announcement.action_url or '',
                        'action_text': announcement.action_text or '',
                        'is_active': True,
                    }
                    data.append(item)
                    print(f"DEBUG: Successfully processed announcement {announcement.id}")
                except Exception as e:
                    print(f"DEBUG: Error processing announcement {announcement.id}: {str(e)}")
                    continue
            
            print(f"DEBUG: Returning {len(data)} announcements")
            return Response(data, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"DEBUG: Exception in AnnouncementListView: {str(e)}")
            import traceback
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
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
