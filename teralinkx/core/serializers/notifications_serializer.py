from rest_framework import serializers
from ..models import Message, Room

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'room', 'sender', 'message', 'time']

class RoomSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='room_name')  # Accept 'name' in API but map to 'room_name'

    class Meta:
        model = Room
        fields = ['name']