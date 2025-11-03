from rest_framework.views import APIView
from django.http import JsonResponse
from ..models import ClientH, alternateSessions

class GetClientView(APIView):
    def post(self, request):
        acc = request.data.get('phone')
        mac = request.data.get('mac')
        try:
            client_info = ClientH.objects.filter(account=acc).first()
            alt_info = alternateSessions.objects.filter(alternate_bound_mac=mac).first()
            
            if client_info:
                return JsonResponse({
                    "client": client_info.user.first_name,
                    "acc_no": client_info.account,
                    "acc_ip": client_info.bound_ip,
                    "acc_mac": '',
                    "acc_bal": client_info.balance,
                    "acc_stat": client_info.status,
                    "acc_aVchr": client_info.active_voucher,
                    "acc_aVchrEx": client_info.voucher_expiry,
                    "image": client_info.image.url if client_info.image else None
                })
            elif alt_info:
                bal = ClientH.objects.get(account=acc)
                return JsonResponse({
                    "acc_no": alt_info.alternate_no,
                    "acc_ip": alt_info.alternate_bound_ip,
                    "acc_mac": alt_info.alternate_bound_mac,
                    "acc_bal": bal.balance,
                    "acc_stat": alt_info.alternate_status,
                    "acc_aVchr": alt_info.alternate_active_voucher,
                    "acc_aVchrEx": alt_info.alternate_voucher_expiry
                })
        except (ClientH.DoesNotExist, alternateSessions.DoesNotExist):
            return JsonResponse("Client does not exist!", safe=False)
