from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.serializers.client_serializer import ClientSerializer
from core.services.client_service import ClientService
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class ClientView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []  # Explicitly disable authentication

    def post(self, request):
        serializer = ClientSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            user, client, is_new_user, token = ClientService.create_user_and_client(serializer.validated_data)
            
            return Response({
                "user_id": user.id,
                "is_new_user": is_new_user,
                "token": token,
                "account": client.account,
                "balance": float(client.balance),
                "status": client.status,
                "display_name": client.display_name,
                "account_tier": client.account_tier,
                "phone_number": client.phone_number,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)