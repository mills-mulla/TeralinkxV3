from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        Token.objects.filter(user=user).delete()
        return Response({"message": "Successfully logged out."}, status=200)
