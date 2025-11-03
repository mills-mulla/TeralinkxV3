# core/permissions.py
from rest_framework.permissions import BasePermission
from .models import Room

class IsRoomParticipant(BasePermission):
    """
    Allows access only to users who are participants in the room.
    """

    def has_permission(self, request, view):
        room_name = view.kwargs.get('room_name')
        if not room_name or not request.user.is_authenticated:
            return False

        try:
            room = Room.objects.get(room_name=room_name)
            return request.user in room.participants.all()
        except Room.DoesNotExist:
            return False
