# utils/pusher_notifier.py
import pusher
from django.conf import settings

pusher_client = pusher.Pusher(
    app_id=settings.PUSHER_APP_ID,
    key=settings.PUSHER_KEY,
    secret=settings.PUSHER_SECRET,
    cluster=settings.PUSHER_CLUSTER,
    ssl=settings.PUSHER_SSL,
)

def send_notification(channel, event, payload):
    pusher_client.trigger(channel, event, payload)

# def send_notification(channel, event, payload):
#     try:
#         pusher_client.trigger(channel, event, payload)
#     except Exception as e:
#         # Handle network or config issues gracefully
#         print(f"⚠️ Pusher trigger failed: {e}")
