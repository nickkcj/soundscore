from apps.users.models import User
from django.conf import settings


def create_user(username, email, password):
    """
    Creates a new user with default Supabase profile picture.
    """
    try:
        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            return {"success": False, "message": "Username already exists"}
        
        if User.objects.filter(email=email).exists():
            return {"success": False, "message": "Email already exists"}
        
        # Use your uploaded default image URL
        default_profile_url = f"{settings.SUPABASE_URL}/storage/v1/object/public/profilepictures/2301-default-2.png"
        
        # Create the user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            profile_picture=default_profile_url
        )
        
        return {"success": True, "message": "User created successfully"}
        
    except Exception as e:
        return {"success": False, "message": str(e)}


