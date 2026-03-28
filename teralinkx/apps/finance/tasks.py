"""
Celery tasks for payment processing
Handles M-Pesa API calls asynchronously to prevent worker blocking
"""
import logging
from celery import shared_task
from django.db import transaction, connection
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2, default_retry_delay=3)
def query_payment_status(self, checkout_request_id):
    """
    Async task to query M-Pesa payment status
    Prevents Django worker blocking during status checks
    """
    from finance.queryDaraja import query_stk_status
    
    try:
        # Close any stale connections
        connection.close_if_unusable_or_obsolete()
        
        logger.info(f"Celery: Querying payment status for {checkout_request_id}")
        
        # Query M-Pesa status (can timeout/hang)
        result = query_stk_status(checkout_request_id)
        
        # Handle JsonResponse from queryDaraja
        if hasattr(result, 'content'):
            import json
            result = json.loads(result.content.decode('utf-8'))
        
        logger.info(f"Celery: Status query result - ResultCode={result.get('ResultCode')}")
        
        return {
            'success': True,
            'result': result,
            'result_code': result.get('ResultCode'),
            'message': result.get('message')
        }
        
    except Exception as e:
        logger.error(f"Celery: Status query error: {e}", exc_info=True)
        
        # Retry on failure
        try:
            raise self.retry(exc=e)
        except self.MaxRetriesExceededError:
            logger.error(f"Celery: Max retries exceeded for status query {checkout_request_id}")
            return {
                'success': False,
                'error': str(e),
                'result_code': 'ERROR'
            }
    finally:
        # Always close connection after task
        connection.close_if_unusable_or_obsolete()


@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def initiate_mpesa_stk_push(self, payment_data):
    """
    Async task to initiate M-Pesa STK push
    Returns real checkout ID from M-Pesa API
    
    Args:
        payment_data: Dict with user_id, package_code, phone, amount, etc.
    """
    from users.models import ClientH
    from finance.payment_gateway import MpesaGatewayHelper
    
    try:
        # Close any stale connections
        connection.close_if_unusable_or_obsolete()
        
        # Extract payment data
        user_id = payment_data['user_id']
        package_code = payment_data['package_code']
        initiator_phone = payment_data['initiator_phone']
        recipient_account = payment_data['recipient_account']
        package_name = payment_data['package_name']
        amount_int = payment_data['amount_int']
        
        logger.info(f"Celery: Initiating STK push for {recipient_account}")
        
        # Prepare items for M-Pesa
        items = [{
            'package': package_name,
            'pkg_code': package_code
        }]
        
        # Call M-Pesa API (this blocks Celery worker, not web worker)
        result = MpesaGatewayHelper.initiate_stk_push(
            phone=initiator_phone,
            amount=amount_int,
            account_reference=f"TERALINKX_WAVES_{recipient_account}",
            description=f"Payment for {package_name}",
            package_data=items
        )
        
        if result.get('success'):
            checkout_id = result.get('checkout_request_id')
            logger.info(f"Celery: STK push successful - checkout_id={checkout_id}")
        else:
            logger.error(f"Celery: STK push failed: {result.get('error')}")
        
        # Return result to Django view (waiting with task.get())
        return {
            'success': result.get('success'),
            'checkout_request_id': result.get('checkout_request_id'),
            'merchant_request_id': result.get('merchant_request_id'),
            'customer_message': result.get('customer_message'),
            'response_code': result.get('response_code'),
            'error': result.get('error')
        }
        
    except KeyError as e:
        logger.error(f"Celery: Missing payment data field: {e}")
        return {'success': False, 'error': f'Missing required field: {e}'}
        
    except Exception as e:
        logger.error(f"Celery: Error in STK push task: {e}", exc_info=True)
        
        # Retry on failure
        try:
            raise self.retry(exc=e)
        except self.MaxRetriesExceededError:
            logger.error(f"Celery: Max retries exceeded")
            return {'success': False, 'error': str(e)}
    finally:
        # Always close connection after task
        connection.close_if_unusable_or_obsolete()


@shared_task(bind=True, max_retries=1)
def reconcile_missed_mpesa_callbacks(self, hours_back=2):
    """
    Periodic task: runs every 30 minutes via Celery Beat.
    Queries M-Pesa Pull API for transactions whose callbacks were missed
    and populates PaymentTransaction for each recovered transaction.
    """
    from finance.payment_gateway import MpesaPullReconciliation

    try:
        connection.close_if_unusable_or_obsolete()
        logger.info("Celery: Starting M-Pesa Pull reconciliation")

        result = MpesaPullReconciliation.reconcile_missed_callbacks(hours_back=hours_back)

        logger.info(f"Celery: Reconciliation done - {result}")
        return result

    except Exception as e:
        logger.error(f"Celery: Reconciliation task error: {e}", exc_info=True)
        try:
            raise self.retry(exc=e, countdown=300)
        except self.MaxRetriesExceededError:
            return {'success': False, 'error': str(e)}
    finally:
        connection.close_if_unusable_or_obsolete()


@shared_task(bind=True, soft_time_limit=300, time_limit=600)
def check_pending_transactions(self):
    """
    Periodic task: runs every 2 minutes via Celery Beat.

    Scans TransactionQueue items that are still 'pending' after 2 minutes
    and queries Daraja for their real status.

    Outcomes:
      - ResultCode 0  → full success flow: create PaymentTransaction,
                        activate voucher, mark queue processed.
                        Identical path to querycheckout.handle_successful_payment.
      - ResultCode failure (1, 1032, 1037, 2001) → mark_failed on queue.
                        If used_credit > 0, refund credit back to user balance.
      - Still pending / unknown → leave it, will be checked again next cycle.
      - Expired queue item → mark_failed (timeout).
    """
    from finance.models import TransactionQueue
    from finance.queryDaraja import query_stk_status
    from finance.payment_gateway import (
        PaymentTransactionHelper,
        TransactionQueueHelper,
        MpesaPullReconciliation,
        NotificationHelper,
    )
    from decimal import Decimal

    try:
        connection.close_if_unusable_or_obsolete()

        cutoff = timezone.now() - timezone.timedelta(minutes=2)
        pending_qs = TransactionQueue.objects.filter(
            status='pending',
            method='mpesa',
            created_at__lte=cutoff,
            checkout_request_id__isnull=False,
        ).exclude(checkout_request_id='')[:50]

        if not pending_qs.exists():
            logger.info("check_pending_transactions: nothing to check")
            return {'queried': 0, 'completed': 0, 'failed': 0, 'skipped': 0}

        queried = completed = failed = skipped = 0

        for queue_item in pending_qs:
            try:
                # Expired items — mark failed immediately, no Daraja call
                if queue_item.is_expired:
                    queue_item.mark_pending_timeout_failure()
                    failed += 1
                    continue

                result = query_stk_status(queue_item.checkout_request_id)
                # query_stk_status may return a JsonResponse or dict
                if hasattr(result, 'content'):
                    import json as _json
                    result = _json.loads(result.content.decode())

                queried += 1
                result_code = str(result.get('ResultCode', ''))

                if result_code == '0':
                    # ── Atomic claim ──────────────────────────────────────────
                    if not queue_item.mark_processing():
                        logger.info(
                            f"check_pending_transactions: queue {queue_item.id} "
                            "already claimed, skipping"
                        )
                        skipped += 1
                        continue

                    # ── Build a synthetic callback payload from Daraja result ─
                    # query_stk_status returns the same shape as a callback
                    # CallbackMetadata so we can reuse the existing helper.
                    synthetic_callback = {
                        'Body': {
                            'stkCallback': {
                                'MerchantRequestID': result.get('MerchantRequestID', ''),
                                'CheckoutRequestID': queue_item.checkout_request_id,
                                'ResultCode': 0,
                                'ResultDesc': result.get('ResultDesc', 'The service request is processed successfully.'),
                                'CallbackMetadata': {
                                    'Item': result.get('CallbackMetadata', {}).get('Item', [])
                                }
                            }
                        }
                    }

                    payment_txn = PaymentTransactionHelper.create_payment_transaction_from_callback(
                        synthetic_callback, queue_item
                    )

                    if not payment_txn:
                        queue_item.mark_failed(
                            reason='Failed to create PaymentTransaction from Daraja query',
                            error_code='TXN_CREATE_FAILED',
                            failure_category='system_error'
                        )
                        failed += 1
                        continue

                    # ── Credit balance only (Path 3 — no voucher) ────────────
                    MpesaPullReconciliation._credit_balance_for_queue(queue_item, payment_txn)

                    queue_item.mark_processed()

                    NotificationHelper.send_payment_notification(
                        queue_item.user,
                        f"✅ Payment confirmed! KES {queue_item.price} credited to your balance. "
                        f"Use it next time you connect.",
                        'success'
                    )

                    completed += 1
                    logger.info(
                        f"check_pending_transactions: recovered queue {queue_item.id} "
                        f"checkout={queue_item.checkout_request_id}"
                    )

                elif result_code in ('1', '2', '3', '4', '8', '17', '1019', '1025', '1032', '1037', '2001', '2028', '8006'):
                    # ── Definitive failure ────────────────────────────────────
                    failure_map = {
                        '1':    'Insufficient funds',
                        '2':    'Amount below minimum',
                        '3':    'Amount exceeds maximum',
                        '4':    'Daily limit exceeded',
                        '8':    'Maximum balance exceeded',
                        '17':   'Duplicate transaction — wait 2 minutes',
                        '1019': 'Transaction expired',
                        '1025': 'Payment request error',
                        '1032': 'Cancelled by user',
                        '1037': 'Timeout — user did not respond',
                        '2001': 'Incorrect M-Pesa PIN',
                        '2028': 'Invalid payment configuration',
                        '8006': 'M-Pesa account locked',
                    }
                    reason = failure_map.get(result_code, result.get('ResultDesc', 'Payment failed'))

                    queue_item.mark_failed(
                        reason=reason,
                        error_code=f'MPESA_{result_code}',
                        failure_category='payment_gateway',
                        increment_retry=False
                    )

                    # Refund credit portion only if mixed payment
                    if queue_item.used_credit and queue_item.used_credit > 0:
                        from django.db import transaction as db_txn
                        from users.models import ClientH
                        try:
                            with db_txn.atomic():
                                client = ClientH.objects.select_for_update().get(
                                    id=queue_item.user_id
                                )
                                client.balance += Decimal(str(queue_item.used_credit))
                                client.save(update_fields=['balance'])
                            logger.info(
                                f"check_pending_transactions: refunded credit "
                                f"{queue_item.used_credit} to {queue_item.user}"
                            )
                        except Exception as ref_err:
                            logger.error(
                                f"check_pending_transactions: credit refund failed "
                                f"for queue {queue_item.id}: {ref_err}"
                            )

                    NotificationHelper.send_payment_notification(
                        queue_item.user,
                        f"❌ Payment failed: {reason}",
                        'error'
                    )

                    failed += 1
                    logger.warning(
                        f"check_pending_transactions: failed queue {queue_item.id} "
                        f"code={result_code} reason={reason}"
                    )

                else:
                    # Still processing — leave it
                    skipped += 1
                    logger.debug(
                        f"check_pending_transactions: queue {queue_item.id} "
                        f"still pending (ResultCode={result_code})"
                    )

            except Exception as item_err:
                logger.error(
                    f"check_pending_transactions: error on queue {queue_item.id}: {item_err}",
                    exc_info=True
                )
                skipped += 1

        summary = {'queried': queried, 'completed': completed, 'failed': failed, 'skipped': skipped}
        logger.info(f"check_pending_transactions summary: {summary}")
        return summary

    except Exception as e:
        logger.error(f"check_pending_transactions task error: {e}", exc_info=True)
        return {'error': str(e)}
    finally:
        connection.close_if_unusable_or_obsolete()


@shared_task(bind=True)
def register_mpesa_pull(self, nominated_number, callback_url=None):
    """
    One-time task to register shortcode with Pull API.
    Run manually once before going live.
    """
    from finance.payment_gateway import MpesaPullReconciliation

    try:
        connection.close_if_unusable_or_obsolete()
        result = MpesaPullReconciliation.register_pull(nominated_number, callback_url)
        logger.info(f"Pull API registration result: {result}")
        return result
    except Exception as e:
        logger.error(f"Pull API registration error: {e}")
        return {'success': False, 'error': str(e)}
    finally:
        connection.close_if_unusable_or_obsolete()



@shared_task(bind=True)
def maintain_voucher_pool(self, min_count=5):
    """
    Periodic task: runs every 6 hours via Celery Beat.
    Tops up the AvailableVoucher fallback pool when it drops below min_count
    per package per location.
    """
    import uuid
    from django.utils import timezone as tz
    from packages.models import PackageType, AvailableVoucher
    from locations.models import Location

    try:
        connection.close_if_unusable_or_obsolete()

        packages  = PackageType.objects.filter(is_active=True)
        locations = Location.objects.filter(is_active=True)
        batch_id  = f"auto_{tz.now().strftime('%Y%m%d_%H%M%S')}"
        created   = 0

        for package in packages:
            for location in locations:
                existing = AvailableVoucher.objects.filter(
                    package=package, location=location, is_used=False
                ).count()
                needed = max(0, min_count - existing)
                if needed:
                    vouchers = [
                        AvailableVoucher(
                            voucher_code=f'FB-{uuid.uuid4().hex[:10].upper()}',
                            voucher_type='pre_generated',
                            package=package,
                            location=location,
                            batch_id=batch_id,
                            valid_until=tz.now() + tz.timedelta(days=30),
                        )
                        for _ in range(needed)
                    ]
                    AvailableVoucher.objects.bulk_create(vouchers, ignore_conflicts=True)
                    created += needed
                    logger.info(
                        f"maintain_voucher_pool: topped up {needed} vouchers "
                        f"for {package.code} @ {location.name}"
                    )

        logger.info(f"maintain_voucher_pool: created {created} vouchers total")
        return {'created': created, 'batch_id': batch_id}

    except Exception as e:
        logger.error(f"maintain_voucher_pool error: {e}", exc_info=True)
        return {'error': str(e)}
    finally:
        connection.close_if_unusable_or_obsolete()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def push_certificate_to_mikrotik(self):
    """
    Push renewed Let's Encrypt cert to MikroTik router.
    Triggered by certbot deploy hook after successful renewal.
    Retries 3 times with 60s delay on failure.
    """
    try:
        connection.close_if_unusable_or_obsolete()
        from finance.cert_push import push_cert_to_mikrotik
        result = push_cert_to_mikrotik()
        if result['success']:
            logger.info(f"Cert push succeeded: steps={result['steps']}")
        else:
            logger.error(f"Cert push failed: {result['error']}")
            raise Exception(result['error'])
        return result
    except Exception as e:
        logger.error(f"push_certificate_to_mikrotik error: {e}", exc_info=True)
        try:
            raise self.retry(exc=e)
        except self.MaxRetriesExceededError:
            logger.error("Max retries exceeded for cert push")
            return {'success': False, 'error': str(e)}
    finally:
        connection.close_if_unusable_or_obsolete()
