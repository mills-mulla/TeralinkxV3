# core/tasks.py

from celery import shared_task, group
from core.models import *
# from core.views.moitoring import monitor_user
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

@shared_task(bind=True, soft_time_limit=300, time_limit=600)
def task_query_unprocessed_checkoutrqs(self):
    try:
        from .scheduler import task_query_unprocessed_checkoutrqs
        task_query_unprocessed_checkoutrqs()
    finally:
        # Cleanup any resources
        import gc
        gc.collect()

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

@shared_task(bind=True, soft_time_limit=300, time_limit=600)
def task_update_dhcp_model(self):
    try:
        from .scheduler import update_dhcp_model
        update_dhcp_model()
    finally:
        import gc
        gc.collect()

@shared_task(bind=True, soft_time_limit=300, time_limit=600)
def task_update_active_users(self):
    try:
        from .scheduler import task_update_active_users
        task_update_active_users()
    finally:
        import gc
        gc.collect()

@shared_task(bind=True, soft_time_limit=300, time_limit=600)
def task_delete_pending(self):
    try:
        from .scheduler import delete_pending
        delete_pending()
    finally:
        import gc
        gc.collect()

BATCH_SIZE = 100  # adjust based on your server/API load

#create monitoring  for this to work
# @shared_task
# def process_dispatch_voucher_batch(voucher_ids):
#     """
#     Updates a batch of DispatchVoucher records.
#     """
#     vouchers = DispatchVoucher.objects.filter(dispatch_id__in=voucher_ids)

#     for voucher in vouchers:
#         try:
#             stats = monitor_user(voucher.usermanid)
#             if stats:
#                 # Store as decimals (MB) for proper math
#                 voucher.total_download = Decimal(str(int(stats['total_download']) / (1024 * 1024)))
#                 voucher.total_upload = Decimal(str(int(stats['total_upload']) / (1024 * 1024)))
#                 voucher.uptime = int(stats['uptime'])
#                 voucher.active_sessions = stats['active_sessions']
#                 voucher.save(update_fields=['total_download', 'total_upload', 'uptime', 'active_sessions'])
#                 logging.info(f"Updated usage for {voucher.dispatch_voucher_code}")
#             else:
#                 logging.warning(f"No stats returned for {voucher.usermanid}")
#         except Exception as e:
#             logging.error(f"Failed to update {voucher.dispatch_voucher_code}: {e}")

@shared_task(bind=True, soft_time_limit=600, time_limit=1200)
def update_all_dispatch_voucher_usage(self):
    """
    Split all vouchers into batches and run tasks in parallel.
    """
    try:
        vouchers = DispatchVoucher.objects.filter(usermanid__isnull=False).values_list('dispatch_id', flat=True)
        # Split into batches
        batches = [vouchers[i:i + BATCH_SIZE] for i in range(0, len(vouchers), BATCH_SIZE)]
        
        job = group(process_dispatch_voucher_batch.s(list(batch)) for batch in batches)
        result = job.apply_async()
        
        # Clean up result to prevent memory accumulation
        result.forget()
        
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