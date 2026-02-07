# FreeRADIUS Voucher System - Complete Guide

## Overview
Time-based voucher system where validity counts from **first login**, not per-session.

## How It Works

### 1. Voucher Creation
```bash
curl -X POST http://192.168.88.16:8010/api/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "VOUCHER123",
    "profile": "30Min",
    "is_voucher": true,
    "duration_seconds": 1800
  }'
```

### 2. First Login (Activation)
- User connects: `freeradtester` / `freeradtester`
- Python module detects first login
- Sets `activated_at` = NOW
- Sets `expires_at` = NOW + 1800 seconds
- **Authentication: ACCEPT**

### 3. Subsequent Logins (Within 30 min)
- User reconnects
- Python module checks `expires_at`
- If NOW < `expires_at`: **ACCEPT**
- Remaining time logged

### 4. After Expiry
- User tries to connect
- Python module checks `expires_at`
- If NOW > `expires_at`: **REJECT**
- Voucher marked as `is_active = false`

## Test User

**Username**: `freeradtester`
**Password**: `freeradtester`
**Profile**: 30Min (10Mbps, 30 minutes from first login)
**Status**: Not activated yet

## Voucher Flow

```
Create Voucher → First Login (Activate) → Use Within 30min → Expired → Rejected
     ↓               ↓                          ↓                ↓
  API Call      activated_at set         Can reconnect     Cannot login
                expires_at set           multiple times     anymore
```

## Database Tables

### vouchers
- `username` - Voucher code
- `profile` - Speed/limit profile
- `duration_seconds` - Validity period
- `activated_at` - First login timestamp
- `expires_at` - Expiry timestamp
- `is_active` - Enabled/disabled flag

### radcheck
- Standard RADIUS user credentials

### radusergroup
- Links user to profile

## API Endpoints

### Create Voucher User
`POST /api/users/`
```json
{
  "username": "VOUCHER123",
  "profile": "30Min",
  "is_voucher": true,
  "duration_seconds": 1800
}
```

### Check Voucher Status
```sql
SELECT username, activated_at, expires_at, is_active 
FROM vouchers 
WHERE username='freeradtester';
```

## FreeRADIUS Components

### Python Module
- **File**: `/etc/freeradius/3.0/mods-config/python/voucher_check.py`
- **Function**: Checks voucher expiry on authorization
- **Database**: Connects to PostgreSQL to check/update vouchers

### Module Config
- **File**: `/etc/freeradius/mods-available/python_voucher`
- **Enabled**: Symlinked to `mods-enabled/`

## Testing

1. **Create voucher** (done ✅)
2. **Connect from MikroTik** with `freeradtester`/`freeradtester`
3. **Check activation**:
   ```sql
   SELECT * FROM vouchers WHERE username='freeradtester';
   ```
4. **Wait 30 minutes** or manually set expiry:
   ```sql
   UPDATE vouchers 
   SET expires_at = NOW() - INTERVAL '1 minute' 
   WHERE username='freeradtester';
   ```
5. **Try to reconnect** → Should be REJECTED

## Advantages

✅ **Absolute expiry** - Time counts from first use
✅ **One-time voucher** - Cannot reuse after expiry
✅ **Reconnect allowed** - Can disconnect/reconnect within validity
✅ **Automatic enforcement** - FreeRADIUS handles rejection
✅ **Database tracked** - Full audit trail

## Next Steps

- Test with `freeradtester` user
- Monitor FreeRADIUS logs for voucher activation
- Integrate with V3 voucher generation
- Add voucher status API endpoint
