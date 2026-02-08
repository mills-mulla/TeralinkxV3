# TODO: Real-time RADIUS API Check for Reconnect

## Issue
When RECONNECT button is orange (session limit reached), user can still click it but the backend might have stale session data if Celery hasn't synced yet.

## Solution
Add logic to ReconnectAPIView to check RADIUS API directly for fresh session data before processing reconnect request.

## Implementation Steps

1. **Update ReconnectAPIView** (`/home/teralinkx/TeralinkxV3/teralinkx/apps/finance/authentications.py`)
   - Before attempting reconnect, query RADIUS API directly
   - Get fresh active_devices count for the voucher
   - Compare with package device_limit
   - If session limit truly reached, return 403 with clear message
   - If Celery data was stale and slots available, proceed with reconnect

2. **Add RADIUS API Query Helper**
   ```python
   def get_fresh_session_count(voucher_code):
       """Query RADIUS API directly for current active sessions"""
       response = requests.post(
           'http://radiusapi:8010/api/vouchers/usage/batch/',
           json={'usernames': [voucher_code]},
           timeout=5
       )
       data = response.json()
       return data['results'][0]['active_sessions']
   ```

3. **Update ReconnectAPIView Logic**
   - Check fresh session count vs device limit
   - If limit reached, return error
   - If slots available, proceed with reconnect
   - Update DispatchVoucher.session_count with fresh data

## Benefits
- Prevents false "session limit reached" errors
- Provides real-time session validation
- Better user experience when Celery sync is delayed
- Reduces support tickets for "can't reconnect" issues

## Priority
Medium - Implement after current disconnect functionality is complete

## Related Files
- `/home/teralinkx/TeralinkxV3/teralinkx/apps/finance/authentications.py` (ReconnectAPIView)
- `/home/teralinkx/TeralinkxV3/TeralinkxFR/src/components/VoucherCard.vue` (Orange RECONNECT button)
- `/home/teralinkx/TeralinkxV3/radius_api/api/views.py` (RADIUS API endpoint)

## Status
📌 PINNED - To be implemented after disconnect functionality is complete
