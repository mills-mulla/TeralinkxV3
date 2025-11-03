# File: views/dispatch_voucher.py
from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import DispatchVoucher

class DispatchVoucherAPIView(APIView):
    def post(self, request):
        data = request.data
        try:
            DispatchVoucher.objects.create(
                dispatch_account=data.get('account'),
                dispatch_price=data.get('price'),
                dispatch_package_desc=data.get('package_desc'),
                dispatch_package=data.get('package'),
                dispatch_status=data.get('status'),
                dispatch_voucher_code=data.get('voucher_code'),
                dispatch_package_duration=data.get('package_duration'),
                dispatch_devices=''
            )
            return Response({'message': 'Voucher dispatched successfully'})
        except Exception as e:
            return Response({'message': str(e)})