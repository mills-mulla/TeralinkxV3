from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
import logging
import uuid

from users.models import ClientH, UserDevice, UserSession
from locations.models import Location
from core.services.client_service import ClientService  # Use shared client service

logger = logging.getLogger(__name__)
User = get_user_model()


class DeviceAutoAuthAPIView(APIView):
    """
    MAC-based automatic device authentication.
    
    Automatically authenticates users based on their registered device MAC addresses.
    Provides seamless authentication without requiring phone number input.
    """
    permission_classes = [AllowAny]  # No JWT required for initial auth
    authentication_classes = []  # No authentication needed
    
    def post(self, request):
        """
        Authenticate user automatically using device MAC address.
        
        Expected payload:
        {
            "current_mac": "D4:01:C3:CB:12:D8",
            "current_ip": "192.168.88.1",
            "location_id": 1,
            "device_info": {...}
        }
        """
        try:
            # Extract request data
            mac_address = request.data.get('current_mac', '').strip()
            ip_address = request.data.get('current_ip', '').strip()
            location_id = request.data.get('location_id', 1)
            device_info = request.data.get('device_info', {})
            
            logger.info(f"🤖 AUTO-AUTH attempt - MAC: {mac_address}, IP: {ip_address}")
            
            # Validate required fields
            if not mac_address:
                return Response({
                    'success': False,
                    'error': 'MAC address is required',
                    'error_type': 'missing_mac'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not ip_address:
                return Response({
                    'success': False,
                    'error': 'IP address is required',
                    'error_type': 'missing_ip'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get location
            try:
                location = Location.objects.get(id=location_id)
            except Location.DoesNotExist:
                location = Location.objects.first()  # Fallback to first location
            
            # 🔍 STEP 1: Find device by MAC address
            try:
                device = UserDevice.objects.select_related('user').get(
                    mac_address=mac_address,
                    status='active'
                )
                logger.info(f"✅ Device found: {device.device_name} owned by {device.user.account}")
                
            except UserDevice.DoesNotExist:
                logger.info(f"❌ No active device found for MAC: {mac_address}")
                return Response({
                    'success': False,
                    'error': 'Device not registered or inactive',
                    'error_type': 'device_not_found',
                    'requires_manual_auth': True
                }, status=status.HTTP_404_NOT_FOUND)
            
            except UserDevice.MultipleObjectsReturned:
                # Handle case where MAC is associated with multiple users
                logger.warning(f"⚠️ Multiple devices found for MAC: {mac_address}")
                device = UserDevice.objects.select_related('user').filter(
                    mac_address=mac_address,
                    status='active'
                ).order_by('-last_seen').first()
                logger.info(f"📱 Using most recently seen device: {device.user.account}")
            
            # 🔍 STEP 2: Get the user from the device
            client = device.user
            user = client.user
            
            # 🔍 STEP 3: Security checks
            if client.status != 'active':
                logger.warning(f"🚫 Account suspended: {client.account}")
                return Response({
                    'success': False,
                    'error': 'Account is suspended or inactive',
                    'error_type': 'account_suspended'
                }, status=status.HTTP_403_FORBIDDEN)
            
            if not device.is_trusted:
                logger.info(f"🔐 Device not trusted, requiring manual auth: {mac_address}")
                return Response({
                    'success': False,
                    'error': 'Device requires manual authentication',
                    'error_type': 'device_not_trusted',
                    'requires_manual_auth': True,
                    'suggested_phone': client.phone_number
                }, status=status.HTTP_403_FORBIDDEN)
            
            # 🔍 STEP 4: Update device and session with atomic transaction
            with transaction.atomic():
                # Update device presence
                device.update_presence(ip_address=ip_address, location=location)
                
                # Create or update web auth session (not RADIUS network sessions)
                session = UserSession.objects.filter(
                    user=client,
                    device=device,
                    session_type='web',
                    is_active=True
                ).first()
                
                if session:
                    # Update existing session
                    session.ip_address = ip_address
                    session.location = location
                    session.last_activity = timezone.now()
                    session.request_metadata = device_info
                    session.save()
                    logger.info(f"Using existing active session: {session.session_id} for device {mac_address}")
                else:
                    # Create new web auth session
                    session = UserSession.objects.create(
                        user=client,
                        device=device,
                        session_id=f"auto_{timezone.now().timestamp()}",
                        ip_address=ip_address,
                        location=location,
                        session_type='web',
                        is_active=True,
                        request_metadata=device_info,
                        user_agent=request.META.get('HTTP_USER_AGENT', '')
                    )
                    logger.info(f"Created new session: {session.session_id} for device {mac_address}")
                
                # Update client location and activity
                client.current_location = location
                client.last_location_update = timezone.now()
                client.last_login = timezone.now()
                client.last_seen = timezone.now()
                client.save()
            
            # 🔍 STEP 5: Generate authentication tokens using ClientService
            correlation_id = str(uuid.uuid4())
            
            # Generate access and refresh tokens using the same method as passwordless auth
            token_data = ClientService._generate_jwt_tokens(
                user=user,
                client=client,
                device=device,
                session=session,
                ip_address=ip_address,
                location=location,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                correlation_id=correlation_id
            )
            
            # 🔍 STEP 6: Prepare response matching passwordless auth format
            response_data = {
                'success': True,
                'message': f'Welcome back, {client.display_name or user.username}!',
                'authentication_method': 'device_auto_auth',
                'is_new_account': False,
                'requires_otp': False,
                
                # Auth tokens (matching passwordless format)
                'auth': token_data,
                
                # User data (matching passwordless format)
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                },
                
                # Client data (matching passwordless format)
                'client': {
                    'id': client.id,
                    'account': client.account,
                    'display_name': client.display_name,
                    'phone_number': client.phone_number,
                    'balance': float(client.balance),
                    'account_tier': client.account_tier,
                    'status': client.status,
                    'home_location': client.home_location.name if client.home_location else None,
                    'current_location': location.name
                },
                
                # Device data
                'device': {
                    'id': device.id,
                    'mac_address': device.mac_address,
                    'device_name': device.device_name,
                    'device_type': device.device_type,
                    'is_trusted': device.is_trusted,
                    'last_seen': device.last_seen.isoformat() if device.last_seen else None,
                    'total_connections': device.total_connections
                },
                
                # Session data
                'session': {
                    'id': session.id,
                    'session_id': session.session_id,
                    'login_time': session.login_time.isoformat() if session.login_time else None,
                    'location': str(location),
                    'ip_address': ip_address
                },
                
                # Metadata (matching passwordless format)
                'metadata': {
                    'is_new_user': False,
                    'client_created': False,
                    'processing_time_ms': 0,  # Could calculate if needed
                    'timestamp': timezone.now().isoformat(),
                    'location_detected': True,
                    'requires_otp': False,
                    'requires_password': False,
                    'auth_method': 'device_auto_auth'
                }
            }
            
            logger.info(f"🎉 AUTO-AUTH successful for {client.account} via device {device.device_name}")
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"💥 AUTO-AUTH error: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': 'Authentication failed due to server error',
                'error_type': 'server_error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeviceTrustAPIView(APIView):
    """
    Manage device trust settings for auto-authentication.
    """
    permission_classes = [AllowAny]  # No JWT required for trust setup
    authentication_classes = []  # No authentication needed
    
    def post(self, request):
        """
        Mark a device as trusted for auto-authentication.
        
        Expected payload:
        {
            "current_mac": "D4:01:C3:CB:12:D8",
            "phone": "+254712345678",
            "trust_device": true
        }
        """
        try:
            mac_address = request.data.get('current_mac', '').strip()
            phone = request.data.get('phone', '').strip()
            trust_device = request.data.get('trust_device', False)
            
            if not mac_address or not phone:
                return Response({
                    'success': False,
                    'error': 'MAC address and phone number are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Find user by phone
            try:
                client = ClientH.objects.get(phone_number=phone, status='active')
            except ClientH.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Find or create device
            device, created = UserDevice.objects.get_or_create(
                mac_address=mac_address,
                user=client,
                defaults={
                    'device_name': f"{client.display_name}'s Device",
                    'device_type': 'other',
                    'status': 'active'
                }
            )
            
            # Update trust setting
            device.is_trusted = trust_device
            device.save()
            
            action = 'trusted' if trust_device else 'untrusted'
            logger.info(f"🔐 Device {mac_address} {action} for user {client.account}")
            
            return Response({
                'success': True,
                'message': f'Device {action} successfully',
                'device_trusted': device.is_trusted,
                'device_name': device.device_name
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"💥 Device trust error: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': 'Failed to update device trust'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)