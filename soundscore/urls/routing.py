from django.urls import re_path
from soundscore.views.group_chat import GroupChatConsumer 

websocket_urlpatterns = [
    re_path(r'ws/group/(?P<group_id>\w+)/$', GroupChatConsumer.as_asgi()),
]
