from rest_framework import serializers
from ..models import DHCPLease

class DHCPLeaseSerializer(serializers.ModelSerializer):
    """Serializer for DHCPLease model including all fields"""
    class Meta:
        model = DHCPLease
        fields = '__all__'