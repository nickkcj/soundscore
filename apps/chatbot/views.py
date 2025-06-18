from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json
from .core.chatbot import SoundScoreBot
from .core.utils import get_chat_history, save_chat_message
import sys # Import sys for printing to stderr

# Create a singleton bot instance
_bot_instance = None

def get_bot():
    global _bot_instance
    if _bot_instance is None:
        print("DEBUG: Creating new SoundScoreBot instance", file=sys.stderr)
        _bot_instance = SoundScoreBot()
    else:
        print("DEBUG: Reusing existing SoundScoreBot instance", file=sys.stderr)
    return _bot_instance

@require_POST
@login_required
def send_message_view(request):
    """Process a chat message and return the bot's response."""
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()

        if not message:
            return JsonResponse({"error": "Message cannot be empty"}, status=400)

        # Save user message
        save_chat_message(request.user.id, message, is_bot=False)

        # Get bot instance
        bot = get_bot()

        # Process the message
        response = bot.get_response(message)
        
        # Save bot response
        save_chat_message(request.user.id, response["message"], is_bot=True)
        
        return JsonResponse({
            "response": response["message"]
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def get_chat_history_view(request):
    """Get chat history for the current user."""
    try:
        history = get_chat_history(request.user.id)
        return JsonResponse({"history": history})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def chat_view(request):
    """Render the chat interface."""
    return render(request, 'chatbot/chat.html')