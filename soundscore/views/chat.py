from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json
from ..agent.chatbot import SoundScoreBot
import sys # Import sys for printing to stderr

# Create a singleton bot instance
_bot_instance = None

def get_bot():
    global _bot_instance
    if _bot_instance is None:
        print("DEBUG: Creating new SoundScoreBot instance", file=sys.stderr) # ADDED
        _bot_instance = SoundScoreBot()
    else:
        print("DEBUG: Reusing existing SoundScoreBot instance", file=sys.stderr) # ADDED
    return _bot_instance

@require_POST
@login_required
def chat_message(request):
    """Process a chat message and return the bot's response."""
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()

        if not message:
            return JsonResponse({"error": "Message cannot be empty"}, status=400)

        # Get bot instance
        bot = get_bot()

        # Process the message
        response = bot.get_response(message)
        
        # Return just the message without the SQL
        return JsonResponse({
            "response": response["message"]
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)