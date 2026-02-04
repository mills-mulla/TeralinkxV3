# apps/users/image_api.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser, FormParser


class ProfileImageUploadAPIView(APIView):
    """Handle profile image uploads separately"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        """Upload profile image"""
        try:
            print(f"Image upload request received")
            print(f"Request FILES: {request.FILES}")
            print(f"Request data: {request.data}")
            
            user = request.user
            print(f"User: {user}")
            
            client = user.client_profile
            print(f"Client: {client}")
            
            if 'profile_image' in request.FILES:
                print(f"Profile image found in FILES")
                if hasattr(client, 'profile_image'):
                    print(f"Client has profile_image field")
                    client.profile_image = request.FILES['profile_image']
                    client.save()
                    print(f"Image saved successfully")
                    
                    return Response({'success': True}, status=status.HTTP_200_OK)
                else:
                    print(f"Client does not have profile_image field")
                    return Response({'error': 'Profile image field not available'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                print(f"No profile_image in request.FILES")
                return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            print(f"Error in image upload: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)