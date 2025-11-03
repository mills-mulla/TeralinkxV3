from rest_framework import serializers
from ..models import DailyPass


class DailyPassSerializer(serializers.ModelSerializer):
    """Serializer for DailyPass model """
    class Meta:
        model = DailyPass
        fields = [
            'id', 
            'package', 
            'price', 
            'package_desc', 
            'package_duration', 
            'devices',
            'banner',
            'limit',
            'status'

        ]