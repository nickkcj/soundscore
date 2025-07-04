from apps.users.models import User

def delete_user_data(username):
    """
    Delete a user by username.
    Parameters:
        username (str): Username to delete
    Returns:
        dict: Success status and message
    """
    try:
        user = User.objects.get(username=username).first()
        if not user:
            return {
                "success": False,
                "message": "User does not exist"
            }
        
        user.delete()
        return {
            "success": True,
            "message": "User deleted successfully"
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }