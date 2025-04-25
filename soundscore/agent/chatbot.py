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
        print(f"\n[DEBUG] get_response called with: {user_input}")
        start_time = time.time()

        # --- Add current message to history FIRST ---
        self.add_to_history("user", user_input)
        # --- ---

        # Handle special commands (no history needed for these)
        user_input_lower = user_input.lower()
        if user_input_lower in ('exit', 'quit', 'bye'):
            # Add bot farewell before returning
            self.add_to_history("bot", FAREWELL_MESSAGE)
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
        
        # --- Prepare conversation history for prompts ---
        history_limit = 5 # Keep last 5 turns (user + bot)
        recent_history = self.conversation_history[-history_limit:]
        history_for_prompt = "\n".join([f"{turn['speaker']}: {turn['message']}" for turn in recent_history])
        print(f"[DEBUG] History for prompt:\n{history_for_prompt}")
        # --- ---

        try:
            print("[DEBUG] Calling convert_prompt_to_sql...")
            # --- Pass history to SQL generation ---
            query_result = convert_prompt_to_sql(user_input, history=history_for_prompt)
            # --- ---
            print(f"[DEBUG] convert_prompt_to_sql returned: {query_result}")

            sql = query_result.get("sql")
            if not sql:
                response = f"I'm sorry, I couldn't understand that query. {query_result.get('message', 'Unknown error')}"
                # Add bot error message to history before returning
                self.add_to_history("bot", response)
                print(f"[DEBUG] No SQL generated, returning error: {response}")
                return {"message": "🤖 " + response} # Add emoji here

            print(f"[DEBUG] Executing SQL: {sql}")
            execution_result = execute_query(sql)
            print(f"[DEBUG] execute_query success: {execution_result.get('success')}")

            if not execution_result.get("success"):
                error_message = f"I encountered an error running that query: {execution_result.get('error', 'Unknown database error')}"
                 # Add bot error message to history before returning
                self.add_to_history("bot", error_message)
                print(f"[DEBUG] Query execution failed: {error_message}")
                return {"message": "🤖 " + error_message} # Add emoji here

            results = execution_result.get("results")
            print(f"[DEBUG] Got {len(results) if results else 0} results")

            if not results:
                response = "I couldn't find any results matching your query."
                 # Add bot message to history before returning
                self.add_to_history("bot", response)
                print("[DEBUG] No results found")
                return {"message": "🤖 " + response} # Add emoji here

            print("[DEBUG] Calling format_with_gemini...")
            try:
                format_start = time.time()
                # --- Pass history and user_input to formatting ---
                response = format_with_gemini(results, user_input, history=history_for_prompt)
                # --- ---
                format_elapsed = time.time() - format_start
                print(f"[DEBUG] format_with_gemini returned in {format_elapsed:.2f}s: {response[:100]}...")
            except Exception as format_error:
                print(f"[DEBUG ERROR] format_with_gemini failed: {format_error}")
                print(traceback.format_exc())
                response = f"Results: {str(results)}" # Fallback formatting

            # Add final bot response to history
            self.add_to_history("bot", response) # Store the plain response

            total_elapsed = time.time() - start_time
            print(f"[DEBUG] get_response completed in {total_elapsed:.2f} seconds")
            # Add emoji just before returning
            return {"message": "🤖 " + response}

        except Exception as e:
            print(f"[DEBUG CRITICAL ERROR] Uncaught exception in get_response: {type(e).__name__}: {e}")
            print(traceback.format_exc())
            error_response = f"Sorry, I encountered an unexpected error: {type(e).__name__}"
            # Add bot error message to history before returning
            self.add_to_history("bot", error_response)
            return {"message": "🔴 " + error_response} # Add emoji here

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
