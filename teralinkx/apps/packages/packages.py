# File: package.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import PackageType
from core.serializers.package_serializer import PackageTypeSerializer

class PackageAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Regular users can view
    
    def get(self, request):
        """Get all packages - accessible to authenticated users"""
        packages = PackageType.objects.filter(is_active=True, is_public=True)
        serializer = PackageTypeSerializer(packages, many=True)
        return Response({
            'count': packages.count(),
            'packages': serializer.data
        })

class PackageCreateAPIView(APIView):
    permission_classes = [IsAdminUser]  # Only admins can create
    
    def post(self, request):
        """Create new package - ADMIN ONLY"""
        serializer = PackageTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Package created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)