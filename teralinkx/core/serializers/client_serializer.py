from rest_framework import serializers
from ..models import ClientH

class ClientSerializer(serializers.ModelSerializer):
    current_mac = serializers.CharField()
    current_ip = serializers.CharField()
    phone = serializers.CharField()


    class Meta:
        model = ClientH
        fields = ['phone', 'current_ip', 'current_mac']
