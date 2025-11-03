# serializers/AdvertisementSerializer.py

from rest_framework import serializers
from ..models import Advertisement

class AdvertisementSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = Advertisement
        fields = ['id', 'title', 'caption', 'image']
