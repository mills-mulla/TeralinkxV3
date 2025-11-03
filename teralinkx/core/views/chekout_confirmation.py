from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import logging
from ..services.notification_service import create_and_notify
from django.utils import timezone
from ..models import Queue, Package, DailyPass, DispatchVoucher, ClientH
from .queryDaraja import query_stk_status
from django.db import transaction
from ..generate import activate_voucher
from django.contrib.auth import get_user_model
from decimal import Decimal
from .moitoring import get_user_by_name
from ..authentications import validate_voucher, Api, TeralinkxWaves,who,how
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)
User = get_user_model()
now = timezone.now()


def create_dispatch_voucher(user, dispatch_obj, voucher_code, dispatch_account, package_desc, queue_record, hotspot_ip):
    """
    Creates a DispatchVoucher record and deducts the client's balance.
    Also performs auto-login for the voucher.

    Args:
        user: User instance linked to the dispatch.
        dispatch_obj: Dispatch object (Package or DailyPass).
        voucher_code: Voucher code string.
        dispatch_account: Dispatch account identifier.
        package_desc: Description of the package.
        quota_record: Record with usage information.
        hotspot_ip: IP address for hotspot auto-login.
    """
    DispatchVoucher.objects.create(
        dispatch_account=dispatch_account,
        dispatch_voucher_code=voucher_code,
        dispatch_package=getattr(dispatch_obj, 'package', None),
        dispatch_package_desc=package_desc,
        dispatch_package_duration=getattr(dispatch_obj, 'package_duration', None),
        dispatch_status='active',
        dispatch_price=str(getattr(dispatch_obj, 'price', 0)),
        dispatch_devices=str(getattr(dispatch_obj, 'devices', 0)),
        usermanid=get_user_by_name(voucher_code),
        usage_limit=dispatch_obj.usage_limit
    )

    client = user.clienth
    client.balance -= Decimal(queue_record.used_balance)
    client.save()

    perform_auto_login(dispatch_account, voucher_code, hotspot_ip)


def get_device_by_package_desc(package_desc):
    """
    Retrieves a device either from Package or DailyPass matching the package description.

    Args:
        package_desc: Description string of the package.

    Returns:
        device instance or None if not found.
    """
    pkg = Package.objects.filter(package_desc=package_desc).first()
    if not pkg:
        pkg = DailyPass.objects.filter(package_desc__icontains=package_desc).first()
    return pkg


def refund_user_balance(user, amount):
    """
    Refunds the specified amount to the user's client balance.

    Args:
        user: User instance to refund.
        amount: Decimal amount to refund.
    """
    try:
        client = user.clienth
        if client is None:
            logger.error(f"❌ ClientH profile not found for user {user.username} (User ID: {user.id})")
            return
        
        amount_decimal = Decimal(amount)  # Ensure amount is converted to Decimal

        if amount_decimal > 0:
            with transaction.atomic():
                client.add_balance(amount_decimal)
                logger.info(f"💰 Refunded {amount_decimal} to user {user.username}")
    except Exception as e:
        logger.error(f"❌ Error during refund for user {user.username} (User ID: {user.id}): {str(e)}")


def process_voucher_activation(user, pkg, package_desc, queue_record, hotspot_ip):
    """
    Activates a voucher and dispatches it. Updates DailyPass limit if applicable.

    Args:
        user: User instance.
        device: Device instance (Package or DailyPass).
        package_desc: Package description.
        queue_record: Queue record related to payment.
        hotspot_ip: IP for auto-login.
    """
    activation_result = activate_voucher(prefix='QRDSTk', profile=package_desc, devices=pkg.devices)

    if activation_result["status"] != "activated":
        logger.error("Voucher activation failed")
        refund_user_balance(user,Decimal(queue_record.price))
        return JsonResponse({
            'ResultCode': -1,
            'ResultDesc': 'Voucher activation failed,Account has been refunded!',
            'Metadata': {}
        })

    voucher_code = activation_result["voucher_code"]
    dispatch_helper_args = (user, pkg, voucher_code, queue_record.recipient.strip(),package_desc, queue_record, hotspot_ip)
    create_dispatch_voucher(*dispatch_helper_args)
    
    if isinstance(pkg, DailyPass):
        pkg.limit -= 1
        if pkg.limit < 1:
            pkg.status = 'soldout'
        pkg.save()


    return JsonResponse({
        'ResultCode': 0,
        'ResultDesc': 'Payment processed and voucher dispatched.',
        'Metadata': {'voucher_status': 'active'}
    })


def notify_user_payment_success(user, recipient):
    """
    Sends notifications to the user about payment success.

    Args:
        user: User instance.
        recipient: Recipient string.
    """
    message_body = f"✅ Payment successful for {recipient}."
    create_and_notify(user, "Checkout confirmed", "success")
    create_and_notify(user, message_body, "success")


def notify_user_payment_pending(user):
    """
    Sends notification about pending payment.

    Args:
        user: User instance.
    """
    create_and_notify(user, " ⏳ Payment pending", "info")


@csrf_exempt
def payment_status(request):
    """
    Handles payment status queries from M-Pesa and processes voucher dispatch on successful payments.

    Args:
        request: Django HttpRequest object.

    Returns:
        JsonResponse with the payment processing status.
    """
    checkout_request_id = request.GET.get('request_id')
    ping = request.GET.get('ping')
    hotspot_ip = request.GET.get('hotspot_ip')

    if not checkout_request_id:
        return JsonResponse({
            'ResultCode': -1,
            'ResultDesc': 'Missing checkout_request_id',
            'Metadata': {}
        })

    pending_transactions = Queue.objects.filter(
        checkout_request_id=checkout_request_id,
        method='mpesa',
        status="Pending..."
    )

    if not pending_transactions.exists():
        logger.info("No unprocessed transactions found.")
        return JsonResponse({
            'ResultCode': -1,
            'ResultDesc': 'No pending transactions found',
            'Metadata': {}
        })

    for queue_record in pending_transactions:
        try:
            response_data = query_stk_status(checkout_request_id)
            package_desc = queue_record.package_desc.strip()
            pkg = get_device_by_package_desc(package_desc)
            recipient = queue_record.recipient.strip()

            if str(response_data.get('ResultCode')) == '0':
                user = None
                try:
                    user = User.objects.get(id=ping)
                except (TypeError, ValueError, User.DoesNotExist):
                    logger.info("No valid user found for notification.")

                if user:
                    notify_user_payment_success(user, recipient)

                with transaction.atomic():
                    queue_record.status = "processed"
                    queue_record.save()
                    logger.info(f"Transaction {checkout_request_id} processed.")

                    if pkg:
                        # Process voucher activation and dispatch
                        return process_voucher_activation(user, pkg, package_desc, queue_record, hotspot_ip)

            else:
                logger.warning(f"Transaction still pending or failed: {response_data}")
                if ping:
                    try:
                        user = User.objects.get(id=ping)
                        notify_user_payment_pending(user)
                    except User.DoesNotExist:
                        pass

                return JsonResponse({
                    'ResultCode': -1,
                    'ResultDesc': 'Payment still pending',
                    'Metadata': response_data
                })

        except Exception as e:
            logger.error(f"Error querying transaction {checkout_request_id}: {e}")
            return JsonResponse({
                'ResultCode': -1,
                'ResultDesc': str(e),
                'Metadata': {}
            })

    return JsonResponse({
        'ResultCode': -1,
        'ResultDesc': 'Unhandled state',
        'Metadata': {}
    })


def perform_auto_login(account, voucher_code, bound_ip):
    """
    Validates the voucher and performs auto-login by interacting with the router API.

    Args:
        account: Dispatch account string.
        voucher_code: Voucher code string.
        bound_ip: IP address bound to the login.

    Returns:
        DRF Response object with success or error message.
    """
    is_valid, response = validate_voucher(account, voucher_code)

    if not is_valid:
        return response

    try:
        # Credentials should be defined or loaded from secure config/environment
        router = Api(TeralinkxWaves, user=who, password=how, port=8728, verbose=True)
        hotspot_login = router.talk(f'/ip/hotspot/active/login =user={voucher_code} =ip={bound_ip}')
        logger.info(f"Reconnect command sent successfully: {hotspot_login}")
        return Response({'answer': 'Reconnect command sent successfully.'}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Failed to perform auto-login: {e}")
        return Response({'error': 'Failed to perform auto-login', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

