from django.urls import path, re_path
from apps.groups.views import group_views
from apps.groups.consumers import GroupChatConsumer

urlpatterns = [
    path('', group_views.all_groups_view, name="all_groups"),
    path('create/', group_views.create_group_view, name="create_group"),
    path('<int:group_id>/', group_views.group_room_view, name="group_room"),
    path('set_online_status/', group_views.set_online_status_view, name="set_online_status"),
    path('<int:group_id>/join/', group_views.join_group_view, name="join_group"),
]

websocket_urlpatterns = [
    re_path(r'ws/group/(?P<group_id>\d+)/$', GroupChatConsumer.as_asgi()),
]