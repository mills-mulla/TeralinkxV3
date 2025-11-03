# File: views/superuser.py
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model

class SuperuserAPIView(APIView):
    def post(self, request):
        User = get_user_model()
        try:
            User.objects.create_superuser(
                username=request.data.get('username'),
                email=request.data.get('email', ''),
                password=request.data.get('password')
            )
            return Response({'success': True, 'message': 'Superuser created successfully'})
        except Exception as e:
            return Response({'success': False, 'errors': str(e)}, status=400)