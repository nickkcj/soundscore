from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('api/send/', views.send_message_view, name='send_message'),
    path('api/history/', views.get_chat_history_view, name='chat_history'),
]
