# core/tasks.py

from celery import shared_task, group
from core.models import *
# from core.views.moitoring import monitor_user
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

@shared_task(bind=True, soft_time_limit=300, time_limit=600)
def task_query_pending_transactions(self):
    """Query M-Pesa for pending transactions older than 1 minute"""
    try:
        from django.utils import timezone
        from datetime import timedelta
        from finance.models import TransactionQueue, BalanceTransaction
        from finance.queryDaraja import query_stk_status
        from decimal import Decimal
        
        # Get pending transactions older than 1 minute
        one_minute_ago = timezone.now() - timedelta(minutes=1)
        pending_transactions = TransactionQueue.objects.filter(
            status='pending',
            created_at__lte=one_minute_ago,
            checkout_request_id__isnull=False
        ).exclude(checkout_request_id='')[:50]  # Limit to 50 per run
        
        if not pending_transactions.exists():
            logger.info("No pending transactions to query")
            return {'queried': 0, 'completed': 0, 'failed': 0}
        
        queried = 0
        completed = 0
        failed = 0
        
        for transaction in pending_transactions:
            try:
                # Use existing queryDaraja function
                result = query_stk_status(transaction.checkout_request_id)
                queried += 1
                
                # Check result
                result_code = str(result.get('ResultCode', ''))
                
                if result_code == '0':  # Success
                    client = transaction.user
                    amount = Decimal(str(transaction.price))
                    balance_before = client.balance
                    
                    # Credit account
                    client.balance += amount
                    client.save()
                    
                    # Create balance transaction record
                    BalanceTransaction.objects.create(
                        user=client,
                        transaction_type='topup',
                        credit=amount,
                        debit=0,
                        balance_before=balance_before,
                        balance_after=client.balance,
                        description=f'M-Pesa payment - {transaction.checkout_request_id}',
                        reference=transaction.checkout_request_id
                    )
                    
                    transaction.mark_completed()
                    completed += 1
                    logger.info(f"✓ Transaction {transaction.checkout_request_id} completed - Credited {amount} to {client.account}")
                    
                elif result_code in ['1032', '1037', '1']:  # Cancelled, timeout, or insufficient funds
                    transaction.mark_failed(
                        reason=result.get('ResultDesc', 'Transaction failed'),
                        error_code=result_code,
                        failure_category='user_error'
                    )
                    failed += 1
                    logger.warning(f"✗ Transaction {transaction.checkout_request_id} failed: {result.get('ResultDesc')}")
                    
            except Exception as e:
                logger.error(f"Error querying transaction {transaction.checkout_request_id}: {e}")
                continue
        
        result = {'queried': queried, 'completed': completed, 'failed': failed}
        logger.info(f"Pending transaction query complete: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in task_query_pending_transactions: {e}")
        return {'error': str(e)}
    finally:
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



# ============================================================================
# RADIUS USAGE SYNC TASKS
# ============================================================================

@shared_task(bind=True, soft_time_limit=300, time_limit=600)
def sync_radius_usage_all(self):
    """Sync usage for all active vouchers from FreeRADIUS (every 5 minutes)"""
    try:
        from .radius_sync import RadiusUsageSyncService
        from .radius_session_sync import RadiusSessionSyncService
        
        # Sync usage data (download/upload bytes)
        usage_result = RadiusUsageSyncService.sync_active_vouchers()
        logger.info(f"Radius usage sync complete: {usage_result}")
        
        # Sync session data (create UserSession records)
        session_result = RadiusSessionSyncService.sync_all_active_vouchers()
        logger.info(f"Radius session sync complete: {session_result}")
        
        return {'usage': usage_result, 'sessions': session_result}
    except Exception as e:
        logger.error(f"Radius sync failed: {e}")
        raise
    finally:
        import gc
        gc.collect()


@shared_task(bind=True, soft_time_limit=180, time_limit=300)
def sync_radius_usage_critical(self):
    """Sync usage for critical vouchers (>80% data used) (every 2 minutes)"""
    try:
        from .radius_sync import RadiusUsageSyncService
        result = RadiusUsageSyncService.sync_critical_vouchers()
        logger.info(f"Critical radius sync complete: {result}")
        return result
    except Exception as e:
        logger.error(f"Critical radius sync failed: {e}")
        raise
    finally:
        import gc
        gc.collect()