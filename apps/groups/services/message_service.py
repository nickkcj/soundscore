from apps.groups.models import Group, GroupMessage, GroupMember
from apps.users.models import User

def save_message(group_id, user_id, content):
    try:
        group = Group.objects.get(id=group_id)
        user = User.objects.get(id=user_id)
        message = GroupMessage.objects.create(
            group=group,
            user=user,
            content=content
        )
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
    try:
        messages = (
            GroupMessage.objects
            .filter(group_id=group_id)
            .select_related('user')
            .order_by('-timestamp')[:limit]
        )
        formatted_messages = [{
            "content": msg.content,
            "username": msg.user.username,
            "user_id": msg.user.id,
            "profile_picture": getattr(msg.user, "profile_picture", "/static/images/default.jpg")
        } for msg in messages]
        return formatted_messages
    except Exception as e:
        return []
