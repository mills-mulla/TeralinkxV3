from django.utils import timezone
from django.db import transaction
from decimal import Decimal
from .models import DispatchVoucher, Package, ClientH, ExpiredVoucher, alternateSessions
from django.utils import timezone
import logging
from .generate import activate_voucher
import math

logger = logging.getLogger(__name__)

# Database Configuration
def get_db_url():
    """Returns the PostgreSQL database connection URL."""
    return "postgresql://teralinkx:teralinkx@localhost:5432/teralinkx"

#Expired Voucher Sweep
def check_expired_vouchers():
    """
    Sweep all vouchers marked as expired:
    1. Archive them into ExpiredVoucher
    2. Remove them from DispatchVoucher
    """
    now = timezone.now()

    expired_vouchers = DispatchVoucher.objects.filter(dispatch_status="expired")
    if not expired_vouchers.exists():
        return  # nothing to archive

    expired_records = []
    voucher_codes = [v.dispatch_voucher_code for v in expired_vouchers]

    # Prevent double-archival
    existing_codes = set(
        ExpiredVoucher.objects.filter(expired_voucher__in=voucher_codes)
        .values_list("expired_voucher", flat=True)
    )

    for voucher in expired_vouchers:
        if voucher.dispatch_voucher_code in existing_codes:
            continue

        # Resolve MAC
        mac = ClientH.objects.filter(account=voucher.dispatch_account).first()
        mac2 = alternateSessions.objects.filter(
            alternate_active_voucher=voucher.dispatch_voucher_code
        ).first()

        user_mac = (
            mac.mac_addresses.first().mac_address
            if mac and mac.mac_addresses.exists()
            else mac2.alternate_bound_mac
            if mac2
            else None
        )

        if user_mac:
            expired_records.append(
                ExpiredVoucher(
                    expired_account=voucher.dispatch_account,
                    expired_package=voucher.dispatch_package,
                    expired_voucher=voucher.dispatch_voucher_code,
                    user_mac=user_mac,
                    expiry_time=now,
                )
            )

    if expired_records:
        with transaction.atomic():
            # Bulk insert into archive
            ExpiredVoucher.objects.bulk_create(expired_records, ignore_conflicts=True)
            # Delete only what we successfully archived
            expired_vouchers.filter(dispatch_voucher_code__in=[
                r.expired_voucher for r in expired_records
            ]).delete()



class DowntimeRefund:
    MIN_DOWNTIME_FOR_REFUND = 10
    EXTRA_REFUND_THRESHOLD = 15
    EXTRA_REFUND_PERCENTAGE = Decimal(0.2)

    def post(self, request):
        downtime_minutes = int(request.data.get("downtime_minutes", 0))
        
        # Validate downtime_minutes
        if downtime_minutes < 0:
            logger.error("Negative downtime_minutes: %d", downtime_minutes)
            return {"error": "Invalid downtime_minutes."}, 400

        clients = DispatchVoucher.objects.filter(
            dispatch_expiry=False,
            usage_limit=None
        )
        
        for client in clients:
            refund_amount = self.calculate_refund(client, downtime_minutes)
            self.refund_user_balance(client.dispatch_account, refund_amount)
            logger.info("Refunded %d to client %s due to downtime.", refund_amount, client.dispatch_account)
        
        return {"message": "Refunds processed."}, 200

    def calculate_refund(self, client, downtime_minutes):
        package_price = Decimal(client.dispatch_price)
        duration_days = client.dispatch_package_duration.days

        refund = 0

        if client.dispatch_package_duration <= timezone.timedelta(days=1):  
            refund = self._calculate_short_duration_refund(package_price, downtime_minutes)
        else:  
            refund = self._calculate_long_duration_refund(package_price, downtime_minutes, duration_days)

        if downtime_minutes > self.EXTRA_REFUND_THRESHOLD:
            additional_refund = max(0, refund * self.EXTRA_REFUND_PERCENTAGE)
            refund += additional_refund

        final_refund = round(refund)

        if downtime_minutes < self.MIN_DOWNTIME_FOR_REFUND:
            return 0

        return max(0, final_refund)

    def _calculate_short_duration_refund(self, package_price, downtime_minutes):
        refund_per_minute = package_price / Decimal(60)
        refund_amount = refund_per_minute * downtime_minutes
        
        return max(0, math.floor(refund_amount))

    def _calculate_long_duration_refund(self, package_price, downtime_minutes, duration_days):
        total_minutes = 60 * 24 * duration_days
        refund_per_minute = package_price / Decimal(total_minutes)
        refund_amount = refund_per_minute * downtime_minutes
        
        return max(0, math.floor(refund_amount))

    def refund_user_balance(self, account, amount):
        client = ClientH.objects.filter(account=account).first()
        if client is not None:
            client.add_balance(amount)

