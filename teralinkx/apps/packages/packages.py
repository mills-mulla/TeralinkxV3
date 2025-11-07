# File: views/package.py
from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import Package
from ..serializers.package_serializer import PackageSerializer

class PackageAPIView(APIView):
    def post(self, request):
        package_data = request.data
        new_package = Package.objects.create(
            package=package_data.get('package'),
            price=package_data.get('price'),
            package_desc=package_data.get('package_desc'),
            package_duration=package_data.get('package_duration')
        )
        return Response({'message': 'Package created successfully'})

    def get(self, request):
        packages = Package.objects.all()
        serializer = PackageSerializer(packages, many=True)
        return Response(serializer.data)