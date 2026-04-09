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
    """Shim — delegates to the canonical finance.tasks.check_pending_transactions."""
    from finance.tasks import check_pending_transactions
    return check_pending_transactions.apply().get()


@shared_task
def task_delete_pending():
    """Shim — delegates to finance.tasks.check_pending_transactions which handles
    expiry correctly instead of blindly deleting."""
    from finance.tasks import check_pending_transactions
    return check_pending_transactions.apply().get()
