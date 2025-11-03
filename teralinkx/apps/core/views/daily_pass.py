# File: views/daily_pass.py
from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import DailyPass
from ..serializers.dpass_serializer import DailyPassSerializer

class DailyPassAPIView(APIView):
    def post(self, request):
        data = request.data
        new_package = DailyPass.objects.create(
            package=data.get('package'),
            price=data.get('price'),
            package_desc=data.get('package_desc'),
            package_duration=data.get('package_duration')
            
        )
        return Response({'message': 'Package created successfully'})

    def get(self, request):
        packages = DailyPass.objects.all()
        serializer = DailyPassSerializer(packages, many=True)
        return Response(serializer.data)