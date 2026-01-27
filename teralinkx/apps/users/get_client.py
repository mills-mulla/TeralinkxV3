from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from django.utils import timezone
from django.db import transaction, models
from datetime import timedelta
import logging
import uuid
from users.models import ClientH, UserDevice, UserSession
from locations.models import Location
from core.exceptions import BusinessLogicError

logger = logging.getLogger(__name__)


class GetClientView(APIView):
    """
    API view to retrieve and update client information with device tracking.
    Balances security with usability by intelligently managing sessions.
    
    This endpoint:
    1. Retrieves client information (requires JWT authentication)
    2. Registers/updates device information
    3. Intelligently manages sessions (refresh/create based on rules)
    4. Returns comprehensive client data including sessions and devices
    """
    
    # ============================
    # CONFIGURATION
    # ============================
    
    # Session Management
    SESSION_REFRESH_WINDOW = timedelta(days=15)          # Auto-refresh if device seen < 15 days ago
    AUTO_SESSION_CREATION_WINDOW = timedelta(days=7)     # Auto-create if device seen < 7 days ago
    MAX_AUTO_SESSIONS_PER_DAY = 3                        # Limit auto-created sessions per device per day
    REQUIRE_LOGIN_AFTER_INACTIVITY = timedelta(days=30)  # Require full login after 30 days of account inactivity
    SESSION_LIFETIME = timedelta(days=90)                # Maximum session lifetime
    
    # Security
    MAX_DEVICES_PER_ACCOUNT = 10                         # Maximum devices per account
    TRUSTED_DEVICE_GRACE_PERIOD = timedelta(days=3)      # New devices become trusted after 3 days
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    # ============================
    # CORE METHODS
    # ============================
    
    def post(self, request):
        """
        Handle POST request for client information retrieval and device tracking.
        
        Expected payload:
        {
            "mac": "device_mac_address",     # Required - MUST match token's device_mac
            "ip": "current_ip_address",      # Optional
            "location_id": "location_uuid",  # Optional
            "device_info": {                 # Optional
                "device_name": "My Phone",
                "device_type": "phone",
                "device_platform": "android"
            }
        }
        
        Note: Phone number is obtained from JWT token, NOT from payload.
        """
        try:
            # Extract parameters
            mac = request.data.get('mac')
            ip_address = request.data.get('ip', request.META.get('REMOTE_ADDR'))
            location_id = request.data.get('location_id')
            device_info = request.data.get('device_info', {})
            
            # Get authenticated user from JWT
            auth_user = request.user
            
            # Get client profile for authenticated user
            client = self._get_client_for_user(auth_user)
            
            # Validate client
            if not client:
                return Response(
                    {"error": "Client profile not found for authenticated user"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Validate MAC address in payload
            if not mac:
                return Response(
                    {
                        "error": "MAC address is required in payload",
                        "security_note": "Token-payload consistency check requires MAC in payload"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # SECURITY: Get device_mac from JWT token and validate consistency
            token_device_mac = self._get_device_mac_from_token(request)
            
            if token_device_mac:
                # Perform token-payload consistency check
                validation_result = self._validate_token_payload_consistency(token_device_mac, mac, request)
                if not validation_result['valid']:
                    logger.warning(
                        f"Token-payload mismatch for user {auth_user.username}: "
                        f"Token MAC: {token_device_mac}, Payload MAC: {mac}"
                    )
                    return Response(
                        {
                            "error": "Security violation: Token-payload mismatch",
                            "details": validation_result['message'],
                            "requires_login": True,
                            "security_event": True
                        },
                        status=status.HTTP_401_UNAUTHORIZED
                    )
            
            with transaction.atomic():
                # Check if client is active
                if client.status != 'active':
                    return Response(
                        {
                            "error": f"Account is {client.status}",
                            "account_status": client.status,
                            "requires_login": True
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                # Check account inactivity using session/device activity
                if self._is_account_inactive(client):
                    return Response(
                        {
                            "error": "Account inactive for too long",
                            "message": f"Account has been inactive for more than {self.REQUIRE_LOGIN_AFTER_INACTIVITY.days} days",
                            "last_device_activity": self._get_last_device_activity(client).isoformat() if self._get_last_device_activity(client) else None,
                            "last_session_activity": self._get_last_session_activity(client).isoformat() if self._get_last_session_activity(client) else None,
                            "requires_login": True
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                # Get or create location
                location = None
                if location_id:
                    try:
                        location = Location.objects.get(id=location_id)
                    except Location.DoesNotExist:
                        logger.warning(f"Location {location_id} not found")
                
                # Get or create device (with device limit check)
                device, device_created = self._get_or_create_device_with_limits(
                    client=client,
                    mac_address=mac,
                    device_info=device_info,
                    ip_address=ip_address,
                    location=location
                )
                
                # Check if device is blocked
                if device.status == 'suspended':
                    return Response(
                        {
                            "error": "Device is blocked from network access",
                            "device_status": device.status,
                            "requires_login": True
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                # SECURITY: Verify device belongs to authenticated client
                if device.user != client:
                    logger.warning(
                        f"Device ownership mismatch: Device {mac} belongs to {device.user.account}, "
                        f"but accessed by {client.account}"
                    )
                    return Response(
                        {
                            "error": "Device not registered to authenticated user",
                            "requires_login": True,
                            "security_event": True
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                # Update device presence and trust status
                device_updated = self._update_device_status(
                    device=device,
                    ip_address=ip_address,
                    location=location,
                    device_created=device_created
                )
                
                # Intelligent session management
                session_result = self._manage_session_intelligently(
                    client=client,
                    device=device,
                    ip_address=ip_address,
                    location=location,
                    request=request,
                    token_device_mac=token_device_mac
                )
                
                # Update client's last_login (not last_activity)
                client.last_login = timezone.now()
                if location and location != client.current_location:
                    client.current_location = location
                    client.last_location_update = timezone.now()
                client.save()
                
                # Prepare comprehensive response
                response_data = self._prepare_response_data(
                    client=client,
                    device=device,
                    session_result=session_result,
                    device_created=device_created,
                    device_updated=device_updated,
                    auth_user=auth_user,
                    token_has_device_mac=bool(token_device_mac)
                )
                
                logger.info(
                    f"Client {client.account} accessed by {auth_user.username}. "
                    f"Device: {device.mac_address} ({'created' if device_created else 'existing'}), "
                    f"Session status: {session_result['status']}, "
                    f"Token-payload validation: {'PASSED' if token_device_mac else 'SKIPPED'}"
                )
                
                return Response(response_data, status=status.HTTP_200_OK)
                
        except BusinessLogicError as e:
            logger.warning(f"Business logic error in GetClientView: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error in GetClientView: {str(e)}", exc_info=True)
            return Response(
                {"error": "Internal server error", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # ============================
    # SECURITY HELPER METHODS
    # ============================
    
    def _get_device_mac_from_token(self, request):
        """Extract device_mac from JWT token payload"""
        try:
            # Get the raw token from the request
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if not auth_header.startswith('Bearer '):
                return None
            
            raw_token = auth_header.split(' ')[1]
            
            # Decode the token (without validation since JWT middleware already validated it)
            import jwt
            from django.conf import settings
            
            # Try to decode the token
            decoded_token = jwt.decode(
                raw_token,
                settings.SIMPLE_JWT['SIGNING_KEY'],
                algorithms=[settings.SIMPLE_JWT['ALGORITHM']],
                options={'verify_signature': False}  # Just decode, don't verify again
            )
            
            # Extract device_mac from token claims
            device_mac = decoded_token.get('device_mac')
            
            return device_mac
            
        except Exception as e:
            logger.debug(f"Could not extract device_mac from token: {str(e)}")
            return None
    
    def _validate_token_payload_consistency(self, token_mac, payload_mac, request):
        """
        Validate that the device_mac in JWT token matches the MAC in payload.
        
        Returns:
            dict: {'valid': bool, 'message': str}
        """
        if not token_mac:
            return {
                'valid': False,
                'message': 'Token does not contain device_mac claim'
            }
        
        if not payload_mac:
            return {
                'valid': False,
                'message': 'Payload does not contain MAC address'
            }
        
        # Normalize MAC addresses for comparison
        token_mac_normalized = token_mac.upper().replace('-', ':').replace('.', ':')
        payload_mac_normalized = payload_mac.upper().replace('-', ':').replace('.', ':')
        
        if token_mac_normalized != payload_mac_normalized:
            # Log security event
            from security.models import SecurityLog
            SecurityLog.objects.create(
                user=self._get_client_for_user(request.user),
                action_type='suspicious_activity',
                action_category='authentication',
                description=f"Token-payload MAC mismatch: Token={token_mac}, Payload={payload_mac}",
                severity='high',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details={
                    'token_mac': token_mac,
                    'payload_mac': payload_mac,
                    'user_id': request.user.id,
                    'username': request.user.username
                }
            )
            
            return {
                'valid': False,
                'message': f'Token device_mac ({token_mac}) does not match payload MAC ({payload_mac})'
            }
        
        return {
            'valid': True,
            'message': 'Token-payload consistency check passed'
        }
    
    # ============================
    # ACTIVITY TRACKING METHODS (UPDATED)
    # ============================
    
    def _get_last_device_activity(self, client):
        """Get most recent device activity across all devices"""
        # Get the most recent last_seen from all devices
        most_recent_device = client.devices.order_by('-last_seen').first()
        return most_recent_device.last_seen if most_recent_device else None
    
    def _get_last_session_activity(self, client):
        """Get most recent session activity across all sessions"""
        # Get the most recent last_activity from all sessions
        most_recent_session = client.sessions.order_by('-last_activity').first()
        return most_recent_session.last_activity if most_recent_session else None
    
    def _get_last_activity_overall(self, client):
        """
        Get the most recent activity from either devices or sessions.
        Prioritizes session activity if available.
        """
        session_activity = self._get_last_session_activity(client)
        device_activity = self._get_last_device_activity(client)
        
        # Return the most recent activity
        if session_activity and device_activity:
            return max(session_activity, device_activity)
        return session_activity or device_activity
    
    def _is_account_inactive(self, client):
        """Check if account has been inactive for too long using session/device activity"""
        last_activity = self._get_last_activity_overall(client)
        
        if not last_activity:
            # No activity ever recorded - check account creation date
            if client.user.date_joined < (timezone.now() - self.REQUIRE_LOGIN_AFTER_INACTIVITY):
                return True
            return False
        
        # Check inactivity period
        inactivity_period = timezone.now() - last_activity
        return inactivity_period > self.REQUIRE_LOGIN_AFTER_INACTIVITY
    
    # ============================
    # HELPER METHODS
    # ============================
    
    def _get_client_for_user(self, user):
        """Get client profile for authenticated user"""
        try:
            return user.client_profile
        except ClientH.DoesNotExist:
            logger.error(f"No client profile for user {user.username}")
            return None
    
    def _get_or_create_device_with_limits(self, client, mac_address, device_info, ip_address, location):
        """Get or create device with account limits check"""
        created = False  # Initialize created variable
        
        # Check device count limit
        device_count = client.devices.count()
        
        # Check if this device already exists for this user
        existing_device = UserDevice.objects.filter(
            user=client,
            mac_address=mac_address
        ).first()
        
        if existing_device:
            # Device already exists
            device = existing_device
            created = False
            
            # Update device info if provided
            update_fields = []
            if device_info:
                if 'device_name' in device_info:
                    device.device_name = device_info['device_name']
                    update_fields.append('device_name')
                if 'device_type' in device_info:
                    device.device_type = device_info['device_type']
                    update_fields.append('device_type')
                if 'device_platform' in device_info:
                    device.device_platform = device_info['device_platform']
                    update_fields.append('device_platform')
                if 'device_model' in device_info:
                    device.device_model = device_info['device_model']
                    update_fields.append('device_model')
                if 'device_manufacturer' in device_info:
                    device.device_manufacturer = device_info['device_manufacturer']
                    update_fields.append('device_manufacturer')
                
                if update_fields:
                    device.save(update_fields=update_fields)
                    
        elif device_count >= self.MAX_DEVICES_PER_ACCOUNT:
            # Device doesn't exist and limit reached
            raise BusinessLogicError(
                f"Device limit reached. Maximum {self.MAX_DEVICES_PER_ACCOUNT} devices allowed."
            )
        else:
            # Create new device
            device = UserDevice.objects.create(
                user=client,
                mac_address=mac_address,
                device_name=device_info.get('device_name', f"{client.display_name}'s Device"),
                device_type=device_info.get('device_type', 'other'),
                device_platform=device_info.get('device_platform', 'other'),
                device_model=device_info.get('device_model', ''),
                device_manufacturer=device_info.get('device_manufacturer', ''),
                last_seen_location=location,
                device_identification=device_info.get('device_identification', {}),
                is_trusted=False,  # New devices are not trusted by default
                # Note: TimeStampedModel will automatically set 'created' field
            )
            created = True
        
        return device, created
    
    def _update_device_status(self, device, ip_address, location, device_created):
        """Update device presence and check if it should become trusted"""
        updated = False
        
        # Update presence
        device.update_presence(ip_address=ip_address, location=location)
        
        # Auto-trust device after grace period
        if not device.is_trusted and device.created:  # ← Use device.created instead of device.first_seen
            time_since_created = timezone.now() - device.created
            if time_since_created >= self.TRUSTED_DEVICE_GRACE_PERIOD:
                device.is_trusted = True
                device.save()
                logger.info(f"Device {device.mac_address} auto-trusted after {self.TRUSTED_DEVICE_GRACE_PERIOD.days} days")
                updated = True
        
        return updated
    
    def _manage_session_intelligently(self, client, device, ip_address, location, request, token_device_mac=None):
        """
        Intelligent session management with security rules.
        
        Returns dict with:
        - session: UserSession or None
        - status: 'active_refreshed' | 'new_auto_created' | 'expired' | 'requires_login'
        - message: Human-readable explanation
        """
        
        # 1. Check for existing active session
        active_session = UserSession.objects.filter(
            user=client,
            device=device,
            is_active=True
        ).first()
        
        if active_session:
            # Check if session is expired or too old
            if self._is_session_too_old(active_session):
                active_session.terminate(reason="Session lifetime exceeded")
                logger.info(f"Terminated old session: {active_session.session_id}")
            elif active_session.is_expired:
                active_session.terminate(reason="Session expired")
                logger.info(f"Terminated expired session: {active_session.session_id}")
            else:
                # Refresh active session
                active_session.refresh_activity()
                active_session.ip_address = ip_address
                if location:
                    active_session.location = location
                active_session.save()
                
                return {
                    'session': active_session,
                    'status': 'active_refreshed',
                    'message': 'Existing session refreshed',
                    'requires_login': False
                }
        
        # 2. Check if we should auto-create a new session
        should_create, reason = self._should_auto_create_session(client, device)
        
        if should_create:
            # Create new session
            session_id = f"sess_{uuid.uuid4().hex[:16]}"
            session = UserSession.objects.create(
                user=client,
                device=device,
                session_id=session_id,
                ip_address=ip_address,
                location=location,
                login_time=timezone.now(),
                last_activity=timezone.now(),
                is_active=True,
                session_type='network_login',
                is_owner=True,
                was_transferred=False,
                request_metadata={
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'origin': request.META.get('HTTP_ORIGIN', ''),
                    'referer': request.META.get('HTTP_REFERER', ''),
                    'created_by': 'auto_create',
                    'reason': reason,
                    'auto_created_at': timezone.now().isoformat(),
                    'token_device_mac': token_device_mac
                },
                auto_logout_minutes=int(self.SESSION_LIFETIME.total_seconds() / 60)
            )
            
            logger.info(f"Auto-created session: {session_id} for device {device.mac_address}")
            
            return {
                'session': session,
                'status': 'new_auto_created',
                'message': f'Session auto-created: {reason}',
                'requires_login': False
            }
        
        # 3. Cannot auto-create, requires login
        return {
            'session': None,
            'status': 'requires_login',
            'message': 'Session expired. Please login to continue.',
            'requires_login': True
        }
    
    def _is_session_too_old(self, session):
        """Check if session is older than maximum lifetime"""
        session_age = timezone.now() - session.login_time
        return session_age > self.SESSION_LIFETIME
    
    def _should_auto_create_session(self, client, device):
        """
        Determine if we should auto-create a session.
        Strict security rules to prevent abuse.
        """
        reasons = []
        
        # Rule 1: Device must be trusted
        if not device.is_trusted:
            # Check if device should be auto-trusted based on creation time
            if device.created:  # ← Use device.created instead of device.first_seen
                time_since_created = timezone.now() - device.created
                if time_since_created >= self.TRUSTED_DEVICE_GRACE_PERIOD:
                    # Auto-trust the device
                    device.is_trusted = True
                    device.save()
                    logger.info(f"Device {device.mac_address} auto-trusted during session check")
                    reasons.append("Device auto-trusted")
                else:
                    return False, f"Device not trusted yet (created {time_since_created.days} days ago)"
            else:
                return False, "Device creation time unknown"
        
        # Rule 2: Device must have been seen recently
        if not device.last_seen:
            return False, "Device never seen before"
        
        time_since_last_seen = timezone.now() - device.last_seen
        if time_since_last_seen > self.AUTO_SESSION_CREATION_WINDOW:
            return False, f"Device not seen recently ({time_since_last_seen.days} days ago)"
        
        reasons.append(f"Device seen {time_since_last_seen.days} days ago")
        
        # Rule 3: No recent auto-session spam
        today = timezone.now().date()
        todays_auto_sessions = UserSession.objects.filter(
            user=client,
            device=device,
            login_time__date=today,
            request_metadata__created_by='auto_create'
        ).count()
        
        if todays_auto_sessions >= self.MAX_AUTO_SESSIONS_PER_DAY:
            return False, f"Max auto-sessions reached ({todays_auto_sessions}/day)"
        
        # Rule 4: Check if recent session was manually terminated (not expired)
        recent_manual_termination = UserSession.objects.filter(
            user=client,
            device=device,
            is_active=False,
            last_activity__gte=timezone.now() - timedelta(days=1)
        ).exclude(
            request_metadata__reason__icontains='expired'
        ).exclude(
            request_metadata__reason__icontains='lifetime'
        ).exists()
        
        if recent_manual_termination:
            return False, "Recent manual termination detected"
        
        # Rule 5: Client account must be active
        if client.status != 'active':
            return False, f"Client account is {client.status}"
        
        # Rule 6: Device must be active
        if device.status != 'active':
            return False, f"Device is {device.status}"
        
        # Rule 7: Check account inactivity using proper activity tracking
        if self._is_account_inactive(client):
            return False, f"Account inactive for >{self.REQUIRE_LOGIN_AFTER_INACTIVITY.days} days"
        
        # All rules passed
        reason_msg = "; ".join(reasons)
        return True, reason_msg
    
    def _prepare_response_data(self, client, device, session_result, device_created, device_updated, auth_user, token_has_device_mac):
        """Prepare comprehensive response data with correct activity tracking"""

        print(f"DEBUG: client.sessions.model = {client.sessions.model}")
        print(f"DEBUG: client.sessions.model._meta.fields = {[f.name for f in client.sessions.model._meta.get_fields()]}")
        
        session = session_result.get('session')
        session_status = session_result.get('status')
        
        # Get session statistics
        session_stats = client.get_session_statistics() if hasattr(client, 'get_session_statistics') else {}
        
        # Get activity timestamps
        last_device_activity = self._get_last_device_activity(client)
        last_session_activity = self._get_last_session_activity(client)
        last_activity_overall = self._get_last_activity_overall(client)
        
        # Calculate inactivity days
        inactivity_days = None
        if last_activity_overall:
            inactivity_days = (timezone.now() - last_activity_overall).days
        
        # Calculate device trust progress
        trust_progress = 0
        trust_days_remaining = 0
        if not device.is_trusted and device.created:  # ← Use device.created
            time_since_created = timezone.now() - device.created
            total_grace_seconds = self.TRUSTED_DEVICE_GRACE_PERIOD.total_seconds()
            elapsed_seconds = time_since_created.total_seconds()
            trust_progress = min(100, (elapsed_seconds / total_grace_seconds) * 100)
            trust_days_remaining = max(0, (total_grace_seconds - elapsed_seconds) / 86400)

        # Build response
        response = {
            # Authentication Information
            "authentication": {
                "method": "jwt",
                "authenticated_user": auth_user.username,
                "client_match": client.user == auth_user,
                "requires_login": session_result.get('requires_login', False),
                "token_has_device_mac": token_has_device_mac,
                "token_payload_validation": "required" if token_has_device_mac else "not_required"
            },
            
            # Session Information
            "session_status": {
                "status": session_status,
                "message": session_result.get('message', ''),
                "has_active_session": session is not None,
                "requires_login": session_result.get('requires_login', False),
                "can_auto_renew": not session_result.get('requires_login', True)
            },
            
            # Client Information
            "client_info": {
                "client_id": str(client.id),
                "account": client.account,
                "display_name": client.display_name,
                "phone_number": client.phone_number,
                "account_tier": client.account_tier,
                "status": client.status,
                "last_login": client.last_login.isoformat() if client.last_login else None,
                "last_device_activity": last_device_activity.isoformat() if last_device_activity else None,
                "last_session_activity": last_session_activity.isoformat() if last_session_activity else None,
                "last_activity_overall": last_activity_overall.isoformat() if last_activity_overall else None,
                "inactivity_days": inactivity_days,
                "max_inactivity_days": self.REQUIRE_LOGIN_AFTER_INACTIVITY.days,
                "is_account_inactive": self._is_account_inactive(client),
            },
            
            # Device Information
            "device_info": {
                "device_id": str(device.id),
                "device_name": device.device_name,
                "mac_address": device.mac_address,
                "device_type": device.device_type,
                "device_platform": device.device_platform,
                "status": device.status,
                "is_trusted": device.is_trusted,
                "created": device.created.isoformat() if device.created else None,  # ← Use created
                "last_seen": device.last_seen.isoformat() if device.last_seen else None,
                "total_connections": device.total_connections,
                "device_created": device_created,
                "device_updated": device_updated,
                "trust_progress": round(trust_progress, 1),
                "trust_days_remaining": round(trust_days_remaining, 1),
                "auto_trust_days": self.TRUSTED_DEVICE_GRACE_PERIOD.days,
                "can_auto_create_session": device.is_trusted and device.status == 'active',
            },
            
            # Security Information
            "security": {
                "token_payload_validation_required": token_has_device_mac,
                "device_ownership_verified": True,
                "max_devices_per_account": self.MAX_DEVICES_PER_ACCOUNT,
                "current_device_count": client.devices.count(),
            },
            
            # Configuration Information
            "configuration": {
                "session_refresh_window_days": self.SESSION_REFRESH_WINDOW.days,
                "auto_session_creation_window_days": self.AUTO_SESSION_CREATION_WINDOW.days,
                "max_auto_sessions_per_day": self.MAX_AUTO_SESSIONS_PER_DAY,
                "require_login_after_inactivity_days": self.REQUIRE_LOGIN_AFTER_INACTIVITY.days,
                "session_lifetime_days": self.SESSION_LIFETIME.days,
                "max_devices_per_account": self.MAX_DEVICES_PER_ACCOUNT,
                "trusted_device_grace_period_days": self.TRUSTED_DEVICE_GRACE_PERIOD.days,
            },
            
            # Statistics
            "statistics": {
                "active_devices": client.devices.filter(status='active').count(),
                "total_devices": client.devices.count(),
                "active_sessions": session_stats.get('total_active_sessions', 0),
                "max_allowed_devices": self.MAX_DEVICES_PER_ACCOUNT,
            },
            
            # Location Information
            "location_info": {
                "current_location": str(client.current_location) if client.current_location else None,
                "device_location": str(device.last_seen_location) if device.last_seen_location else None,
            },
            
            # Timestamps
            "timestamps": {
                "server_time": timezone.now().isoformat(),
                "client_last_login": client.last_login.isoformat() if client.last_login else None,
                "device_last_seen": device.last_seen.isoformat() if device.last_seen else None,
                "last_device_activity": last_device_activity.isoformat() if last_device_activity else None,
                "last_session_activity": last_session_activity.isoformat() if last_session_activity else None,
            }
        }
        
        # Add session details if available
        if session:
            session_age = timezone.now() - session.login_time
            response["session_details"] = {
                "session_id": session.session_id,
                "ip_address": session.ip_address,
                "login_time": session.login_time.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "age_days": session_age.days,
                "age_hours": session_age.total_seconds() / 3600,
                "max_age_days": self.SESSION_LIFETIME.days,
                "session_type": session.session_type,
                "auto_logout_minutes": session.auto_logout_minutes,
                "is_owner": session.is_owner,
                "was_transferred": session.was_transferred,
                "created_by": session.request_metadata.get('created_by', 'manual'),
                "token_device_mac": session.request_metadata.get('token_device_mac'),
            }
        
        # Add security recommendations
        if not device.is_trusted and not device_created:
            response["security_recommendation"] = {
                "message": f"This device will become trusted in {round(trust_days_remaining, 1)} days",
                "action": "wait_for_auto_trust",
                "progress_percentage": trust_progress,
                "device_id": str(device.id)
            }
        
        # Add inactivity warning
        if last_activity_overall:
            inactivity_days = (timezone.now() - last_activity_overall).days
            warning_threshold = self.REQUIRE_LOGIN_AFTER_INACTIVITY.days - 7  # Warn 7 days before
            
            if inactivity_days > warning_threshold:
                response["inactivity_warning"] = {
                    "message": f"Account has been inactive for {inactivity_days} days",
                    "days_until_login_required": self.REQUIRE_LOGIN_AFTER_INACTIVITY.days - inactivity_days,
                    "action": "login_soon_required"
                }
        
        return response