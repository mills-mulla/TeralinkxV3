# apps/users/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .client import ClientView
from .get_client import GetClientView
from rest_framework_simplejwt.views import TokenRefreshView

# Create a router for potential future ViewSets
router = DefaultRouter()
# router.register('profiles', ClientProfileViewSet, basename='client-profiles')

urlpatterns = [
    # Client registration and management
    path('clients/', ClientView.as_view(), name='client-create'),
    path('getclient/', GetClientView.as_view()),
    
    # Authentication endpoints
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    # path("me/", MeView.as_view(), name="user-me"),
    # path('logout/', LogoutView.as_view(), name='logout'),
]
    
