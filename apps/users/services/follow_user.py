from apps.users.models import User, UserRelationship
from django.core.paginator import Paginator

def follow_service(user_id, target_username):
    """
    Follow a user.
    
    :param user_id: The ID of the user who is following.
    :param target_username: The username of the user to be followed.
    :return: A dictionary with success status and message.
    """
    try:
        user = User.objects.get(id=user_id)
        target_user = User.objects.get(username=target_username)
        
        if user == target_user:
            return {"success": False, "message": "You cannot follow yourself."}

        if UserRelationship.objects.filter(user_id=user, following=target_user).exists():
            return {"success": False, "message": "You are already following this user."}

        UserRelationship.objects.create(user_id=user, following=target_user)
        return {"success": True, "message": f"You are now following {target_user.username}."}
    
    except User.DoesNotExist:
        return {"success": False, "message": "User not found."}
    except Exception as e:
        return {"success": False, "message": str(e)}


def unfollow_service(user_id, target_username):
    """
    Unfollow a user.
    
    :param user_id: The ID of the user who is unfollowing.
    :param target_username: The username of the user to be unfollowed.
    :return: A dictionary with success status and message.
    """
    try:
        user = User.objects.get(id=user_id)
        target_user = User.objects.get(username=target_username)
        
        relationship = UserRelationship.objects.filter(user_id=user, following=target_user).first()
        
        if not relationship:
            return {"success": False, "message": "You are not following this user."}

        relationship.delete()
        return {"success": True, "message": f"You have unfollowed {target_user.username}."}
    
    except User.DoesNotExist:
        return {"success": False, "message": "User not found."}
    except Exception as e:
        return {"success": False, "message": str(e)}


