from ..models import DispatchVoucher

class VoucherService:
    @staticmethod
    def dispatch_voucher(voucher, account):
        return DispatchVoucher.objects.create(
            dispatch_account=account,
            dispatch_voucher_code=voucher.voucher_code,
            dispatch_package=voucher.package,
            dispatch_package_code=voucher.package_code,
            dispatch_package_duration=str(voucher.duration),
            dispatch_status="active",
            dispatch_devices='',
            dispatch_price=str(voucher.price)
        )
