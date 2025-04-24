from django.urls import path
from ..views import chat

urlpatterns = [
    path('message/', chat.chat_message, name='chat_message'),
]