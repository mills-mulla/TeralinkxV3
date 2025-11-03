from rest_framework import generics, permissions
from ..models import ClientH
from ..serializers.userprofile_serializer import ClientProfileSerializer

class UpdateClientProfileView(generics.UpdateAPIView):
    queryset = ClientH.objects.all()
    serializer_class = ClientProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.clienth