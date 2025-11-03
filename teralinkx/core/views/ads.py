# ads/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import Advertisement
from ..serializers.AdvertisementSerializer import AdvertisementSerializer

class ActiveAdsAPIView(APIView):
    def get(self, request):
        ads = Advertisement.objects.filter(active=True).order_by('-created_at')
        serializer = AdvertisementSerializer(ads, many=True, context={'request': request})
        return Response(serializer.data)
