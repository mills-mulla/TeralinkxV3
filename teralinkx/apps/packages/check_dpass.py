# File: views/check_dpass.py
############################
############################
#update tho check trial and  daily free net time eligibility
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from ..models import DispatchVoucher

class CheckDpassStatus(APIView):
    def post(self, request):
        client_id = request.data.get('client_id')
        package_desc = request.data.get('package_desc')
        if not client_id:
            return Response({"error": "client_id is required"}, status=400)

        now = timezone.now()
        purchase_window_start = now.replace(hour=6, minute=0, second=0, microsecond=0)
        purchase_window_end = now.replace(hour=7, minute=0, second=0, microsecond=0)
        is_purchase_time = purchase_window_start <= now < purchase_window_end
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

        has_active = DispatchVoucher.objects.filter(
            dispatch_account=client_id,
            dispatch_package_desc=package_desc,
            dispatch_time__gte=start_of_day
        ).exists()

        has_expired = ExpiredVoucher.objects.filter(
            expired_account=client_id,
            expired_voucher__startswith='DPASS',
            expiry_time__gte=start_of_day
        ).exists() if not has_active else False

        return Response({
            "isPurchaseTime": is_purchase_time,
            "hasPurchasedToday": has_active or has_expired
        })
