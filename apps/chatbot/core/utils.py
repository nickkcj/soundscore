"""Utility functions for the SoundScore chatbot."""

import os
import time
import json
from django.conf import settings

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def typing_effect(text, delay=0.03):
    """Print text with a typing effect."""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def format_bot_message(message):
    """Format a message from the bot."""
    lines = message.strip().split('\n')
    width = max(len(line) for line in lines) + 4
    
    result = "┌" + "─" * width + "┐\n"
    
    for line in lines:
        padding = width - len(line) - 4
        result += "│ 🤖 " + line + " " * padding + " │\n"
    
    result += "└" + "─" * width + "┘"
    return result

def format_user_message(message):
    """Format a message from the user."""
    return f"💬 You: {message}"

def format_thinking():
    """Show a thinking animation."""
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    for _ in range(2):  # Do 2 full cycles
        for frame in frames:
            print(f"\r🧠 Thinking {frame}", end="", flush=True)
            time.sleep(0.1)
    print("\r" + " " * 20 + "\r", end="")  # Clear the line

def get_chat_history(user_id):
    """Get chat history for a user."""
    history_file = os.path.join(settings.BASE_DIR, 'chat_history', f'{user_id}.json')
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            return json.load(f)
    return []

def save_chat_message(user_id, message, is_bot=False):
    """Save a chat message to the user's history."""
    history_file = os.path.join(settings.BASE_DIR, 'chat_history', f'{user_id}.json')
    os.makedirs(os.path.dirname(history_file), exist_ok=True)
    
    history = get_chat_history(user_id)
    history.append({
        'message': message,
        'is_bot': is_bot,
        'timestamp': time.time()
    })
    
    with open(history_file, 'w') as f:
        json.dump(history, f)