from apps.users.models import User
from django.db import transaction

def update_user_data(old_username, new_username, email=None, password=None, profile_picture=None):
    """Updates user information in the local database (dbsqlite3)"""
    try:
        with transaction.atomic():
            # Get the user by old_username
            try:
                user = User.objects.get(username=old_username)
            except User.DoesNotExist:
                return {"error": f"User '{old_username}' not found in database"}

            # Check if new username already exists (and is different)
            if new_username and new_username != old_username:
                if User.objects.filter(username=new_username).exists():
                    return {"error": f"Username '{new_username}' is already taken"}
                user.username = new_username

            # Check if email needs to be updated
            if email:
                if User.objects.filter(email=email).exclude(id=user.id).exists():
                    return {"error": f"Email '{email}' is already in use by another account"}
                user.email = email

            # Update password if provided
            if password:
                user.set_password(password)  # Use set_password for hashing

            # Handle profile picture if provided
            if profile_picture:
                # Save the uploaded file to the user's profile_picture field
                # Assuming profile_picture is a Django File object
                user.profile_picture.save(profile_picture.name, profile_picture, save=False)

            user.save()
        return {"success": True, "message": "User updated successfully in database"}
    except Exception as e:
        return {"error": f"Error updating user in database: {str(e)}"}