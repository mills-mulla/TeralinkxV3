from rest_framework import serializers
from ..models import Announce

class AnnounceSerializer(serializers.ModelSerializer):
    """Serializer for Announce model with formatted datetime fields"""
    class Meta:
        model = Announce
        fields = [
            'id', 
            'title', 
            'content', 
            'start_date', 
            'end_date', 
            'is_active', 
            'priority', 
            'created_at', 
            'updated_at'
        ]
