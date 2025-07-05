from apps.users.models import User
from apps.users.services.supabase_storage import SupabaseStorageService
from django.conf import settings

def update_user_data(old_username, new_username=None, email=None, password=None, profile_picture=None):
    """
    Updates user data including profile picture upload to Supabase.
    """
    try:
        # Find the user by old username
        user = User.objects.get(username=old_username)
        storage_service = SupabaseStorageService()
        
        # Update basic fields
        if new_username and new_username != old_username:
            if User.objects.filter(username=new_username).exclude(id=user.id).exists():
                return {"success": False, "error": "Username already exists"}
            user.username = new_username
            
        if email and email != user.email:
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                return {"success": False, "error": "Email already exists"}
            user.email = email
            
        if password:
            user.set_password(password)
        
        # Handle profile picture upload
        if profile_picture:
            # Delete old profile picture if it's not default
            if user.profile_picture and user.profile_picture != settings.DEFAULT_PROFILE_PICTURE:
                storage_service.delete_profile_picture(user.profile_picture)
            
            # Upload new profile picture
            upload_result = storage_service.upload_profile_picture(profile_picture, user.id)
            
            if upload_result["success"]:
                user.profile_picture = upload_result["url"]
            else:
                return {"success": False, "error": f"Failed to upload image: {upload_result['error']}"}
        
        # Save user
        user.save()
        
        return {"success": True, "message": "User updated successfully"}
        
    except User.DoesNotExist:
        return {"success": False, "error": "User not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}