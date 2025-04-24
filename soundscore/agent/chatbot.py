"""Main chat interface for the SoundScore database agent."""

import traceback
import time

from .prompt_handler import convert_prompt_to_sql
from .query_engine import execute_query, format_with_gemini
from .utils import format_bot_message, clear_screen, typing_effect
from .constants import GREETING_MESSAGE, FAREWELL_MESSAGE, HELP_MESSAGE

class SoundScoreBot:
    def __init__(self):
        self.conversation_history = []

    def add_to_history(self, speaker, message):
        self.conversation_history.append({"speaker": speaker, "message": message})

    def display_message(self, message, is_bot=True):
        if is_bot:
            formatted = format_bot_message(message)
            typing_effect(formatted)
        else:
            print(f"💬 You: {message}")


    def greet(self):
        clear_screen()
        self.display_message(GREETING_MESSAGE)
        self.add_to_history("bot", GREETING_MESSAGE)

    def process_query(self, user_input):
        self.add_to_history("user", user_input)
        # 1. Convert prompt to SQL using Gemini
        query_result = convert_prompt_to_sql(user_input)
        sql = query_result.get("sql")
        if not sql:
            response = f"I'm sorry, I couldn't understand that query. {query_result.get('message', 'Unknown error')}"
            self.display_message(response)
            self.add_to_history("bot", response)
            return

        # 2. Execute the SQL query
        execution_result = execute_query(sql)
        if not execution_result.get("success"):
            error_message = f"I encountered an error running that query: {execution_result.get('error', 'Unknown database error')}"
            self.display_message(error_message)
            self.add_to_history("bot", error_message)
            return

        results = execution_result.get("results")
        if not results:
            response = "I couldn't find any results matching your query."
            self.display_message(response)
            self.add_to_history("bot", response)
            return

        # 3. Format the results with Gemini
        try:
            response = format_with_gemini(results, user_input)
        except Exception as e:
            response = f"Results: {str(results)}"
        self.display_message(response)
        self.add_to_history("bot", response)

    def get_response(self, user_input):
        """Process a user query and return a response (for API use)."""

        start_time = time.time()
        
        self.add_to_history("user", user_input)
        
        # Handle special commands
        user_input_lower = user_input.lower()
        if user_input_lower in ('exit', 'quit', 'bye'):
            return {"message": "👋 " + FAREWELL_MESSAGE}
        elif user_input_lower in ('help', '?'):
            return {"message": "❓ " + HELP_MESSAGE}
        elif user_input_lower in ('clear', 'cls'):
            return {"message": "🧹 Screen cleared."}
        elif not user_input_lower.strip():
            return {"message": "⚠️ Please enter a question."}
        
        # Specific test for Gemini API
        if user_input_lower == 'test gemini':

            try:
                import google.generativeai as genai
                from decouple import config
                
                genai.configure(api_key=config("GOOGLE_API_KEY"))
                model = genai.GenerativeModel("gemini-1.5-flash")
                test_response = model.generate_content("Hello, is Gemini API working?")
                test_result = f"✅ Gemini API Test Success! Response: {test_response.text[:100]}"

                return {"message": test_result}
            except Exception as e:
                test_result = f"❌ Gemini API Test Failed: {type(e).__name__}: {str(e)}"


                return {"message": test_result}
        
        # Continue with normal processing
        try:

            query_result = convert_prompt_to_sql(user_input)

            
            sql = query_result.get("sql")
            if not sql:
                response = f"I'm sorry, I couldn't understand that query. {query_result.get('message', 'Unknown error')}"
                self.add_to_history("bot", response)

                return {"message": response}


            execution_result = execute_query(sql)

            
            if not execution_result.get("success"):
                error_message = f"I encountered an error running that query: {execution_result.get('error', 'Unknown database error')}"
                self.add_to_history("bot", error_message)

                return {"message": error_message}

            results = execution_result.get("results")

            
            if not results:
                response = "I couldn't find any results matching your query."
                self.add_to_history("bot", response)

                return {"message": response}


            try:
                format_start = time.time()
                response = format_with_gemini(results, user_input)
                format_elapsed = time.time() - format_start

            except Exception as format_error:


                response = f"Results: {str(results)}"
            
            # Add robot emoji to response for web interface
            response = "🤖 " + response 
            self.add_to_history("bot", response)
            
            total_elapsed = time.time() - start_time

            return {"message": response}
        
        except Exception as e:


            return {"message": f"🔴 Sorry, I encountered an unexpected error: {type(e).__name__}"}

    def run(self):
        self.greet()
        while True:

            user_input = input("💬 You: ")
            if user_input.lower() in ('exit', 'quit', 'bye'):
                self.display_message(FAREWELL_MESSAGE)
                break
            elif user_input.lower() in ('help', '?'):
                self.display_message(HELP_MESSAGE)
                continue
            elif user_input.lower() in ('clear', 'cls'):
                clear_screen()
                self.greet()
                continue
            elif not user_input.strip():
                continue
            self.process_query(user_input)

def start_chat():
    """Start the chatbot."""
    bot = SoundScoreBot()
    bot.run()
