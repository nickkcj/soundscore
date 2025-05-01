from django.urls import path
from soundscore.views.group_page import all_groups, create_group, group_room
urlpatterns = [
    path('', all_groups, name="all_groups"),
    path('create/', create_group, name="create_group"),
    path('<int:group_id>/', group_room, name="group_room"),
]
