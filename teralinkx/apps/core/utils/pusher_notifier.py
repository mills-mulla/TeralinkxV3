# utils/pusher_notifier.py
import pusher
from django.conf import settings

try:
    pusher_client = pusher.Pusher(
        app_id=settings.PUSHER_APP_ID or 'dummy',
        key=settings.PUSHER_KEY or 'dummy',
        secret=settings.PUSHER_SECRET or 'dummy',
        cluster=settings.PUSHER_CLUSTER or 'us2',
        ssl=settings.PUSHER_SSL if hasattr(settings, 'PUSHER_SSL') else True,
    )
except Exception as e:
    print(f"⚠️ Pusher initialization failed: {e}. Notifications disabled.")
    pusher_client = None

def send_notification(channel, event, payload):
    if pusher_client:
        try:
            pusher_client.trigger(channel, event, payload)
        except Exception as e:
            print(f"⚠️ Pusher trigger failed: {e}")
    else:
        print(f"⚠️ Pusher not configured. Skipping notification: {channel}/{event}")
