"""Utility functions for the SoundScore chatbot."""

import os
import time

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