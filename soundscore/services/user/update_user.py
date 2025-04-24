from .supabase_client import authenticate_with_jwt, get_admin_client
import os
import base64

def update_user_supabase(old_username, new_username, email=None, password=None, profile_picture=None):
    """
    Updates user information in Supabase
    """
    try:
        client = get_admin_client()
        if not client:
            return {"error": "Could not connect to Supabase"}
        
        # Get the user ID from Supabase
        user_response = client.table('soundscore_user').select('id').eq('username', old_username).limit(1).execute()
        if not user_response.data:
            return {"error": f"User '{old_username}' not found in Supabase"}
        
        supabase_user_id = user_response.data[0]['id']
        update_data = {}
        
        # Check if new username already exists (but only if it's different from current)
        if new_username and new_username != old_username:
            existing_user = client.table('soundscore_user').select('id').eq('username', new_username).limit(1).execute()
            if existing_user.data:
                return {"error": f"Username '{new_username}' is already taken"}
            update_data['username'] = new_username
        elif new_username:
            # Username is the same as current, no need to update
            pass
        
        # Check if email needs to be updated
        if email:
            # Check if new email is already in use by another account
            existing_email = client.table('soundscore_user').select('id').eq('email', email).neq('id', supabase_user_id).limit(1).execute()
            if existing_email.data:
                return {"error": f"Email '{email}' is already in use by another account"}
            update_data['email'] = email
        
        if password:
            update_data['password'] = password
        
        # Handle profile picture if provided
        if profile_picture:
            # Rest of profile picture handling code remains unchanged
            import os
            name, ext = os.path.splitext(profile_picture.name)
            file_name = f"{old_username[:10]}_{name[:20]}{ext}"
            file_content = profile_picture.read()
            
            # Upload to Supabase Storage
            bucket = client.storage.from_('avatars')
            bucket.remove(file_name)  # Try deleting if it already exists
            storage_response = client.storage.from_('avatars').upload(
                file=file_content,
                path=file_name,
                file_options={"content-type": profile_picture.content_type}  
            )
            
            if hasattr(storage_response, 'error') and storage_response.error:
                return {"error": f"Error uploading profile picture: {storage_response.error}"}
            
            public_url = client.storage.from_('avatars').get_public_url(file_name)
            update_data['profile_picture'] = public_url
        
        # Update the user in Supabase
        if update_data:
            update_response = client.table('soundscore_user').update(update_data).eq('id', supabase_user_id).execute()
            if hasattr(update_response, 'error') and update_response.error:
                return {"error": f"Error updating user in Supabase: {update_response.error}"}
        
        return {"success": True, "message": "User updated successfully in Supabase"}
        
    except Exception as e:
        return {"error": f"Error updating user in Supabase: {str(e)}"}