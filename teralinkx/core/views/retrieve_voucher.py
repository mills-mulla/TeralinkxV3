# File: views/retrieve_voucher.py
from rest_framework.views import APIView
from django.http import JsonResponse
from ..models import DispatchVoucher


class RetrieveVoucher(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        try:
            voucher = DispatchVoucher.objects.get(dispatch_account=phone_number, status='active')
             
            return JsonResponse({
                'voucher': {
                    'voucher_code': voucher.dispatch_voucher_code,
                    'package': voucher.dispatch_package,
                    'package_desc': voucher.dispatch_package_desc,
                    'devices': voucher.dispatch_devices,
                    'package_duration': str(voucher.dispatch_package_duration),
                    'price': str(voucher.dispatch_price),
                    'usage': {
                        'uptime': voucher.uptime,
                        'total_download': voucher.total_download,
                        'total_upload': voucher.total_upload,
                        'active_sessions': voucher.active_sessions
                    }
                },
                'message': 'Voucher retrieved successfully'
            })
        except DispatchVoucher.DoesNotExist:
            return JsonResponse({'message': 'No matching record found'}, status=400)