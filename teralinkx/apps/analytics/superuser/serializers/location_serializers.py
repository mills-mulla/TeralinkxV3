# serializers/location_serializers.py
from rest_framework import serializers
from locations.models import Location

class LocationSerializer(serializers.ModelSerializer):
    """Serializer for Location model"""
    client_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Location
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_client_count(self, obj):
        """Get number of clients at this location"""
        return obj.home_users.count()
