from apps.users.models import User
from django.contrib.auth.hashers import make_password


def create_user(username, email, password):
    """
    Create a new user with the given username, email, and password.
    Parameters:
        username (str): Desired username
        email (str): User's email address
        password (str): Plaintext password
    Returns:
        dict: Success status, message, and user_id if successful
    """
    try:
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return {
                "success": False,
                "message": "Username already exists"
            }

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return {
                "success": False,
                "message": "Email already exists"
            }

        # Create the user with hashed password
        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            is_active=True,
            is_superuser=False,
            is_staff=False,
        )

        return {
            "success": True,
            "message": "User created successfully",
            "user_id": user.id
        }

    except Exception as e:
        # Return error message if something goes wrong
        return {
            "success": False,
            "message": str(e)
        }


