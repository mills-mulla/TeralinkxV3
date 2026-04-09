# apps/core/enhanced_device_auth.py - Enhanced Device Auto-Auth with Fallback Strategies
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from django.core.cache import caches
from django.conf import settings
import logging
import uuid
import json

from users.models import ClientH, UserDevice, UserSession
from locations.models import Location
from core.services.client_service import ClientService
from .auth_health import SessionBackupService

logger = logging.getLogger(__name__)
User = get_user_model()


class EnhancedDeviceAutoAuthView(APIView):
    """
    Enhanced device auto-authentication with multiple fallback strategies.
    Provides seamless authentication recovery after backend restarts.
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def post(self, request):
        """
        Multi-strategy device authentication with comprehensive fallback.
        """
        try:
            # Extract request data
            mac_address = request.data.get('current_mac', '').strip()
            ip_address = request.data.get('current_ip', '').strip()
            location_id = request.data.get('location_id', 1)
            device_info = request.data.get('device_info', {})
            
            # Check if this is a seamless reauth attempt
            is_seamless_reauth = device_info.get('seamless_reauth', False)
            stored_user_data = device_info.get('stored_user_data')
            
            logger.info(f"🔄 Enhanced AUTO-AUTH attempt - MAC: {mac_address}, Seamless: {is_seamless_reauth}")
            
            # Validate required fields
            if not mac_address:
                return self._error_response('MAC address is required', 'missing_mac')
            
            if not ip_address:
                return self._error_response('IP address is required', 'missing_ip')
            
            # Get location
            try:
                location = Location.objects.get(id=location_id)
            except Location.DoesNotExist:
                location = Location.objects.first()
            
            # Strategy 1: Device fingerprint authentication
            auth_result = self._attempt_device_fingerprint_auth(
                mac_address, ip_address, location, device_info
            )
            
            if auth_result['success']:
                logger.info("✅ Device fingerprint auth successful")
                return self._success_response(auth_result, 'device_fingerprint')
            
            # Strategy 2: Session token recovery (if seamless reauth)
            if is_seamless_reauth and stored_user_data:
                auth_result = self._attempt_session_recovery(
                    stored_user_data, mac_address, ip_address, location, device_info
                )
                
                if auth_result['success']:
                    logger.info("✅ Session recovery successful")
                    return self._success_response(auth_result, 'session_recovery')
            
            # Strategy 3: Trusted device authentication
            auth_result = self._attempt_trusted_device_auth(
                mac_address, ip_address, location, device_info
            )
            
            if auth_result['success']:
                logger.info("✅ Trusted device auth successful")
                return self._success_response(auth_result, 'trusted_device')
            
            # Strategy 4: Phone verification bypass (for known devices)
            if stored_user_data and stored_user_data.get('phone'):
                auth_result = self._attempt_phone_verification_bypass(
                    stored_user_data['phone'], mac_address, ip_address, location, device_info
                )
                
                if auth_result['success']:
                    logger.info("✅ Phone verification bypass successful")
                    return self._success_response(auth_result, 'phone_bypass')
            
            # All strategies failed
            logger.warning("❌ All authentication strategies failed")
            return self._error_response(
                'Device authentication failed. Manual login required.',
                'all_strategies_failed',
                requires_manual_auth=True
            )
            
        except Exception as e:
            logger.error(f"💥 Enhanced device auth error: {str(e)}", exc_info=True)
            return self._error_response(
                'Authentication failed due to server error',
                'server_error'
            )
    
    def _attempt_device_fingerprint_auth(self, mac_address, ip_address, location, device_info):
        """Strategy 1: Device fingerprint authentication"""
        try:
            # Find device by MAC address
            device = UserDevice.objects.select_related('user').filter(
                mac_address=mac_address,
                status='active'
            ).first()
            
            if not device:
                return {'success': False, 'error': 'Device not found'}
            
            client = device.user
            user = client.user
            
            # Security checks
            if client.status != 'active':
                return {'success': False, 'error': 'Account suspended'}
            
            # Update device presence
            device.update_presence(ip_address=ip_address, location=location)
            
            # Generate tokens
            tokens = self._generate_auth_tokens(user, client, device, location, ip_address, device_info)
            
            # Backup session
            SessionBackupService.backup_session(user.id, {
                'user_id': user.id,
                'client_id': client.id,
                'device_id': device.id,
                'location_id': location.id,
                'auth_method': 'device_fingerprint'
            })
            
            return {
                'success': True,
                'user': user,
                'client': client,
                'device': device,
                'tokens': tokens,
                'location': location
            }
            
        except Exception as e:
            logger.error(f"Device fingerprint auth error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _attempt_session_recovery(self, stored_user_data, mac_address, ip_address, location, device_info):
        """Strategy 2: Session token recovery"""
        try:
            user_id = stored_user_data.get('id')
            if not user_id:
                return {'success': False, 'error': 'No user ID in stored data'}
            
            # Try to restore session from backup
            session_data = SessionBackupService.restore_session(user_id)
            if not session_data:
                return {'success': False, 'error': 'No session backup found'}
            
            # Validate user still exists and is active
            try:
                user = User.objects.get(id=user_id)
                client = user.clienth
                
                if client.status != 'active':
                    return {'success': False, 'error': 'Account no longer active'}
                
            except (User.DoesNotExist, AttributeError):
                return {'success': False, 'error': 'User not found'}
            
            # Find or create device
            device, created = UserDevice.objects.get_or_create(
                mac_address=mac_address,
                user=client,
                defaults={
                    'device_name': f"{client.display_name}'s Device",
                    'device_type': 'other',
                    'status': 'active',
                    'is_trusted': True  # Trust device from session recovery
                }
            )
            
            # Update device presence
            device.update_presence(ip_address=ip_address, location=location)
            
            # Generate new tokens
            tokens = self._generate_auth_tokens(user, client, device, location, ip_address, device_info)
            
            return {
                'success': True,
                'user': user,
                'client': client,
                'device': device,
                'tokens': tokens,
                'location': location
            }
            
        except Exception as e:
            logger.error(f"Session recovery error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _attempt_trusted_device_auth(self, mac_address, ip_address, location, device_info):
        """Strategy 3: Trusted device authentication"""
        try:
            # Find trusted devices by MAC
            trusted_devices = UserDevice.objects.select_related('user').filter(
                mac_address=mac_address,
                is_trusted=True,
                status='active'
            )
            
            if not trusted_devices.exists():
                return {'success': False, 'error': 'No trusted devices found'}
            
            # Use most recently seen trusted device
            device = trusted_devices.order_by('-last_seen').first()
            client = device.user
            user = client.user
            
            # Security checks
            if client.status != 'active':
                return {'success': False, 'error': 'Account suspended'}
            
            # Update device presence
            device.update_presence(ip_address=ip_address, location=location)
            
            # Generate tokens
            tokens = self._generate_auth_tokens(user, client, device, location, ip_address, device_info)
            
            # Backup session
            SessionBackupService.backup_session(user.id, {
                'user_id': user.id,
                'client_id': client.id,
                'device_id': device.id,
                'location_id': location.id,
                'auth_method': 'trusted_device'
            })
            
            return {
                'success': True,
                'user': user,
                'client': client,
                'device': device,
                'tokens': tokens,
                'location': location
            }
            
        except Exception as e:
            logger.error(f"Trusted device auth error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _attempt_phone_verification_bypass(self, phone, mac_address, ip_address, location, device_info):
        """Strategy 4: Phone verification bypass for known devices"""
        try:
            # Find user by phone
            try:
                client = ClientH.objects.get(phone_number=phone, status='active')
                user = client.user
            except ClientH.DoesNotExist:
                return {'success': False, 'error': 'User not found'}
            
            # Check if device was recently used by this user
            recent_device = UserDevice.objects.filter(
                mac_address=mac_address,
                user=client,
                last_seen__gte=timezone.now() - timezone.timedelta(days=7)  # Within last week
            ).first()
            
            if not recent_device:
                return {'success': False, 'error': 'Device not recently used'}
            
            # Update device as trusted and active
            recent_device.is_trusted = True
            recent_device.status = 'active'
            recent_device.update_presence(ip_address=ip_address, location=location)
            
            # Generate tokens
            tokens = self._generate_auth_tokens(user, client, recent_device, location, ip_address, device_info)
            
            # Backup session
            SessionBackupService.backup_session(user.id, {
                'user_id': user.id,
                'client_id': client.id,
                'device_id': recent_device.id,
                'location_id': location.id,
                'auth_method': 'phone_bypass'
            })
            
            return {
                'success': True,
                'user': user,
                'client': client,
                'device': recent_device,
                'tokens': tokens,
                'location': location
            }
            
        except Exception as e:
            logger.error(f"Phone verification bypass error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _generate_auth_tokens(self, user, client, device, location, ip_address, device_info):
        """Generate JWT tokens using ClientService"""
        try:
            # Create or update session
            session = UserSession.objects.filter(
                user=client,
                device=device,
                session_type='web',
                is_active=True
            ).first()
            
            if session:
                session.ip_address = ip_address
                session.location = location
                session.last_activity = timezone.now()
                session.request_metadata = device_info
                session.save()
            else:
                session = UserSession.objects.create(
                    user=client,
                    device=device,
                    session_id=f"enhanced_auto_{timezone.now().timestamp()}",
                    ip_address=ip_address,
                    location=location,
                    session_type='web',
                    is_active=True,
                    request_metadata=device_info,
                    user_agent=device_info.get('userAgent', '')
                )
            
            # Update client
            client.current_location = location
            client.last_location_update = timezone.now()
            client.last_login = timezone.now()
            client.last_seen = timezone.now()
            client.save()
            
            # Generate tokens
            correlation_id = str(uuid.uuid4())
            token_data = ClientService._generate_jwt_tokens(
                user=user,
                client=client,
                device=device,
                session=session,
                ip_address=ip_address,
                location=location,
                user_agent=device_info.get('userAgent', ''),
                correlation_id=correlation_id
            )
            
            return token_data
            
        except Exception as e:
            logger.error(f"Token generation error: {e}")
            raise
    
    def _success_response(self, auth_result, auth_method):
        """Format successful authentication response"""
        user = auth_result['user']
        client = auth_result['client']
        device = auth_result['device']
        tokens = auth_result['tokens']
        location = auth_result['location']
        
        return Response({
            'success': True,
            'message': f'Welcome back, {client.display_name or user.username}!',
            'authentication_method': auth_method,
            'is_new_account': False,
            'requires_otp': False,
            
            # Auth tokens
            'auth': tokens,
            
            # User data
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            
            # Client data
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
                'id': getattr(auth_result.get('session'), 'id', None),
                'session_id': getattr(auth_result.get('session'), 'session_id', None),
                'login_time': timezone.now().isoformat(),
                'location': str(location),
                'ip_address': auth_result.get('ip_address', '')
            },
            
            # Metadata
            'metadata': {
                'is_new_user': False,
                'client_created': False,
                'processing_time_ms': 0,
                'timestamp': timezone.now().isoformat(),
                'location_detected': True,
                'requires_otp': False,
                'requires_password': False,
                'auth_method': auth_method,
                'backend_version': getattr(settings, 'BACKEND_VERSION', 'unknown')
            }
        }, status=status.HTTP_200_OK)
    
    def _error_response(self, error_message, error_type, requires_manual_auth=False):
        """Format error response"""
        response_data = {
            'success': False,
            'error': error_message,
            'error_type': error_type,
            'timestamp': timezone.now().isoformat()
        }
        
        if requires_manual_auth:
            response_data['requires_manual_auth'] = True
        
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)