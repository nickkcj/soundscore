import google.generativeai as genai
from decouple import config
import re
import traceback
import time

# --- Add history parameter ---
def convert_prompt_to_sql(prompt, history=None):
# --- ---
    """Convert a natural language prompt to SQL using Gemini API only."""
    print(f"\n[DEBUG] convert_prompt_to_sql called with: {prompt[:50]}...")
    start_time = time.time()
    try:

        api_key = config("GOOGLE_API_KEY")

        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash") # Use pro for better context handling

        # --- Build history string for prompt ---
        history_section = ""
        if history:
            history_section = f"""
                            ### CONVERSATION HISTORY (Use this for context)
                            {history}
                            ---
                            """
        # --- ---

        print("[DEBUG] Sending prompt to Gemini API...")
        response = model.generate_content(
            contents = f"""You are a PostgreSQL expert. Your job is to convert user questions into clean, safe SQL queries based on the provided schema and conversation history.

                            ### SCHEMA

                            **Tables** (ALWAYS use EXACTLY these table names with no schema prefixes):

                            - **soundscore_user**
                            - Columns: `id`, `username`, `email`, `created_at`

                            - **soundscore_review**
                            - Columns: `id`, `rating`, `text`, `created_at`, `user_id`, `album_id`
                            - Foreign Keys:
                                - `user_id → soundscore_user.id`
                                - `album_id → soundscore_album.id`

                            - **soundscore_album**
                            - Columns: `id`, `title`, `artist`, `release_date`

                            ### FOREIGN KEY USAGE

                            - Use `soundscore_review.user_id` to access user information from `soundscore_user`
                            - Use `soundscore_review.album_id` to access album information from `soundscore_album`
                            - Always use **INNER JOIN** when joining related tables through foreign keys
                            - You can and should follow these relationships to compute things like:
                            - Review counts per album
                            - Average rating per album
                            - Which user wrote a specific review
                            - What albums a user has reviewed, etc.

                            ### CRITICAL RULES

                            - NEVER use table names like `"users"`, `"reviews"` or `"albums"` – ALWAYS use `"soundscore_user"`, `"soundscore_review"`, and `"soundscore_album"`
                            - NEVER use schema prefixes like `"public."` before table names
                            - Output only raw SQL (no explanations, no markdown)
                            - Never quote numeric values (e.g. use `id = 4`, not `'4'`)
                            - Always use `INNER JOIN` for cross-table queries
                            - Use `LIMIT` where appropriate

                            {history_section}

                            ### EXAMPLES

                            - "Show latest reviews"  
                            `SELECT * FROM soundscore_review ORDER BY created_at DESC LIMIT 5`

                            - "Show best albums"  
                            `SELECT soundscore_album.*, AVG(soundscore_review.rating) as avg_rating FROM soundscore_album INNER JOIN soundscore_review ON soundscore_album.id = soundscore_review.album_id GROUP BY soundscore_album.id ORDER BY avg_rating DESC LIMIT 5`

                            - "Who wrote the most reviews"  
                            `SELECT soundscore_user.username, COUNT(*) as review_count FROM soundscore_review INNER JOIN soundscore_user ON soundscore_review.user_id = soundscore_user.id GROUP BY soundscore_user.id, soundscore_user.username ORDER BY review_count DESC LIMIT 5`

                            - "What is the worst rated album"  
                            `SELECT soundscore_album.*, AVG(soundscore_review.rating) as avg_rating FROM soundscore_album INNER JOIN soundscore_review ON soundscore_album.id = soundscore_review.album_id GROUP BY soundscore_album.id ORDER BY avg_rating ASC LIMIT 1`

                            - "What album was reviewed the most"  
                            `SELECT soundscore_album.title, COUNT(soundscore_review.id) as review_count FROM soundscore_album INNER JOIN soundscore_review ON soundscore_album.id = soundscore_review.album_id GROUP BY soundscore_album.id, soundscore_album.title ORDER BY review_count DESC LIMIT 1`

                            ---

                            USER QUESTION (Respond only to this question, using history for context):
                            {prompt}

                            ---
                            SQL QUERY (Generate only the SQL query):
            """
        )

        
        # Add response validation
        if not hasattr(response, 'text') or not response.text:

            return {"sql": None, "source": "error", "message": "Empty response from Gemini"}
            
        # Extract SQL from response
        raw_response = response.text.strip()
        sql = raw_response
        
        # Clean up the response - remove markdown formatting if present
        if "```" in sql:
            sql = re.search(r"```(?:sql)?\s*(.*?)\s*```", sql, re.DOTALL).group(1)
            
        # Remove comments and clean up whitespace
        sql = re.sub(r"--.*", "", sql)
        sql = sql.replace("\n", " ").strip()
        sql = re.sub(r"\s+", " ", sql)
        
        # Fix numeric values (remove quotes from numeric IDs)
        sql = re.sub(r"(\b\w*_id|\bid)\s*=\s*['\"](\d+)['\"]", r"\1 = \2", sql)
        sql = re.sub(r"(\b\w*_id|\bid)\s*=\s*['\"]?(\d+);['\"]?", r"\1 = \2", sql)

        elapsed = time.time() - start_time

        return {
            "sql": sql,
            "source": "gemini",
            "message": "Generated SQL query."
        }

    except Exception as e:
        elapsed = time.time() - start_time
        return {"sql": None, "source": "error", "message": str(e), "trace": traceback.format_exc()}
    finally:
        print(f"[DEBUG] convert_prompt_to_sql completed in {elapsed:.2f} seconds.")

