import re
import json
from .prompt_handler import convert_prompt_to_sql
import google.generativeai as genai
import os

def execute_query(query):
    """Stub for SQL execution. Replace with Django ORM or custom logic."""
    # Example: raise NotImplementedError or return a fake result for testing
    raise NotImplementedError("Direct SQL execution is not supported. Please implement using Django ORM.")

def extract_table(query):
    """Simple table extraction from query."""
    # Try to extract the table name from the FROM clause
    match = re.search(r'\bFROM\s+(\w+)', query, re.IGNORECASE)
    if match:
        table = match.group(1)
        # Ensure table name has the soundscore_ prefix
        if not table.startswith("soundscore_"):
            if table in ["users", "user"]:
                return "soundscore_user"
            elif table in ["reviews", "review"]:
                return "soundscore_review"
            elif table in ["albums", "album"]:
                return "soundscore_album"
        return table
    return None

# --- Add history parameter ---
def format_with_gemini(results, query, history=None):
    """Format results using Gemini AI with improved prompt and history."""
    import google.generativeai as genai
    from decouple import config
    import traceback
    import time

    start_time = time.time()
    
    # Check if results is an error object or empty
    if not results or (isinstance(results, dict) and 'error' in results):
        print(f"[DEBUG] Error or empty results detected: {results}")
        return "Sorry, I could not find what you requested."
    
    if isinstance(results, list) and len(results) == 0:
        print("[DEBUG] Empty results list")
        return "Sorry, I could not find what you requested."
    
    # Filter out sensitive data before processing
    filtered_results = filter_sensitive_data(results)
    
    # Print the exact results structure
    print(f"[DEBUG] Filtered results structure (sensitive data removed)")
    
    # Clean up results to remove duplicates if needed
    cleaned_results = filtered_results
    if isinstance(filtered_results, list) and len(filtered_results) > 0:
        # If results contain only usernames, de-duplicate them
        if all(len(item) == 1 and 'username' in item for item in filtered_results):
            unique_usernames = set(item['username'] for item in filtered_results if item['username'])
            print(f"[DEBUG] Unique usernames: {unique_usernames}")
            cleaned_results = [{'username': username} for username in unique_usernames]
            print(f"[DEBUG] De-duplicated results: {cleaned_results}")

    try:
        api_key = config("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Build history section
        history_section = ""
        if history:
            history_section = f"""
        ### CONVERSATION HISTORY (For context)
        {history}
        ---
        """
        
        # Add context about the query execution
        query_context = ""
        if "1 star" in query.lower() or "one star" in query.lower() or "rating = 1" in query.lower():
            query_context = """
        IMPORTANT CONTEXT: If the results show album information, and the query was about finding albums with 1-star reviews, 
        then the albums in the results DO have 1-star reviews. That's why they were returned by the query.
        """

        prompt_text = f"""
        {history_section}

        ### USER QUERY
        "{query}"

        ### DATABASE RESULTS
        {str(cleaned_results)[:2000]}

        {query_context}

        ### QUERY EXPLANATION
        The database was searched based on the user's question. If results were returned, they directly answer the question.
        For example:
        - If the user asked about albums with 1-star reviews and album results were returned, those ARE the albums with 1-star reviews.
        - If the user asked who wrote reviews and usernames were returned, those ARE the users who wrote those reviews.
        - The results might not show all details, but the filtering conditions from the query have been APPLIED.

        ### YOUR TASK
        Answer the user's question based on these results:
        - Use a friendly, conversational tone
        - If results were returned, they contain the answer - NEVER say you don't have information that's implied by the results
        - Focus on directly answering the question using only the information provided
        - If multiple items match, list them all
        - Don't explain database queries or how you got the information
        - Use spaces nicely.
        """
        
        # Add a direct try for just the API call
        try:
            response = model.generate_content(prompt_text)
            elapsed = time.time() - start_time
            
            # Response validation
            if not hasattr(response, 'text') or not response.text:
                return f"I found some results, but couldn't format them properly."
                
            return response.text.strip()
            
        except Exception as api_error:
            if 'timeout' in str(api_error).lower():
                return f"I found information but the formatting service timed out. Here's what I found: {str(cleaned_results)[:200]}"
            raise
        
    except Exception as e:
        elapsed = time.time() - start_time
        
        # Try a simpler fallback with a different model
        try:
            model = genai.GenerativeModel("gemini-1.0-pro")
            simple_prompt = f"Here are the results: {str(cleaned_results)[:500]}. The user asked: '{query}'. Please provide a direct, accurate answer based only on this data."
            response = model.generate_content(simple_prompt)
            if hasattr(response, 'text') and response.text:
                return response.text.strip()
        except Exception as fallback_error:
            # If all fails, return raw results
            return f"Here are the results: {str(cleaned_results)[:500]}..."


def filter_sensitive_data(results):
    """Remove sensitive data like passwords, emails, and IDs before sending to LLM."""
    if not results:
        return results
        
    # List of sensitive fields to filter out (case insensitive)
    sensitive_fields = (
        # Authentication related
        'password', 'passwd', 'pass', 'hash', 'salt', 
        # API access related
        'secret', 'token', 'api_key', 'key',
        # Personal identifiers
        'email', 'id', 'user_id', 'recipient_id', 'sender_id'
    )
        
    # Handle list of dictionaries
    if isinstance(results, list):
        filtered_results = []
        for item in results:
            if isinstance(item, dict):
                # Remove sensitive fields
                filtered_item = {k: v for k, v in item.items() 
                               if k.lower() not in sensitive_fields}
                filtered_results.append(filtered_item)
            else:
                filtered_results.append(item)
        return filtered_results
    
    # Handle single dictionary
    elif isinstance(results, dict):
        return {k: v for k, v in results.items() 
                if k.lower() not in sensitive_fields}
    
    return results