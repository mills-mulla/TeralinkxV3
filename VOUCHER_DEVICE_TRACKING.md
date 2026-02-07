# Voucher Device Tracking Implementation Summary

## Overview
Integration of RADIUS accounting data with UserSession model for real-time voucher device tracking.

## Flow

### 1. CELERY SYNC (Periodic Task)
```python
# Gets RADIUS data from API
- mac_address
- ip_address  
- session_id (acctsessionid)
- start_time (acctstarttime)
- stop_time (acctstoptime)
- total_bytes (usage)
```

### 2. UPDATE DISPATCH VOUCHER
```python
# Your existing code updates:
- total_download
- total_upload
- session_count
```

### 3. UPDATE/CREATE USER SESSION
```python
# Query by session_id (unique RADIUS identifier)
session = UserSession.objects.filter(session_id=radius_session_id).first()

if session:
    # UPDATE existing
    session.data_used = total_usage
    session.voucher_activated = session_start  # acctstarttime
    session.last_activity = session_stop       # acctstoptime
    session.ip_address = ip_address
    session.is_active = True
else:
    # CREATE new
    device = UserDevice.get(mac_address=mac)  # Find device owner
    UserSession.create(
        session_id=radius_session_id,
        user=device.user,              # Device owner (not voucher owner)
        device=device,
        session_type='network',        # Network connection
        active_voucher=voucher_code,
        voucher_activated=session_start,
        last_activity=session_stop,
        data_used=total_usage
    )
```

### 4. FRONTEND QUERY
```python
# Get all sessions for a voucher
sessions = UserSession.objects.filter(
    active_voucher='VOUCHER123',
    session_type='network'
).select_related('device', 'user')

# Now you know:
for session in sessions:
    print(f"Device: {session.device.mac_address}")
    print(f"Owner: {session.user.account}")
    print(f"IP: {session.ip_address}")
    print(f"Started: {session.voucher_activated}")
    print(f"Last seen: {session.last_activity}")
    print(f"Data used: {session.data_used}")
```

## Key Features

### ✅ session_id as Primary Key
- Uses RADIUS acctsessionid
- Unique & indexed for fast lookups
- No conflicts with MAC+voucher queries

### ✅ Device Owner Tracking
- Finds device by MAC
- Uses device owner as session user
- Handles borrowed devices correctly

### ✅ Session Type
- `session_type='network'` for RADIUS sessions
- `session_type='voucher'` for manual voucher activation
- `session_type='web'` for web authentication

### ✅ Time Tracking
- `voucher_activated` = session start (acctstarttime)
- `last_activity` = session stop/update (acctstoptime)
- `login_time` = when session record created

### ✅ Stale Session Cleanup
- Deactivates sessions no longer in RADIUS
- Matches by MAC address

## Files Modified

1. `/apps/sync/radius_session_sync.py` - Production sync service
2. `/apps/users/models.py` - Fixed deactivate_voucher method
3. `/apps/sync/test_radius_session_sync.py` - Test service (dry-run)
4. `/apps/sync/test_voucher_sync.py` - Unit test script

## Testing

### Dry Run Test
```bash
docker exec teralinkx_web python manage.py shell
```

```python
from apps.sync.test_radius_session_sync import TestRadiusSessionSyncService

# Test with dry_run=True (no changes)
TestRadiusSessionSyncService.test_sync_voucher_sessions('VOUCHER_CODE', dry_run=True)

# Test with actual writes
TestRadiusSessionSyncService.test_sync_voucher_sessions('VOUCHER_CODE', dry_run=False)
```

### Production Sync
```python
from apps.sync.radius_session_sync import RadiusSessionSyncService

# Sync single voucher
RadiusSessionSyncService.sync_voucher_sessions('VOUCHER_CODE')

# Sync all active vouchers
result = RadiusSessionSyncService.sync_all_active_vouchers()
print(f"Synced: {result['synced']}, Failed: {result['failed']}")
```

## Next Steps

1. ✅ Test with real RADIUS data
2. ✅ Verify device matching works correctly
3. ✅ Check frontend queries return expected data
4. ⏳ Add to Celery periodic tasks
5. ⏳ Monitor sync performance
6. ⏳ Add error notifications

## Benefits

- Real-time voucher device tracking
- No data duplication
- Accurate device owner identification
- Historical session data
- Easy frontend queries
- Scalable architecture
