# views/user.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        client = getattr(user, 'clienth', None)

        return Response({
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "client": {
                "account": client.account if client else None,
                "ip": client.current_ip_address if client else None,
                "balance": client.balance if client else None,
                "status": client.status if client else None,
                "voucher_expiry": client.voucher_expiry if client else None
            }
        })
