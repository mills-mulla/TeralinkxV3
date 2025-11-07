# core/tasks.py

from celery import shared_task, group
from core.models import *
from core.views.moitoring import monitor_user
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

@shared_task
def task_query_unprocessed_checkoutrqs():
    from .scheduler import task_query_unprocessed_checkoutrqs
    task_query_unprocessed_checkoutrqs()

@shared_task
def task_check_voucher_expiry():
    from .scheduler import check_voucher_expiry
    check_voucher_expiry()

@shared_task
def task_check_session_expiry():
    from .scheduler import ckeck_session_expiry
    ckeck_session_expiry()

@shared_task
def task_update_dhcp_model():
    from .scheduler import update_dhcp_model
    update_dhcp_model()

@shared_task
def task_update_active_users():
    from .scheduler import task_update_active_users
    task_update_active_users()

@shared_task
def task_delete_pending():
    from .scheduler import delete_pending
    delete_pending()

BATCH_SIZE = 100  # adjust based on your server/API load

@shared_task
def process_dispatch_voucher_batch(voucher_ids):
    """
    Updates a batch of DispatchVoucher records.
    """
    vouchers = DispatchVoucher.objects.filter(dispatch_id__in=voucher_ids)

    for voucher in vouchers:
        try:
            stats = monitor_user(voucher.usermanid)
            if stats:
                # Store as decimals (MB) for proper math
                voucher.total_download = Decimal(str(int(stats['total_download']) / (1024 * 1024)))
                voucher.total_upload = Decimal(str(int(stats['total_upload']) / (1024 * 1024)))
                voucher.uptime = int(stats['uptime'])
                voucher.active_sessions = stats['active_sessions']
                voucher.save(update_fields=['total_download', 'total_upload', 'uptime', 'active_sessions'])
                logging.info(f"Updated usage for {voucher.dispatch_voucher_code}")
            else:
                logging.warning(f"No stats returned for {voucher.usermanid}")
        except Exception as e:
            logging.error(f"Failed to update {voucher.dispatch_voucher_code}: {e}")

@shared_task
def update_all_dispatch_voucher_usage():
    """
    Split all vouchers into batches and run tasks in parallel.
    """
    vouchers = DispatchVoucher.objects.filter(usermanid__isnull=False).values_list('dispatch_id', flat=True)
    # Split into batches
    batches = [vouchers[i:i + BATCH_SIZE] for i in range(0, len(vouchers), BATCH_SIZE)]
    
    job = group(process_dispatch_voucher_batch.s(list(batch)) for batch in batches)
    job.apply_async()



from .utils.pusher_notifier import send_notification

@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def push_notification_task(self, channel, event, payload):
    try:
        send_notification(channel, event, payload)
    except Exception as exc:
        # Retry up to 3 times with 5s delay
        raise self.retry(exc=exc)
    
@shared_task
def mark_dispatch_as_expired(voucher_id):
    try:
        voucher = DispatchVoucher.objects.get(dispatch_id=voucher_id)
        if voucher.dispatch_status != "expired":
            voucher.dispatch_status = "expired"
            voucher.save(update_fields=["dispatch_status"])
            return f"Voucher {voucher_id} marked as expired."
        return f"Voucher {voucher_id} already expired."
    except DispatchVoucher.DoesNotExist:
        return f"Voucher {voucher_id} not found."