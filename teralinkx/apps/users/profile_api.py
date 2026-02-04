# apps/users/profile_api.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.auth.hashers import make_password
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image
import io
import os

from users.models import ClientH
from security.models import SecurityLog


class ProfileUpdateAPIView(APIView):
    """Update user profile information"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]
    
    def patch(self, request):
        """Update profile fields"""
        try:
            user = request.user
            client = user.client_profile
            
            # Update display name
            if 'display_name' in request.data:
                client.display_name = request.data['display_name']
                print(f"Updated display_name to: {client.display_name}")
            
            # Update password
            if 'password' in request.data and request.data['password']:
                user.password = make_password(request.data['password'])
                user.save()
                print("Updated password")
            
            # Update two-factor authentication (check if field exists)
            if 'two_factor_enabled' in request.data:
                value = request.data['two_factor_enabled']
                if hasattr(client, 'two_factor_enabled'):
                    client.two_factor_enabled = bool(value)
                    print(f"Updated 2FA to: {client.two_factor_enabled}")
            
            # Remove profile image handling from this endpoint
            # Images are now handled by /api/profile/image/
            
            # IMPORTANT: Save the client model
            client.save()
            print("Client saved successfully")
            
            return Response({'success': True}, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error in profile update: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProfileDataAPIView(APIView):
    """Get comprehensive profile data including usage statistics"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get profile data with usage statistics"""
        try:
            user = request.user
            client = user.client_profile
            
            # Get user devices
            devices = []
            for device in client.devices.all():
                devices.append({
                    'id': device.id,
                    'device_name': device.device_name,
                    'device_type': device.device_type,
                    'device_platform': device.device_platform,
                    'device_manufacturer': device.device_manufacturer,
                    'device_model': device.device_model,
                    'status': device.status,
                    'last_seen': device.last_seen.isoformat() if device.last_seen else None,
                    'is_trusted': device.is_trusted,
                    'total_connections': device.total_connections
                })
            
            # Get usage statistics (mock data - implement actual logic)
            usage_stats = {
                'total_data_used': client.lifetime_data_used or 0,
                'daily_usage': 0,  # Implement daily usage calculation
                'weekly_usage': 0,  # Implement weekly usage calculation
                'monthly_usage': 0,  # Implement monthly usage calculation
            }
            
            # Get recent security logs
            recent_logs = SecurityLog.objects.filter(
                user=client
            ).order_by('-created_at')[:10]
            
            security_activity = []
            for log in recent_logs:
                security_activity.append({
                    'action_type': log.action_type,
                    'description': log.description,
                    'severity': log.severity,
                    'created_at': log.created_at.isoformat(),
                    'ip_address': log.ip_address
                })
            
            profile_data = {
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'has_usable_password': user.has_usable_password()
                },
                'client': {
                    'id': client.id,
                    'account': client.account,
                    'display_name': client.display_name,
                    'phone_number': client.phone_number,
                    'balance': float(client.balance),
                    'status': client.status,
                    'account_tier': client.account_tier,
                    'two_factor_enabled': client.two_factor_enabled,
                    'profile_image': request.build_absolute_uri(client.profile_image.url) if client.profile_image else None,
                    'created_at': client.created_at.isoformat() if hasattr(client, 'created_at') else None,
                    'last_login': client.last_login.isoformat() if client.last_login else None,
                    'lifetime_data_used': client.lifetime_data_used,
                    'failed_login_attempts': client.failed_login_attempts
                },
                'devices': devices,
                'usage_statistics': usage_stats,
                'security_activity': security_activity,
                'account_limits': {
                    'max_devices': client.get_max_allowed_devices(),
                    'active_devices': len([d for d in devices if d['status'] == 'active']),
                    'credit_limit': float(client.credit_limit),
                    'available_credit': float(client.available_credit)
                }
            }
            
            return Response(profile_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to load profile data: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )