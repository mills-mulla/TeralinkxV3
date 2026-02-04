import logging
from django.utils import timezone
from .authentications import who, TeralinkxWaves, how
from .helpers import get_db_url,check_expired_vouchers
from decimal import Decimal
from celery import shared_task
from .models import ClientH,DispatchVoucher,ActiveUser,DHCPLease , alternateSessions
from apps.finance.models import TransactionQueue
from .views.queryDaraja import query_stk_status
from django.db import transaction
from .views.moitoring import monitor_user
from django.db.models import F
from .router.ros_api.api import Api
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)

@shared_task
def update_voucher_usage():
    for voucher in DispatchVoucher.objects.filter(dispatch_status='active'):
        stats = monitor_user(voucher.usermanid)  # returns dict
        if stats:
            voucher.uptime = stats['uptime']
            voucher.total_download = stats['total_download']
            voucher.total_upload = stats['total_upload']
            voucher.active_sessions = stats['active_sessions']
            voucher.save()



@shared_task
def task_query_unprocessed_checkoutrqs():
    """
    Checks for unprocessed M-Pesa transactions in the queue.
    
    If transactions have been pending for more than 2 minutes, 
    it queries their status. Successful transactions will have
    their status updated to 'refunded', and the respective client 
    will have their balance updated accordingly.
    """
    pending_transactions = get_pending_transactions()

    if not pending_transactions:
        logger.info("No unprocessed transactions found.")
        return

    for queue_record in pending_transactions:
        process_transaction(queue_record)


def get_pending_transactions():
    """
    Retrieves a list of pending transactions from the TransactionQueue.

    Returns:
        list: Pending transaction records.
    """
    return TransactionQueue.objects.filter(method='mpesa', status__in=['pending', 'Pending...'])


def process_transaction(queue_record):
    """
    Processes a single transaction record.

    Args:
        queue_record (Queue): The transaction record to process.
    """
    if is_transaction_expired(queue_record):
        try:
            response_data = query_stk_status(queue_record.checkout_request_id)
            if response_data.get('ResultCode') == "0":
                refund_transaction(queue_record)
        except Exception as e:
            logger.error(f"Error querying transaction {queue_record.checkout_request_id}: {e}")
    else:
        logger.info(f"Transaction {queue_record.checkout_request_id} is still within the processing window.")


def is_transaction_expired(queue_record):
    """
    Checks if the transaction has been pending for more than 2 minutes.

    Args:
        queue_record (TransactionQueue): The transaction record to check.

    Returns:
        bool: True if the transaction is expired, False otherwise.
    """
    return timezone.now() > queue_record.created_at + timezone.timedelta(minutes=2)

def refund_transaction(queue_record):
    """
    Refunds the transaction and updates the client's balance.

    Args:
        queue_record (TransactionQueue): The transaction record to refund.
    """
    try:
        # Retrieve the client
        client = ClientH.objects.get(account=queue_record.recipient)
        
        with transaction.atomic():
            if queue_record.status != "refunded":
                queue_record.status = "refunded"
                queue_record.save()
                
                if queue_record.price is not None and queue_record.price > Decimal("0"):
                    client.add_balance(Decimal(queue_record.price))
                    logger.info(f"💰 Refunded {queue_record.price} to user {queue_record.recipient}")
            else:
                logger.warning(f"Attempted to refund an already refunded transaction: {queue_record.id}")
                
    except ObjectDoesNotExist:
        logger.error(f"Client with account {queue_record.recipient} does not exist.")
    except Exception as e:
        logger.error(f"An error occurred during the refund process: {str(e)}")



@shared_task
def task_check_voucher_expiry():
    check_expired_vouchers()


@shared_task
def task_check_session_expiry():
    now = timezone.now()
    expired_sessions = alternateSessions.objects.filter(last_login__lte=now - F('session_timeout'))
    count = expired_sessions.count()
    expired_sessions.delete()
    logger.info(f"Deleted {count} expired sessions.")


@shared_task
def task_update_dhcp_model():
    try:
        router = Api(TeralinkxWaves, user=who, password=how, port=8728, verbose=True)
        dhcpleases = router.talk('/ip/dhcp-server/lease/print')

        with transaction.atomic():
            existing_leases = {lease.mac_address: lease for lease in DHCPLease.objects.all()}
            new_leases = []

            for lease_data in dhcpleases:
                mac = lease_data.get('mac-address')
                defaults = {...}  # (same as before)
                if mac in existing_leases:
                    lease = existing_leases.pop(mac)
                    for k, v in defaults.items(): setattr(lease, k, v)
                    lease.save()
                else:
                    new_leases.append(DHCPLease(mac_address=mac, **defaults))

            DHCPLease.objects.filter(mac_address__in=existing_leases).delete()
            DHCPLease.objects.bulk_create(new_leases)
        logger.info("DHCP leases updated successfully.")
    except Exception as e:
        logger.error(f"Error updating DHCP leases: {e}")

@shared_task
def task_update_active_users():
    try:
        router = Api(TeralinkxWaves, user=who, password=how, port=8728, verbose=True)
        active_users = router.talk('/ip/hotspot/active/print')

        with transaction.atomic():
            existing_users = {u.username: u for u in ActiveUser.objects.all()}
            new_users = []

            for user_data in active_users:
                username = user_data.get("user", "")

                defaults = {
                    "idA": user_data.get(".id", ""),
                    "ip_address": user_data.get("address", ""),
                    "mac_address": user_data.get("mac-address", ""),
                    "radius": user_data.get("radius", ""),
                    "login_by": user_data.get("login-by", ""),
                    "server": user_data.get("server", ""),
                    "uptime": user_data.get("uptime", ""),
                    "idle_time": user_data.get("idle-time", ""),
                    "bytes_in": user_data.get("bytes-in", "0"),
                    "bytes_out": user_data.get("bytes-out", "0"),
                    "packets_in": user_data.get("packets-in", "0"),
                    "packets_out": user_data.get("packets-out", "0"),
                }

                if username in existing_users:
                    user = existing_users.pop(username)
                    for k, v in defaults.items():
                        setattr(user, k, v)
                    user.save()
                else:
                    new_users.append(ActiveUser(username=username, **defaults))

            # Remove users not in the router anymore
            ActiveUser.objects.filter(username__in=existing_users).delete()
            # Add new users in bulk
            ActiveUser.objects.bulk_create(new_users)

        logger.info("Active users updated successfully.")

    except Exception as e:
        logger.error(f"Error updating active users: {e}")




@shared_task
def task_delete_pending():
    deleted_count, _ = TransactionQueue.objects.filter(status__in=['pending', 'Pending...']).delete()
    logger.info(f"Deleted {deleted_count} pending records.")
