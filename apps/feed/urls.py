from django.urls import path
from .views import feed, comment, like, notification

urlpatterns = [
    path('', feed.feed_view, name='feed'),
    path('comment/', comment.post_comment_view, name='comment'),
    path('like/', like.toggle_like_view, name='like'),
    path('notifications/', notification.get_notifications_view, name='notifications'),
    path('notifications/mark-read/<int:notification_id>/', notification.mark_read_view, name='mark_notification_read'),
    path('notifications/mark-all-read/', notification.mark_all_read_view, name='mark_all_notifications_read'),
    path('notifications/unread-count/', notification.get_unread_count_view, name='unread_notifications_count'),
]
