from apps.groups.models import ChatGroup, ChatGroupMessage, ChatGroupMember
from apps.users.models import User

def save_message(group_id, user_id, content):
    try:
        group = ChatGroup.objects.get(id=group_id)
        user = User.objects.get(id=user_id)
        message = ChatGroupMessage.objects.create(
            group=group,
            user=user,
            content=content
        )
        return {
            "id": message.id,
            "group_id": group_id,
            "user_id": user_id,
            "content": content,
            "created_at": message.created_at
        }
    except Exception as e:
        return None

def get_recent_messages(group_id, limit=50):
    try:
        messages = (
            ChatGroupMessage.objects
            .filter(group_id=group_id)
            .select_related('user')
            .order_by('-created_at')[:limit]
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
