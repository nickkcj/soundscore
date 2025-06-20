from apps.users.models import User
from django.contrib.auth.hashers import make_password


def create_user(username, email, password):
    """Create a new user with the given username, email, and password."""
    try:
        if User.objects.filter(username=username).exists():
            return {
                "success": False,
                "message": "Username already exists"
            }

        if User.objects.filter(email=email).exists():
            return {
                "success": False,
                "message": "Email already exists"
            }

        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            profile_picture='core/static/images/default.jpg',
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
        return {
            "success": False,
            "message": str(e)
        }


