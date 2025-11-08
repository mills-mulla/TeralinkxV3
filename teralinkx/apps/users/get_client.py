from rest_framework.views import APIView
from django.http import JsonResponse
from users.models import ClientH, UserDevice, UserSession  # Updated imports


class GetClientView(APIView):
    def post(self, request):
        acc = request.data.get('phone')
        mac = request.data.get('mac')
        try:
            client_info = ClientH.objects.filter(account=acc).first()
            
            if client_info:
                # Get current session info instead of direct fields
                current_session = client_info.active_sessions.order_by('-last_activity').first()
                
                return JsonResponse({
                    "client": client_info.display_name or client_info.user.first_name,
                    "acc_no": client_info.account,
                    "acc_ip": client_info.current_ip_address,  # Now from session
                    "acc_mac": client_info.current_mac_address,  # Now from session
                    "acc_bal": float(client_info.balance),
                    "acc_stat": client_info.status,
                    "acc_aVchr": client_info.active_voucher,
                    "acc_aVchrEx": client_info.voucher_expiry.isoformat() if client_info.voucher_expiry else None,
                    "image": client_info.profile_image.url if client_info.profile_image else None,
                    "active_devices": client_info.connected_devices.count(),  # New field
                    "current_location": str(client_info.current_location) if client_info.current_location else None
                })
            
            else:
                return JsonResponse({"error": "Client not found"}, status=404)
                
        except ClientH.DoesNotExist:
            return JsonResponse({"error": "Client does not exist!"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)