
from rest_framework import serializers
from ..models import Package


class PackageSerializer(serializers.ModelSerializer):
    """Serializer for Package model including all relevant fields"""
    class Meta:
        model = Package
        fields = [
            'id', 
            'package', 
            'price', 
            'package_desc', 
            'package_duration', 
            'devices'
        ]


