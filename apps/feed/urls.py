from django.urls import path
from .views import feed, comment, like, notification

urlpatterns = [
    path('', feed.feed_view, name='feed'),
    path('comment/', comment.post_comment_view, name='comment'),
    path('comments/likes/toggle/', like.toggle_like_view, name='like'),
    path('comments/post-comment/', comment.post_comment_view, name='feed_post_comment'),
    path('comments/toggle-like/', like.toggle_like_view, name='feed_toggle_like'),
    path('comments/load-more/', feed.load_more_reviews_view, name='feed_load_more'),
    path('comments/post/', comment.post_comment_view, name='comment_post'),

    # Notifications
    path('notifications/', notification.get_notifications_view, name='notifications'),
    path('notifications/mark-read/<int:notification_id>/', notification.mark_read_view, name='mark_notification_read'),
    path('notifications/mark-all-read/', notification.mark_all_read_view, name='mark_all_notifications_read'),
    path('notifications/mark-all-as-read/', notification.mark_all_read_view, name='mark_all_notifications_read_alias'),
    path('notifications/unread-count/', notification.get_unread_count_view, name='unread_notifications_count'),
]