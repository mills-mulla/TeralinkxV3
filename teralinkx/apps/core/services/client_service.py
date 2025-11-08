# core/services/client_service.py
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.authtoken.models import Token
from users.models import ClientH, UserDevice
from locations.models import Location
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

class ClientService:

    @staticmethod
    def detect_location(ip_address=None, mac_address=None):
        """Simple location detection - enhance this later"""
        try:
            # For now, return first active location or create default
            location = Location.objects.filter(is_active=True).first()
            if not location:
                location = Location.objects.create(
                    name="Primary Hotspot",
                    code="PRIMARY",
                    location_type="hotspot",
                    city="Nairobi",
                    is_active=True
                )
            return location
        except Exception as e:
            # Fallback if locations table doesn't exist or other error
            print(f"Location detection error: {e}")
            # Create a default location without saving to DB
            class FallbackLocation:
                id = 1
                name = "Default Location"
                code = "DEFAULT"
                
                def can_roam_to(self, other_location):
                    return True
                    
            return FallbackLocation()

    @staticmethod
    @transaction.atomic
    def create_user_and_client(validated_data):
        """
        Creates a User and corresponding ClientH atomically.
        """
        phone = validated_data['phone']
        current_ip = validated_data.get('current_ip')
        current_mac = validated_data.get('current_mac')
        
        # Detect location based on IP/MAC
        detected_location = ClientService.detect_location(current_ip, current_mac)

        # Create or get User
        user, user_created = User.objects.get_or_create(
            username=phone,
            defaults={
                'first_name': f"User_{phone[-4:]}",
                'email': f"{phone}@teralinkx.net",
            }
        )

        # Create or get ClientH - handle location gracefully
        client_data = {
            'account': phone,
            'phone_number': phone,
            'display_name': f"User_{phone[-4:]}",
            'status': 'active'
        }
        
        # Only add location if it's a real Location instance
        if hasattr(detected_location, 'id'):
            client_data['home_location_id'] = detected_location.id
            client_data['current_location_id'] = detected_location.id
        
        client, client_created = ClientH.objects.get_or_create(
            user=user,
            defaults=client_data
        )

        # Create UserDevice if MAC provided
        if current_mac:
            device_data = {
                'device_name': f"{client.display_name}'s Device",
                'device_type': 'other',
                'device_platform': 'other',
                'is_trusted': True,
                'status': 'active',
            }
            
            # Only add location if it's a real Location instance
            if hasattr(detected_location, 'id'):
                device_data['last_seen_location_id'] = detected_location.id
            
            device, device_created = UserDevice.objects.get_or_create(
                mac_address=current_mac,
                user=client,
                defaults=device_data
            )
            
            # Update device presence with detected location
            if current_ip and hasattr(device, 'update_presence'):
                try:
                    device.update_presence(
                        ip_address=current_ip,
                        location=detected_location
                    )
                except Exception as e:
                    print(f"Device presence update error: {e}")
                    # Continue without device presence update

        # Create authentication token
        token, _ = Token.objects.get_or_create(user=user)

        return user, client, (user_created or client_created), token.key