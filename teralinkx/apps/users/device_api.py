# apps/users/device_api.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404

from users.models import UserDevice


class DeviceListAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            client = request.user.client_profile
            devices = client.devices.all()
            
            device_data = []
            for device in devices:
                device_data.append({
                    'id': device.id,
                    'device_name': device.device_name,
                    'device_type': device.device_type,
                    'device_manufacturer': device.device_manufacturer,
                    'device_model': device.device_model,
                    'status': device.status,
                    'is_trusted': device.is_trusted,
                    'last_seen': device.last_seen.isoformat() if device.last_seen else None,
                    'total_connections': device.total_connections
                })
            
            return Response(device_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeviceUpdateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, device_id):
        try:
            client = request.user.client_profile
            device = get_object_or_404(UserDevice, id=device_id, user=client)
            
            if 'device_name' in request.data:
                device.device_name = request.data['device_name']
                device.save()
            
            return Response({'success': True}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DeviceBlockAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, device_id):
        try:
            client = request.user.client_profile
            device = get_object_or_404(UserDevice, id=device_id, user=client)
            device.block_device("User blocked via profile")
            
            return Response({'success': True}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DeviceUnblockAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, device_id):
        try:
            client = request.user.client_profile
            device = get_object_or_404(UserDevice, id=device_id, user=client)
            device.unblock_device("User unblocked via profile")
            
            return Response({'success': True}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DeviceTrustAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, device_id):
        try:
            client = request.user.client_profile
            device = get_object_or_404(UserDevice, id=device_id, user=client)
            
            device.is_trusted = request.data.get('is_trusted', False)
            device.save()
            
            return Response({'success': True}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DeviceRemoveAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, device_id):
        try:
            client = request.user.client_profile
            device = get_object_or_404(UserDevice, id=device_id, user=client)
            device.delete()
            
            return Response({'success': True}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)