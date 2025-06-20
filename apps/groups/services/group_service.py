from apps.groups.models import ChatGroup, ChatGroupMember, ChatGroupMessage, GroupUserOnline
from apps.users.models import User
import uuid

def create_group(name, description, category, privacy, cover_image_file, username):
    try:
        user = User.objects.get(username=username)
        # Handle cover image
        if cover_image_file:
            filename = f"group_covers/{uuid.uuid4()}.{cover_image_file.name.split('.')[-1]}"
            # Save file to media storage
            group = ChatGroup(
                name=name,
                description=description,
                category=category,
                privacy=privacy,
                cover_image=cover_image_file
            )
            group.save()
        else:
            group = ChatGroup.objects.create(
                name=name,
                description=description,
                category=category,
                privacy=privacy,
                cover_image="/static/images/default.jpg"
            )
        # Add creator as member
        ChatGroupMember.objects.create(group=group, user=user)
        return group.id
    except Exception as e:
        raise Exception(f"Error creating group: {e}")

def get_all_groups():
    try:
        all_groups = list(ChatGroup.objects.all())
        for group in all_groups:
            group.member_count = ChatGroupMember.objects.filter(group=group).count()
        trending = sorted(all_groups, key=lambda x: getattr(x, "member_count", 0), reverse=True)[:4]
        return {
            "groups": all_groups,
            "trending_groups": trending
        }
    except Exception as e:
        return {"groups": [], "trending_groups": []}

def join_group(group_id, username):
    try:
        user = User.objects.get(username=username)
        group = ChatGroup.objects.get(id=group_id)
        ChatGroupMember.objects.get_or_create(group=group, user=user)
        return True
    except Exception as e:
        return False

def get_group_room_data(group_id, username):
    try:
        user = User.objects.get(username=username)
        group = ChatGroup.objects.get(id=group_id)
        members = ChatGroupMember.objects.filter(group=group).select_related('user')
        online_ids = set(
            GroupUserOnline.objects.filter(group=group, is_online=True).values_list('user_id', flat=True)
        )
        member_list = [{
            "user_id": m.user.id,
            "username": m.user.username,
            "profile_picture": getattr(m.user, "profile_picture", "/static/images/default.jpg"),
            "is_online": m.user.id in online_ids,
        } for m in members]
        messages = ChatGroupMessage.objects.filter(group=group).select_related('user')
        formatted_messages = [{
            "content": msg.content,
            "username": msg.user.username,
            "user_id": msg.user.id,
            "profile_picture": getattr(msg.user, "profile_picture", "/static/images/default.jpg")
        } for msg in messages]
        return {
            "group": group,
            "group_id": group_id,
            "member_count": len(member_list),
            "members": member_list,
            "recent_messages": formatted_messages,
            "current_username": username,
        }
    except Exception as e:
        return {}

def get_groups_by_user(username):
    try:
        user = User.objects.get(username=username)
        memberships = ChatGroupMember.objects.filter(user=user)
        group_ids = [m.group.id for m in memberships]
        if not group_ids:
            return []
        groups = ChatGroup.objects.filter(id__in=group_ids)
        return groups
    except Exception as e:
        return []