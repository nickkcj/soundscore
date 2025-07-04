from apps.groups.models import Group, GroupMessage, GroupMember
from apps.users.models import User

def save_message(group_id, user_id, content):
    """
    Save a new message to a group chat.
    Parameters:
        group_id (int): ID of the group
        user_id (int): ID of the user sending the message
        content (str): Message content
    Returns:
        dict: Message data if successful, None otherwise
    """
    try:
        # Get group and user objects
        group = Group.objects.get(id=group_id)
        user = User.objects.get(id=user_id)
        # Create the message
        message = GroupMessage.objects.create(
            group=group,
            user=user,
            content=content
        )
        # Return message data for frontend
        return {
            "id": message.id,
            "group_id": group_id,
            "user_id": user_id,
            "content": content,
            "created_at": message.timestamp
        }
    except Exception as e:
        return None

def get_recent_messages(group_id, limit=50):
    """
    Get the most recent messages for a group.
    Parameters:
        group_id (int): ID of the group
        limit (int): Max number of messages to return (default 50)
    Returns:
        list: Formatted message dicts
    """
    try:
        # Get recent messages for the group, newest first
        messages = (
            GroupMessage.objects
            .filter(group_id=group_id)
            .select_related('user')
            .order_by('-timestamp')[:limit]
        )
        # Format messages for frontend
        formatted_messages = [{
            "content": msg.content,
            "username": msg.user.username,
            "user_id": msg.user.id,
            "profile_picture": getattr(msg.user, "profile_picture", "/static/images/default.jpg")
        } for msg in messages]
        return formatted_messages
    except Exception as e:
        return []
