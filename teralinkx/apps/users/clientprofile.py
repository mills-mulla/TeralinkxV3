# views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.utils import timezone
from users.models import ClientH
from core.serializers.userprofile_serializer import ClientProfileSerializer
from security.models import SecurityLog
import logging

logger = logging.getLogger(__name__)


class UpdateClientProfileView(generics.UpdateAPIView):
    """
    View for updating client profile information with enhanced security and validation.
    
    Features:
    - Multi-field update with validation
    - Security logging for sensitive changes
    - Device and location updates
    - Permission-based field restrictions
    """
    
    queryset = ClientH.objects.all()
    serializer_class = ClientProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # Fields that trigger security logs when changed
    SECURITY_SENSITIVE_FIELDS = {
        'two_factor_enabled': '2FA status changed',
        'status': 'Account status changed',
        'account_tier': 'Account tier changed',
        'home_location': 'Home location changed',
        'current_location': 'Current location changed',
    }
    
    # Fields that require special permissions
    RESTRICTED_FIELDS = ['status', 'account_tier', 'credit_limit', 'balance']

    def get_object(self):
        """Get the client profile for the authenticated user."""
        try:
            return self.request.user.client_profile
        except ClientH.DoesNotExist:
            # Create a client profile if it doesn't exist (for new users)
            return ClientH.objects.create(
                user=self.request.user,
                account=self.request.user.username,  # Default account number
                display_name=self.request.user.get_full_name(),
                account_tier='basic',
                status='active'
            )

    def update(self, request, *args, **kwargs):
        """Enhanced update with security logging and validation."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Check for restricted fields in request
        restricted_fields = set(request.data.keys()) & set(self.RESTRICTED_FIELDS)
        if restricted_fields and not self._has_admin_permission(request):
            return Response(
                {"error": f"Cannot update restricted fields: {', '.join(restricted_fields)}"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate device updates
        if 'devices' in request.data:
            device_update_result = self._validate_device_updates(instance, request.data.get('devices', []))
            if not device_update_result['success']:
                return Response(
                    {"error": device_update_result['message']},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Track changes before update
        changes = self._track_changes(instance, request.data)
        
        # Perform update
        self.perform_update(serializer)
        
        # Log sensitive changes
        self._log_sensitive_changes(instance, changes, request)
        
        # Handle post-update actions
        self._handle_post_update_actions(instance, request.data)
        
        # Get updated instance
        updated_instance = self.get_object()
        response_serializer = self.get_serializer(updated_instance)
        
        return Response(response_serializer.data)

    def perform_update(self, serializer):
        """Save the updated instance."""
        serializer.save()
        logger.info(f"Profile updated for user: {self.request.user.username}")

    def _has_admin_permission(self, request):
        """Check if user has admin permissions for restricted fields."""
        return request.user.is_staff or request.user.is_superuser

    def _track_changes(self, instance, new_data):
        """Track what fields are being changed."""
        changes = {}
        
        for field, new_value in new_data.items():
            if field in self.SECURITY_SENSITIVE_FIELDS:
                old_value = getattr(instance, field, None)
                
                # Handle related fields
                if hasattr(old_value, 'id'):
                    old_value = str(old_value)
                if hasattr(new_value, 'id'):
                    new_value = str(new_value)
                
                if old_value != new_value:
                    changes[field] = {
                        'old': old_value,
                        'new': new_value,
                        'message': self.SECURITY_SENSITIVE_FIELDS[field]
                    }
        
        return changes

    def _log_sensitive_changes(self, instance, changes, request):
        """Log security-sensitive changes."""
        if changes:
            for field, change_info in changes.items():
                SecurityLog.objects.create(
                    user=instance,
                    action_type='profile_update',
                    description=f"{change_info['message']}: {change_info['old']} → {change_info['new']}",
                    severity='medium',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    details={
                        'field': field,
                        'old_value': str(change_info['old']),
                        'new_value': str(change_info['new']),
                        'changed_by': request.user.username,
                        'timestamp': timezone.now().isoformat()
                    }
                )
                
                logger.info(
                    f"Security-sensitive change detected for user {instance.account}: "
                    f"{field} changed from {change_info['old']} to {change_info['new']}"
                )

    def _validate_device_updates(self, client, devices_data):
        """Validate device-related updates."""
        for device_data in devices_data:
            device_mac = device_data.get('mac_address')
            if not device_mac:
                return {"success": False, "message": "Device MAC address is required"}
            
            # Check if device exists and belongs to user
            try:
                device = client.devices.get(mac_address=device_mac)
            except client.devices.model.DoesNotExist:
                return {
                    "success": False, 
                    "message": f"Device with MAC {device_mac} not found or doesn't belong to you"
                }
            
            # Validate device status changes
            if 'status' in device_data:
                new_status = device_data['status']
                if new_status == 'suspended' and not self._has_admin_permission(self.request):
                    return {
                        "success": False,
                        "message": "Only administrators can suspend devices"
                    }
        
        return {"success": True, "message": "Device updates validated"}

    def _handle_post_update_actions(self, instance, data):
        """Handle special actions after profile update."""
        # Update user's last activity
        instance.user.last_login = timezone.now()
        instance.user.save()
        
        # Handle location updates
        if 'current_location' in data:
            instance.last_location_update = timezone.now()
            instance.save()
        
        # Handle 2FA setup notification
        if 'two_factor_enabled' in data and data['two_factor_enabled']:
            # Send notification or log 2FA setup
            logger.info(f"2FA enabled for user: {instance.account}")
        
        # Handle device updates
        if 'devices' in data:
            self._process_device_updates(instance, data['devices'])

    def _process_device_updates(self, client, devices_data):
        """Process device updates from the request."""
        for device_data in devices_data:
            try:
                device = client.devices.get(mac_address=device_data['mac_address'])
                
                # Update device fields
                updatable_fields = ['device_name', 'device_type', 'device_platform', 
                                   'device_model', 'device_manufacturer', 'auto_connect']
                
                for field in updatable_fields:
                    if field in device_data:
                        setattr(device, field, device_data[field])
                
                # Handle status changes with logging
                if 'status' in device_data and device_data['status'] != device.status:
                    old_status = device.status
                    device.status = device_data['status']
                    
                    # Log device status change
                    SecurityLog.objects.create(
                        user=client,
                        action_type='device_status_changed',
                        description=f"Device {device.mac_address} status changed: {old_status} → {device.status}",
                        severity='low',
                        details={
                            'device_id': str(device.id),
                            'device_name': device.device_name,
                            'old_status': old_status,
                            'new_status': device.status,
                            'changed_by': self.request.user.username
                        }
                    )
                
                device.save()
                
            except client.devices.model.DoesNotExist:
                logger.warning(f"Device {device_data.get('mac_address')} not found for user {client.account}")