from django.urls import path
from .views import UserAPIView, ProfileAPIView, SessionAPIView, DisconnectAPIView

urlpatterns = [
    path('users/', UserAPIView.as_view(), name='users'),
    path('profiles/', ProfileAPIView.as_view(), name='profiles'),
    path('sessions/', SessionAPIView.as_view(), name='sessions'),
    path('disconnect/', DisconnectAPIView.as_view(), name='disconnect'),
]
