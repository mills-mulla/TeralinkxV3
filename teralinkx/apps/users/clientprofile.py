from rest_framework import generics, permissions
from users.models import ClientH  # Updated import
from core.serializers.userprofile_serializer import ClientProfileSerializer

class UpdateClientProfileView(generics.UpdateAPIView):
    queryset = ClientH.objects.all()
    serializer_class = ClientProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Updated to use correct related_name
        return self.request.user.client_profile