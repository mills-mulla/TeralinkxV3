# apps/notifications/urls.py
from django.urls import path
from .views import MarkNotificationReadView, AnnouncementListView, PublicAnnouncementListView

urlpatterns = [
    path('<int:notification_id>/read/', MarkNotificationReadView.as_view(), name='mark_notification_read'),
    path('announcements/', AnnouncementListView.as_view(), name='announcements_list'),
    path('announcements/public/', PublicAnnouncementListView.as_view(), name='public_announcements'),
]