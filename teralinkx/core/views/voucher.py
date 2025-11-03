# File: views/voucher.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.middleware.csrf import get_token
from ..models import AvailableVoucher, DispatchVoucher

class VoucherAPIView(APIView):
    def get_csrf_token(self, request):
        return get_token(request)

    def post(self, request):
        csrf_token = self.get_csrf_token(request)
        data = request.data
        desc = data.get('package_desc')
        acc = data.get('phone_number')

        try:
            vouchers = AvailableVoucher.objects.filter(package_desc=desc)
            if vouchers.exists():
                voucher = vouchers.first()
                voucher.delete()

                DispatchVoucher.objects.create(
                    dispatch_account=acc,
                    dispatch_voucher_code=voucher.voucher_code,
                    dispatch_package=voucher.package,
                    dispatch_package_desc=voucher.package_desc,
                    dispatch_package_duration=str(voucher.duration),
                    dispatch_status="active",
                    dispatch_devices='',
                    dispatch_price=str(voucher.price)
                )

                return Response({
                    'voucher': {
                        'voucher_code': voucher.voucher_code,
                        'package': voucher.package,
                        'package_desc': voucher.package_desc,
                        'duration': str(voucher.duration),
                        'price': str(voucher.price)
                    },
                    'message': 'Voucher dispatched successfully'
                })
            return Response({'message': 'No voucher found'}, status=404)
        except Exception as e:
            return Response({'message': str(e)}, status=400)