# Pusher Real-Time Notifications Setup

## Backend Setup (Already Configured)

The backend is already set up with Pusher integration:

- **Pusher Client**: `/apps/core/utils/pusher_notifier.py`
- **Notification Service**: `/apps/core/services/notification_service.py`
- **Settings**: Configure in Django settings

### Django Settings Required

Add to your `settings.py`:

```python
# Pusher Configuration
PUSHER_APP_ID = 'your_app_id'
PUSHER_KEY = 'your_key'
PUSHER_SECRET = 'your_secret'
PUSHER_CLUSTER = 'mt1'  # or your cluster
PUSHER_SSL = True
```

## Frontend Setup

### 1. Install Pusher JS

```bash
cd admteralinkx/adminstration
npm install pusher-js
```

### 2. Configure Environment Variables

Create `.env` file in `admteralinkx/adminstration/`:

```env
VITE_PUSHER_KEY=your_pusher_key_here
VITE_PUSHER_CLUSTER=mt1
```

### 3. Files Created

- **Composable**: `src/composables/usePusher.js` - Pusher connection management
- **Component**: `src/components/RealTimeNotifications.vue` - Toast notifications
- **Integration**: Added to `App.vue`

## Usage

### Backend - Sending Notifications

```python
from apps.core.services.notification_service import create_and_notify

# Send notification to specific user
create_and_notify(
    user=user_instance,
    message="Payment received successfully",
    type="success",
    extra_data={"amount": 100, "transaction_id": "TXN123"}
)
```

### Backend - Broadcasting to Admin Channel

```python
from apps.core.utils.pusher_notifier import send_notification

# Broadcast to all admins
send_notification(
    channel='admin-notifications',
    event='new-alert',
    payload={
        'message': 'New user registered',
        'type': 'info',
        'details': 'John Doe just signed up'
    }
)
```

### Frontend - Custom Channels

```javascript
import { usePusher } from '@/composables/usePusher'

const { initPusher, subscribe } = usePusher()

// Initialize
initPusher(userId)

// Subscribe to custom channel
subscribe('custom-channel', 'custom-event', (data) => {
  console.log('Received:', data)
})
```

## Notification Types

- **success**: Green checkmark icon
- **error**: Red error icon
- **warning**: Yellow warning icon
- **info**: Blue info icon (default)

## Channels

- `user-{userId}`: User-specific notifications
- `admin-notifications`: Global admin notifications
- Custom channels as needed

## Testing

### Test Backend

```python
# In Django shell
from apps.core.utils.pusher_notifier import send_notification

send_notification(
    'admin-notifications',
    'new-alert',
    {'message': 'Test notification', 'type': 'success'}
)
```

### Test Frontend

Open browser console and check for:
- `✅ Pusher connected`
- Notifications appearing in top-right corner

## Auto-dismiss

Notifications automatically dismiss after 5 seconds. Users can also manually close them.

## Next Steps

1. Get Pusher credentials from https://pusher.com
2. Add credentials to Django settings and frontend .env
3. Integrate notification triggers in your business logic
4. Customize notification appearance as needed
