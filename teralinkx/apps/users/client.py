from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.serializers.client_serializer import ClientSerializer
from core.services.client_service import ClientService
from core.services.dhcp import DHCPManager
from rest_framework.permissions import AllowAny


class ClientView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ClientSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            user, client, is_new_user, token = ClientService.create_user_and_client(serializer.validated_data)
            DHCPManager.sync_client(client, client.mac_addresses.first())

            return Response({
                "user_id": user.id,
                "is_new_user": is_new_user,
                "token": token,
                "account": client.account,
                "balance": client.balance,
                "status": client.status
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
