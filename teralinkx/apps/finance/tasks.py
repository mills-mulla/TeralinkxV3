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


@shared_task(bind=True, max_retries=2)
def process_payment_callback(self, callback_data):
    """
    Async task to process M-Pesa callback
    Can be used for heavy processing without blocking callback endpoint
    """
    from finance.payment_gateway import (
        TransactionQueueHelper,
        PaymentTransactionHelper,
        VoucherHelper,
        NotificationHelper
    )
    
    try:
        connection.close_if_unusable_or_obsolete()
        
        stk_callback = callback_data.get('Body', {}).get('stkCallback', {})
        checkout_id = stk_callback.get('CheckoutRequestID')
        result_code = stk_callback.get('ResultCode')
        
        logger.info(f"Celery: Processing callback for {checkout_id}, result={result_code}")
        
        if result_code == 0:
            # Success - process payment
            queue_item = TransactionQueueHelper.get_pending_by_checkout_id(checkout_id)
            
            if queue_item:
                transaction = PaymentTransactionHelper.create_payment_transaction_from_callback(
                    callback_data,
                    queue_item
                )
                
                if transaction:
                    TransactionQueueHelper.process_successful_queue(queue_item, callback_data)
                    
                    # Activate voucher
                    location_id = queue_item.metadata.get('package_data', {}).get('location_id')
                    activated_voucher = VoucherHelper.activate_voucher(
                        queue_item.package_code,
                        transaction.gateway_reference,
                        location_id
                    )
                    
                    logger.info(f"Celery: Payment processed successfully for {checkout_id}")
                    return {'success': True, 'transaction_id': transaction.transaction_id}
        
        return {'success': False, 'result_code': result_code}
        
    except Exception as e:
        logger.error(f"Celery: Error processing callback: {e}", exc_info=True)
        raise self.retry(exc=e)
    finally:
        connection.close_if_unusable_or_obsolete()
