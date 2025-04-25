from ..views import feed
from django.urls import path

urlpatterns = [
    path('', feed.get_notifications, name='notifications'),
    path('unread-count/', feed.get_unread_count_view, name='unread_count'),
    path('mark-all-as-read/', feed.mark_all_read, name='mark_all_as_read'),
]