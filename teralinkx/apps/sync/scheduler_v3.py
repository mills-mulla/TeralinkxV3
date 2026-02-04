import logging
from django.utils import timezone
from decimal import Decimal
from django.db import transaction
from django.db.models import F
from django.core.exceptions import ObjectDoesNotExist

# V3 Model Imports
from users.models import ClientH, UserSession
from packages.models import DispatchVoucher
from finance.models import TransactionQueue

logger = logging.getLogger(__name__)

def check_voucher_expiry():
    """Check and expire vouchers based on V3 models"""
    now = timezone.now()
    expired_vouchers = DispatchVoucher.objects.filter(
        status='active',
        expires_at__lte=now
    )
    
    count = expired_vouchers.update(status='expired')
    logger.info(f"Expired {count} vouchers")

def ckeck_session_expiry():
    """Check and clean expired sessions based on V3 models"""
    now = timezone.now()
    expired_sessions = UserSession.objects.filter(
        is_active=True,
        last_activity__lte=now - F('auto_logout_minutes') * 60
    )
    
    count = expired_sessions.update(is_active=False)
    logger.info(f"Expired {count} sessions")

def delete_pending():
    """Delete old pending transactions"""
    cutoff_time = timezone.now() - timezone.timedelta(hours=24)
    deleted_count, _ = TransactionQueue.objects.filter(
        status='pending',
        created_at__lte=cutoff_time
    ).delete()
    logger.info(f"Deleted {deleted_count} old pending transactions")