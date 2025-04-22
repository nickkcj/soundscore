from .supabase_client import authenticate_with_jwt, get_admin_client
import os
import base64

def update_user_supabase(username, email=None, password=None, profile_picture=None):
    """
    Updates user information in Supabase
    """
    try:
        client = get_admin_client()
        if not client:
            return {"error": "Could not connect to Supabase"}
        
        # Get the user ID from Supabase
        user_response = client.table('soundscore_user').select('id').eq('username', username).limit(1).execute()
        if not user_response.data:
            return {"error": f"User '{username}' not found in Supabase"}
        
        supabase_user_id = user_response.data[0]['id']
        update_data = {}
        
        # Add fields to update
        if email:
            update_data['email'] = email
        
        if password:
            update_data['password'] = password  # Note: You may need to hash this depending on your setup
        
        # Handle profile picture if provided
        if profile_picture:
            # Convert Django's InMemoryUploadedFile to a format suitable for Supabase storage
            import os
            name, ext = os.path.splitext(profile_picture.name)
            file_name = f"{username[:10]}_{name[:20]}{ext}"
            file_content = profile_picture.read()  # Read binary content
            
            # Upload to Supabase Storage
            storage_response = client.storage.from_('avatars').upload(
                file=file_content,
                path=file_name,
                file_options={"content-type": profile_picture.content_type,
                              "upsert": True}  
            )
            
            if hasattr(storage_response, 'error') and storage_response.error:
                return {"error": f"Error uploading profile picture: {storage_response.error}"}
            
            # Get public URL and store in user record
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