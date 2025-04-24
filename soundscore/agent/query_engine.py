import re
from ..services.user.supabase_client import authenticate_with_jwt

def execute_query(query):
    """Execute SQL query through Supabase API with minimal parsing."""
    try:
        # Get authenticated client
        client = authenticate_with_jwt()
        if not client:
            return {"results": None, "success": False, "error": "Authentication failed"}

        # Handle direct SQL execution for JOINs and complex queries
        if " join " in query.lower() or "group by" in query.lower():
            # Execute raw SQL through RPC
            response = client.rpc('execute_sql', {'sql_query': query}).execute()
            if response.data:
                return {"results": response.data, "success": True}
            else:
                return {"results": None, "success": False, "error": "Query failed"}
            
        # For simpler queries, parse more details
        table_name = extract_table(query)
        
        if not table_name:
            return {"results": None, "success": False, "error": "Could not determine table name from query"}

        # Parse ORDER BY clause
        order_match = re.search(r'ORDER\s+BY\s+(\w+)(?:\s+(ASC|DESC))?', query, re.IGNORECASE)
        order_column = None
        order_direction = None
        if order_match:
            order_column = order_match.group(1)
            order_direction = order_match.group(2) or 'ASC'
        
        # Parse LIMIT clause
        limit_match = re.search(r'LIMIT\s+(\d+)', query, re.IGNORECASE)
        limit = int(limit_match.group(1)) if limit_match else None
        
        # Build the query
        db_query = client.table(table_name).select("*")
        
        # Apply ORDER BY if found
        if order_column:
            is_desc = (order_direction.upper() == 'DESC')
            db_query = db_query.order(order_column, desc=is_desc)
            
        # Apply LIMIT if found
        if limit:
            db_query = db_query.limit(limit)
        
        # Execute the query
        response = db_query.execute()
        return {"results": response.data, "success": True}
        
    except Exception as e:

        return {"results": None, "success": False, "error": str(e)}

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

def format_with_gemini(results, query):
    """Format results using Gemini AI with improved prompt."""
    import google.generativeai as genai
    from decouple import config
    import traceback
    import time



    start_time = time.time()

    try:

        api_key = config("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        

        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Build a better prompt for Gemini
        prompt_text = f"""
        Here are the database query results for a music review database: 
        {str(results)[:2000]}
        
        The user asked: "{query}"
        
        Based ONLY on these results, answer the user's question in a friendly conversational tone.
        Focus on directly addressing what the user asked about.
        If the results don't contain relevant information, say so clearly.
        Don't explain the data structure or mention SQL/databases in your answer.
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
                return f"I found information but the formatting service timed out. Here's what I found: {str(results)[:200]}"
            raise  # Re-raise to be caught by outer exception handler
        
    except Exception as e:
        elapsed = time.time() - start_time



        
        # Try a simpler fallback with a different model
        try:

            model = genai.GenerativeModel("gemini-1.0-pro")  # Try older model
            simple_prompt = f"Summarize this data: {str(results)[:500]}. Question was: {query}"
            response = model.generate_content(simple_prompt)
            if hasattr(response, 'text') and response.text:

                return response.text.strip()
        except Exception as fallback_error:
            # If all fails, return raw results
            return f"Here are the results: {str(results)[:500]}..."