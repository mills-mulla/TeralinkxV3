# core/superuser/views/auth.py
import json
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
import logging

logger = logging.getLogger(__name__)

class AdminLoginView(APIView):
    """
    Admin login view - JWT token based authentication
    """
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        try:
            logger.info("=== JWT LOGIN ATTEMPT ===")

            data = json.loads(request.body)
            username = data.get('username', '').strip()
            password = data.get('password', '')

            # Validate input
            if not username or not password:
                return Response({
                    'success': False,
                    'message': 'Username and password are required'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Authenticate user
            user = authenticate(request, username=username, password=password)
            logger.info(f"Authentication result: {user}")

            if user is not None:
                # Check if user has admin privileges
                if user.is_superuser or user.is_staff:
                    logger.info("User has admin privileges - generating JWT tokens")

                    # Generate JWT tokens
                    refresh = RefreshToken.for_user(user)
                    
                    # Add custom claims to payload if needed
                    refresh['username'] = user.username
                    refresh['is_superuser'] = user.is_superuser
                    refresh['is_staff'] = user.is_staff

                    logger.info("JWT tokens generated successfully")

                    return Response({
                        'success': True,
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'email': user.email,
                            'is_superuser': user.is_superuser,
                            'is_staff': user.is_staff,
                            'first_name': user.first_name,
                            'last_name': user.last_name
                        },
                        'tokens': {
                            'access': str(refresh.access_token),
                            'refresh': str(refresh)
                        }
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'success': False,
                        'message': 'Insufficient permissions. Admin access required.'
                    }, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({
                    'success': False,
                    'message': 'Invalid username or password'
                }, status=status.HTTP_401_UNAUTHORIZED)

        except json.JSONDecodeError:
            return Response({
                'success': False,
                'message': 'Invalid JSON data'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Login error: {e}")
            return Response({
                'success': False,
                'message': 'Server error during login'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TokenRefreshView(APIView):
    """
    Refresh JWT access token using refresh token
    """
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            
            if not refresh_token:
                return Response({
                    'success': False,
                    'message': 'Refresh token is required'
                }, status=status.HTTP_400_BAD_REQUEST)

            refresh = RefreshToken(refresh_token)
            
            # Generate new access token
            new_access_token = str(refresh.access_token)
            
            logger.info("JWT token refreshed successfully")
            
            return Response({
                'success': True,
                'access': new_access_token
            }, status=status.HTTP_200_OK)

        except TokenError as e:
            logger.error(f"Token refresh error: {e}")
            return Response({
                'success': False,
                'message': 'Invalid or expired refresh token'
            }, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.error(f"Token refresh unexpected error: {e}")
            return Response({
                'success': False,
                'message': 'Server error during token refresh'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyTokenView(APIView):
    """
    Verify JWT token validity and return user info
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        logger.info(f"Token verification - user: {request.user}")
        
        return Response({
            'authenticated': True,
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'is_superuser': request.user.is_superuser,
                'is_staff': request.user.is_staff,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name
            }
        })


class CheckAuthView(APIView):
    """
    Check authentication status - compatible with both JWT and Session
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = []

    def get(self, request):
        # Try JWT authentication first
        if request.user.is_authenticated:
            if request.user.is_superuser or request.user.is_staff:
                logger.info(f"JWT Auth check - authenticated: {request.user.username}")
                return Response({
                    'authenticated': True,
                    'user': {
                        'id': request.user.id,
                        'username': request.user.username,
                        'email': request.user.email,
                        'is_superuser': request.user.is_superuser,
                        'is_staff': request.user.is_staff,
                    }
                })
        
        # Fallback to session auth for backward compatibility
        if hasattr(request, 'session') and request.user.is_authenticated:
            if request.user.is_superuser or request.user.is_staff:
                logger.info(f"Session Auth check - authenticated: {request.user.username}")
                return Response({
                    'authenticated': True,
                    'user': {
                        'id': request.user.id,
                        'username': request.user.username,
                        'email': request.user.email,
                        'is_superuser': request.user.is_superuser,
                        'is_staff': request.user.is_staff,
                    },
                    'session_id': request.session.session_key
                })

        logger.info("Auth check - not authenticated")
        return Response({
            'authenticated': False
        })


class AdminLogoutView(APIView):
    """
    Admin logout - primarily client-side token destruction
    Optional: Add token blacklisting if needed
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Optional: Blacklist the refresh token
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                try:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                    logger.info("Refresh token blacklisted")
                except TokenError as e:
                    logger.warning(f"Token blacklist error (may already be invalid): {e}")

            logger.info(f"User {request.user.username} logged out")
            
            return Response({
                'success': True,
                'message': 'Logged out successfully'
            })

        except Exception as e:
            logger.error(f"Logout error: {e}")
            return Response({
                'success': False,
                'message': 'Error during logout'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TokenObtainPairView(APIView):
    """
    Alternative token obtain view matching Simple JWT convention
    """
    permission_classes = []

    def post(self, request):
        # Reuse the login logic but with different response format
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)
        
        if user and (user.is_superuser or user.is_staff):
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            })
        
        return Response({
            'detail': 'No active account found with the given credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)