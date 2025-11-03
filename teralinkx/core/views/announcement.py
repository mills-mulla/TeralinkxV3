# File: views/announcement.py
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from ..models import Announce
from ..serializers.announcement_serializer import AnnounceSerializer

class AnnouncementView(APIView):
    def get(self, request):
        now = timezone.now()
        announcements = Announce.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).order_by('-priority', '-created_at')
        serializer = AnnounceSerializer(announcements, many=True)
        return Response(serializer.data)