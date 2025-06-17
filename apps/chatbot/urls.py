from django.urls import path
from ..views import chatbot

urlpatterns = [
    path('message/', chatbot.chat_message, name='chat_message'),
]
