from .supabase_client import authenticate_with_jwt
from postgrest import APIError

def delete_user_data_supabase(username):
    """
    Deletes a user's reviews and their entry from the soundscore_user table.
    Does NOT delete the user from Supabase Auth.
    """
    client = authenticate_with_jwt()
    if not client:
        return {"error": "Failed to authenticate with Supabase"}

    try:
        # 1. Get the Supabase user ID from the username
        user_response = client.table('soundscore_user').select('id').eq('username', username).limit(1).execute()

        if not user_response.data:
            # User might already be partially deleted or never existed in this table
            return {"warning": f"User '{username}' not found in soundscore_user table. No data deleted from custom tables."}

        supabase_user_id = user_response.data[0]['id']

        # 2. Delete user's reviews first (due to potential foreign key constraints)
        print(f"Attempting to delete reviews for user_id: {supabase_user_id}")
        delete_reviews_response = client.table('soundscore_review').delete().eq('user_id', supabase_user_id).execute()
        # Check for errors specifically, as delete might return empty data on success
        # This part depends heavily on how your Supabase client library handles errors.
        # Assuming no exception means success for now. Add specific error checking if needed.
        print(f"Delete reviews response: {delete_reviews_response.data}")


        # 3. Delete the user from the soundscore_user table
        print(f"Attempting to delete user from soundscore_user table, id: {supabase_user_id}")
        delete_user_response = client.table('soundscore_user').delete().eq('id', supabase_user_id).execute()
        print(f"Delete user response: {delete_user_response.data}")

        # Check for errors specifically
        # Assuming no exception means success for now.

        return {"success": True, "message": "User data deleted successfully from custom tables."}

    except APIError as e:
        print(f"[ERROR] Supabase API Error deleting user data: {e.message}, Code: {e.code}, Details: {e.details}")
        return {"error": f"Supabase error deleting user data: {e.message}"}
    except Exception as e:
        print(f"[ERROR] Unexpected error deleting user data: {str(e)}")
        return {"error": f"An unexpected error occurred: {str(e)}"}