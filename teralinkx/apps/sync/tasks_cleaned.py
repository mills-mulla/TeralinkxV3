# core/tasks.py

from celery import shared_task
from core.models import *
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, soft_time_limit=300, time_limit=600)
def task_check_voucher_expiry(self):
    try:
        from .scheduler import check_voucher_expiry
        check_voucher_expiry()
    finally:
        import gc
        gc.collect()

@shared_task(bind=True, soft_time_limit=300, time_limit=600)
def task_check_session_expiry(self):
    try:
        from .scheduler import ckeck_session_expiry
        ckeck_session_expiry()
    finally:
        import gc
        gc.collect()

from core.utils.pusher_notifier import send_notification

@shared_task(bind=True, max_retries=3, default_retry_delay=5, soft_time_limit=60, time_limit=120)
def push_notification_task(self, channel, event, payload):
    try:
        send_notification(channel, event, payload)
    except Exception as exc:
        raise self.retry(exc=exc)
    finally:
        import gc
        gc.collect()

@shared_task(bind=True, soft_time_limit=180, time_limit=300)
def mark_dispatch_as_expired(self, voucher_id):
    try:
        voucher = DispatchVoucher.objects.get(dispatch_id=voucher_id)
        if voucher.dispatch_status != "expired":
            voucher.dispatch_status = "expired"
            voucher.save(update_fields=["dispatch_status"])
            return f"Voucher {voucher_id} marked as expired."
        return f"Voucher {voucher_id} already expired."
    except DispatchVoucher.DoesNotExist:
        return f"Voucher {voucher_id} not found."
    finally:
        import gc
        gc.collect()