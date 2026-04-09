# apps/sync/test_radius_session_sync.py
"""
TEST VERSION - Sync RADIUS accounting sessions to UserSession model
This version logs actions without modifying data
"""
import logging
import requests
from django.conf import settings
from django.utils import timezone
from users.models import UserSession, UserDevice, ClientH
from packages.models import DispatchVoucher

logger = logging.getLogger(__name__)

RADIUS_API_URL = getattr(settings, 'RADIUS_API_URL', 'http://radiusapi:8010/api')


class TestRadiusSessionSyncService:
    """TEST VERSION - Sync RADIUS sessions to UserSession model"""
    
    @classmethod
    def test_sync_voucher_sessions(cls, voucher_code, dry_run=True):
        """Test sync for a single voucher"""
        print(f"\n{'='*60}")
        print(f"Testing sync for voucher: {voucher_code}")
        print(f"Dry run: {dry_run}")
        print(f"{'='*60}\n")
        
        try:
            voucher = DispatchVoucher.objects.get(voucher_code=voucher_code)
            print(f"✓ Found voucher: {voucher.voucher_code}")
            print(f"  Owner: {voucher.user.client_profile.account}")
            print(f"  Status: {voucher.status}")
            print(f"  Location: {voucher.location}")
            
            # Get active RADIUS sessions
            print(f"\n→ Calling RADIUS API...")
            response = requests.post(
                f'{RADIUS_API_URL}/vouchers/usage/batch/',
                json={'usernames': [voucher_code]},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"✗ API Error: {response.status_code}")
                return False
            
            data = response.json()
            result = data.get('results', [{}])[0]
            active_devices = result.get('active_devices', [])
            
            print(f"✓ Found {len(active_devices)} active devices\n")
            
            # Process each device
            for idx, device_data in enumerate(active_devices, 1):
                print(f"Device {idx}:")
                cls._test_sync_device(voucher, device_data, dry_run)
                print()
            
            # Check for stale sessions
            cls._test_cleanup_stale(voucher, active_devices, dry_run)
            
            print(f"{'='*60}")
            print("Test complete!")
            print(f"{'='*60}\n")
            return True
            
        except DispatchVoucher.DoesNotExist:
            print(f"✗ Voucher {voucher_code} not found")
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @classmethod
    def _test_sync_device(cls, voucher, device_data, dry_run):
        """Test sync for single device"""
        mac = device_data.get('mac_address')
        ip = device_data.get('ip_address')
        session_id = device_data.get('session_id')
        
        print(f"  MAC: {mac}")
        print(f"  IP: {ip}")
        print(f"  Session ID: {session_id}")
        
        if not mac or not ip:
            print("  ✗ Missing MAC or IP")
            return
        
        # Find device
        device = UserDevice.objects.filter(mac_address=mac).first()
        
        if device:
            print(f"  ✓ Device found: {device.device_name}")
            print(f"    Owner: {device.user.account}")
            session_user = device.user
        else:
            print(f"  → Device not found, will create for voucher owner")
            session_user = voucher.user.client_profile
        
        # Check session
        session = UserSession.objects.filter(session_id=session_id).first()
        
        if session:
            print(f"  ✓ Session exists: {session.session_id[:16]}...")
            print(f"    Current user: {session.user.account}")
            print(f"    Current voucher: {session.active_voucher}")
            print(f"    Active: {session.is_active}")
            
            if not dry_run:
                print("  → Would UPDATE session")
        else:
            print(f"  → Session not found, will create")
            print(f"    User: {session_user.account}")
            print(f"    Voucher: {voucher.voucher_code}")
            
            if not dry_run:
                print("  → Would CREATE session")
        
        # Show what would be saved
        print(f"  Data to save:")
        print(f"    - user: {session_user.account}")
        print(f"    - device: {device.device_name if device else 'NEW'}")
        print(f"    - ip: {ip}")
        print(f"    - voucher: {voucher.voucher_code}")
        print(f"    - session_type: voucher")
        print(f"    - is_active: True")
    
    @classmethod
    def _test_cleanup_stale(cls, voucher, active_devices, dry_run):
        """Test cleanup of stale sessions"""
        active_ids = [d.get('session_id') for d in active_devices if d.get('session_id')]
        
        stale = UserSession.objects.filter(
            active_voucher=voucher.voucher_code,
            session_type='voucher',
            is_active=True
        ).exclude(session_id__in=active_ids)
        
        count = stale.count()
        print(f"Stale sessions check:")
        print(f"  Active RADIUS sessions: {len(active_ids)}")
        print(f"  Stale UserSessions: {count}")
        
        if count > 0:
            for session in stale:
                print(f"    - {session.session_id[:16]}... | {session.device.mac_address}")
            
            if not dry_run:
                print(f"  → Would DEACTIVATE {count} sessions")
        else:
            print(f"  ✓ No stale sessions")


# Quick test function
def quick_test(voucher_code):
    """Quick test for a voucher"""
    service = TestRadiusSessionSyncService()
    service.test_sync_voucher_sessions(voucher_code, dry_run=True)


if __name__ == '__main__':
    print("Test Radius Session Sync Service")
    print("Usage: quick_test('VOUCHER_CODE')")
