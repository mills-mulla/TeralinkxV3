from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import DispatchVoucher,DHCPLease,ActiveUser,ClientH
from .router.ros_api.api import Api, RouterOSTrapError
from django.db.models import Q


TeralinkxWaves = '192.168.88.1'
who='admin'
how='q'

def validate_voucher(account, voucher_code):
    try:
        valid_voucher = DispatchVoucher.objects.get(
            dispatch_account=account, 
            dispatch_voucher_code=voucher_code, 
            dispatch_status__in=['active', 'inactive']
        )
        if valid_voucher:
            valid_voucher.dispatch_status = 'active'
            valid_voucher.save()
            
        return True, Response({'answer': 'voucher is valid.'}, status=status.HTTP_200_OK)
    except DispatchVoucher.DoesNotExist:
        return False, Response({'answer': 'voucher does not exist!'}, status=status.HTTP_404_NOT_FOUND)

class Connect(APIView):
    def post(self, request):
        account = request.data.get('account')
        voucher_code = request.data.get('voucher_code')
        bound_mac = request.data.get('bound_mac')

        client = ClientH.objects.get(account=account, status__in=['bound', 'active'])
        bound_ip = client.current_ip_address
        
        # Validate the voucher
        is_valid, response = validate_voucher(account, voucher_code)
        
        if not is_valid:
            return response
        
        # Perform the login if the voucher is valid
        try:
            router = Api(TeralinkxWaves, user=who, password=how, port=8728, verbose=True)
            hotspot_login = router.talk('/ip/hotspot/active/login =user=' + voucher_code + ' =ip=' + bound_ip)
            print(hotspot_login)
            # router.disconnect()
            print("Auto-login command sent successfully.")
            return Response({'answer': 'Auto-login command sent successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            print("Error: Failed to perform auto-login:", e)
            return Response({'error': 'Failed to perform auto-login', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

      
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class Reconnect(APIView):
    def post(self, request):
        account = request.data.get('account')
        voucher_code = request.data.get('voucher_code')
        bound_ip = request.data.get('bound_ip')

        # Step 1: Validate voucher
        is_valid, response = validate_voucher(account, voucher_code)
        if not is_valid:
            return response

        # Step 2: Attempt reconnect with retries
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                router = Api(
                    TeralinkxWaves,
                    user=who,
                    password=how,
                    port=8728,
                    verbose=True
                )
                hotspot_login = router.talk(
                    f"/ip/hotspot/active/login =user={voucher_code} =ip={bound_ip}"
                )
                print("Hotspot login response:", hotspot_login)
                print("Reconnect command sent successfully.")
                return Response(
                    {'answer': 'Reconnect command sent successfully.'},
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                print(f"Attempt {attempt} failed: {e}")
                if attempt < max_retries:
                    time.sleep(1)  # wait before retry
                else:
                    # After last attempt, return error
                    return Response(
                        {
                            'error': 'Failed to perform reconnection after 3 attempts',
                            'details': str(e)
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                
class Disconnect(APIView):
    def post(self, request):
        bound_mac = request.data.get('bound_mac')

       
        try:
            active_entry = ActiveUser.objects.get(mac_address=bound_mac)
            active_id = active_entry.idA
        except ActiveUser.DoesNotExist:
            return Response({'error': 'MAC address not found in active users. User is not connected to the network.'}, status=status.HTTP_404_NOT_FOUND)
      
        try:
            router = Api(TeralinkxWaves, user=who, password=how, port=8728, verbose=True)
            hotspot_logout = router.talk('/ip/hotspot/active/remove =numbers=' + active_id)
            print(hotspot_logout)
            active_entry.delete()
            # router.disconnect()
            print("Logout command sent successfully.")
            return Response({'answer': 'Logout command sent successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            print("Error: Failed to perform logout:", e)
            return Response({'error': 'Failed to perform logout', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


     
