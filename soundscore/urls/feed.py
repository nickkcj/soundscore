from django.urls import path
from ..views import feed

urlpatterns = [
    path('post/', feed.post_comment, name='post_comment'),
    path('likes/toggle/', feed.toggle_like, name='toggle_like'),
]