# apps/sync/radius_session_sync.py
"""
Sync RADIUS accounting sessions to UserSession model
"""
import logging
import requests
from django.conf import settings
from django.utils import timezone
from users.models import UserSession, UserDevice, ClientH
from packages.models import DispatchVoucher

logger = logging.getLogger(__name__)

RADIUS_API_URL = getattr(settings, 'RADIUS_API_URL', 'http://radiusapi:8010/api')


class RadiusSessionSyncService:
    """Sync RADIUS sessions to UserSession model"""
    
    @classmethod
    def sync_all_active_vouchers(cls):
        """Sync all active vouchers' RADIUS sessions"""
        active_vouchers = DispatchVoucher.objects.filter(status='active')
        synced = 0
        failed = 0
        
        for voucher in active_vouchers:
            if cls.sync_voucher_sessions(voucher.voucher_code):
                synced += 1
            else:
                failed += 1
        
        return {'synced': synced, 'failed': failed, 'total': active_vouchers.count()}
    
    @classmethod
    def sync_voucher_sessions(cls, voucher_code):
        """Sync all RADIUS sessions for a voucher to UserSession"""
        try:
            voucher = DispatchVoucher.objects.get(voucher_code=voucher_code)
            
            # Get active RADIUS sessions from API
            response = requests.post(
                f'{RADIUS_API_URL}/vouchers/usage/batch/',
                json={'usernames': [voucher_code]},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to get RADIUS sessions for {voucher_code}")
                return False
            
            data = response.json()
            if not data.get('results'):
                return True
            
            result = data['results'][0]
            active_devices = result.get('active_devices', [])
            stopped_sessions = result.get('stopped_sessions', [])
            
            # Sync each active device to UserSession
            for device_data in active_devices:
                cls._sync_device_session(voucher, device_data, is_active=True)
            
            # Sync stopped sessions with final data
            for device_data in stopped_sessions:
                cls._sync_device_session(voucher, device_data, is_active=False)
            
            # Mark sessions as inactive if not in active_devices or stopped_sessions
            active_session_ids = [d.get('session_id') for d in active_devices]
            stopped_session_ids = [d.get('session_id') for d in stopped_sessions]
            all_synced_session_ids = active_session_ids + stopped_session_ids
            
            UserSession.objects.filter(
                active_voucher=voucher_code,
                session_type='network',
                is_active=True
            ).exclude(
                session_id__in=all_synced_session_ids
            ).update(is_active=False)
            
            # Update session_count: count distinct active devices (MACs)
            unique_active_macs = set(d.get('mac_address') for d in active_devices if d.get('mac_address'))
            voucher.session_count = len(unique_active_macs)
            voucher.save(update_fields=['session_count'])
            logger.info(f"✅ Updated {voucher_code} session_count to {voucher.session_count} (distinct devices)")
            
            return True
            
        except DispatchVoucher.DoesNotExist:
            logger.error(f"Voucher {voucher_code} not found")
            return False
        except Exception as e:
            logger.error(f"Failed to sync sessions for {voucher_code}: {e}")
            return False
    
    @classmethod
    def _sync_device_session(cls, voucher, device_data, is_active=True):
        """Sync single device session from RADIUS to UserSession"""
        mac_address = device_data.get('mac_address')
        ip_address = device_data.get('ip_address')
        radius_session_id = device_data.get('session_id')
        login_time = device_data.get('login_time')
        total_octets = device_data.get('total_octets', 0)
        
        if not mac_address or not radius_session_id:
            return
        
        # Find device by MAC
        device = UserDevice.objects.filter(mac_address=mac_address).first()
        
        if not device:
            device = UserDevice.objects.create(
                mac_address=mac_address,
                user=voucher.user.client_profile,
                device_name=f'Device {mac_address[-8:]}',
                device_type='other'
            )
        
        session_user = device.user
        
        # Query by session_id
        session = UserSession.objects.filter(session_id=radius_session_id).first()
        
        if session:
            # UPDATE existing
            session.ip_address = ip_address
            session.is_active = is_active
            session.data_used = total_octets
            session.last_activity = timezone.now()
            session.save()
        else:
            # CREATE new
            UserSession.objects.create(
                user=session_user,
                device=device,
                session_id=radius_session_id,
                ip_address=ip_address,
                location=voucher.location,
                active_voucher=voucher.voucher_code,
                voucher_activated=login_time,
                session_type='network',
                data_used=total_octets,
                is_active=is_active
            )

