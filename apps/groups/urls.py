from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_groups_view, name="groups"),
    path('create/', views.create_group_view, name="create_group"),
    path('<int:group_id>/', views.group_room_view, name="group_room"),
    path('set_online_status/', views.set_online_status_view, name="set_online_status"),
    path('<int:group_id>/join/', views.join_group_view, name="join_group"),
]
