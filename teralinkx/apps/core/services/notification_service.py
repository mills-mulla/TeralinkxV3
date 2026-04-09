# notifications.py
from notifications.models import Notification
from ..utils.pusher_notifier import send_notification
from sync.tasks import push_notification_task


def create_and_notify(user, message, type, extra_data=None):
    if not user or not hasattr(user, "id"):
        print("⚠️ Skipping notification: invalid user")
        return None

    # Get the actual User instance if user is ClientH
    if hasattr(user, 'user'):
        actual_user = user.user
    else:
        actual_user = user

    # Save to DB immediately
    notification = Notification.objects.create(user=actual_user, message=message)

    # Build payload
    payload = {"message": message, "type": type}
    if extra_data:
        payload.update(extra_data)

    channel = f"user-{actual_user.id}"

    # Queue the Celery task (non-blocking)
    push_notification_task.delay(channel, "new-alert", payload)

    return notification

# def create_and_notify(user, message, type, extra_data=None):
#     if not user or not hasattr(user, "id"):
#         print("⚠️ Skipping notification: invalid user")
#         return None

#     # save notification in DB
#     notification = Notification.objects.create(user=user, message=message)

#     # Construct payload
#     payload = {"message": message, "type": type}
#     if extra_data:
#         payload.update(extra_data)

#     channel = f"user-{user.id}"

#     # Fire-and-forget push to Pusher
#     try:
#         send_notification(channel, "new-alert", payload)
#     except Exception as e:
#         # Log but don’t break purchase process
#         print(f"⚠️ Failed to send Pusher notification: {e}")

#     return notification
