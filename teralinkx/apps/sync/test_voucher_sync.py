"""
Test script for voucher device tracking sync
Run: python manage.py shell < apps/sync/test_voucher_sync.py
"""
from users.models import UserSession, UserDevice, ClientH
from packages.models import DispatchVoucher
from django.utils import timezone

def test_sync_logic():
    """Test the sync logic with sample data"""
    
    print("\n=== Testing Voucher Device Sync Logic ===\n")
    
    # Simulate RADIUS response
    radius_data = {
        'mac_address': '00:11:22:33:44:55',
        'ip_address': '10.0.0.100',
        'session_id': 'test-session-123'
    }
    
    # Test 1: Device doesn't exist
    print("Test 1: New device (should create)")
    device = UserDevice.objects.filter(mac_address=radius_data['mac_address']).first()
    print(f"  Device exists: {device is not None}")
    
    if not device:
        print("  ✓ Will create new device")
    
    # Test 2: Device exists with owner
    print("\nTest 2: Existing device (should use owner)")
    # Create test device if needed
    test_user = ClientH.objects.first()
    if test_user and not device:
        device = UserDevice.objects.create(
            mac_address=radius_data['mac_address'],
            user=test_user,
            device_name='Test Device'
        )
        print(f"  Created test device for user: {test_user.account}")
    
    if device:
        print(f"  Device owner: {device.user.account}")
        print(f"  ✓ Will use device owner as session user")
    
    # Test 3: Session creation
    print("\nTest 3: Session creation")
    voucher = DispatchVoucher.objects.filter(status='active').first()
    
    if voucher:
        print(f"  Voucher: {voucher.voucher_code}")
        print(f"  Voucher owner: {voucher.user.client_profile.account}")
        
        if device:
            print(f"  Device owner: {device.user.account}")
            print(f"  Session will be created for: {device.user.account}")
            
            if device.user != voucher.user.client_profile:
                print("  ⚠ Device owner != Voucher owner (borrowed device)")
            else:
                print("  ✓ Device owner == Voucher owner")
    
    # Test 4: Query sessions by voucher
    print("\nTest 4: Query sessions by voucher")
    if voucher:
        sessions = UserSession.objects.filter(
            active_voucher=voucher.voucher_code,
            session_type='voucher'
        ).select_related('device', 'user')
        
        print(f"  Found {sessions.count()} sessions")
        for session in sessions[:3]:
            print(f"    - {session.user.account} | {session.device.mac_address} | {session.ip_address}")
    
    print("\n=== Test Complete ===\n")

if __name__ == '__main__':
    test_sync_logic()
