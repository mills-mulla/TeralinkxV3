from rest_framework import generics, permissions
from core.models import ClientH
from core.serializers.userprofile_serializer import ClientProfileSerializer

class UpdateClientProfileView(generics.UpdateAPIView):
    queryset = ClientH.objects.all()
    serializer_class = ClientProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.clienth