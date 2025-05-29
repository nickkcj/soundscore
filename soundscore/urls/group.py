from django.urls import path, re_path
from soundscore.views.group_page import all_groups, create_group, group_room, set_online_status
from soundscore.views.group_chat import GroupChatConsumer  # Fixed import

urlpatterns = [
    path('', all_groups, name="all_groups"),
    path('create/', create_group, name="create_group"),
    path('<int:group_id>/', group_room, name="group_room"),
    path('set_online_status/', set_online_status, name="set_online_status"),
]

websocket_urlpatterns = [
    re_path(r'ws/group/(?P<group_id>\d+)/$', GroupChatConsumer.as_asgi()),  # Using your consumer
]
