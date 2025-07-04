from django.test import TestCase
import pytest
import os
from unittest.mock import patch, MagicMock
from apps.chatbot.core.chatbot import SoundScoreBot, start_chat
from apps.chatbot.core.constants import GREETING_MESSAGE, FAREWELL_MESSAGE, HELP_MESSAGE
from apps.chatbot.core.utils import clear_screen


class TestSoundScoreBot:
    """Test core chatbot functionality"""

    def test_bot_initialization(self):
        """Test that the bot initializes correctly"""
        bot = SoundScoreBot()
        assert bot is not None
        assert hasattr(bot, 'conversation_history')
        assert bot.conversation_history == []

    @patch('builtins.print')
    def test_display_message(self, mock_print):
        """Test display_message method"""
        bot = SoundScoreBot()
        test_message = "Test message"
        
        # Test bot message (with formatting)
        bot.display_message(test_message, is_bot=True)
        mock_print.assert_called()
        
        # Test user message (no formatting)
        bot.display_message(test_message, is_bot=False)
        mock_print.assert_called()

    