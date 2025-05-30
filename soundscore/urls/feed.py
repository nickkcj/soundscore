from django.urls import path
from ..views import feed

urlpatterns = [
    path('post/', feed.post_comment, name='post_comment'),
    path('likes/toggle/', feed.toggle_like, name='toggle_like'),
    path('feed/load-more/', feed.load_more_reviews, name='load_more_reviews'),
    path('notification/<int:notification_id>/details/', feed.get_notification_details, name='get_notification_details'),
]