from apps.groups.models import Group, GroupMember, GroupMessage  # fixed import
from apps.users.models import User
import uuid

def create_group(name, description, category, privacy, cover_image_file, username):
    try:
        user = User.objects.get(username=username)
        if cover_image_file:
            filename = f"group_covers/{uuid.uuid4()}.{cover_image_file.name.split('.')[-1]}"
            group = Group(
                name=name,
                description=description,
                category=category,
                privacy=privacy,
                cover_image=cover_image_file
            )
            group.save()
        else:
            group = Group.objects.create(
                name=name,
                description=description,
                category=category,
                privacy=privacy,
                cover_image="/static/images/default.jpg"
            )
        GroupMember.objects.create(group=group, user=user)
        return group.id
    except Exception as e:
        raise Exception(f"Error creating group: {e}")

def get_all_groups():
    try:
        all_groups = list(Group.objects.all())
        for group in all_groups:
            group.member_count = GroupMember.objects.filter(group=group).count()
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
        group = Group.objects.get(id=group_id)
        GroupMember.objects.get_or_create(group=group, user=user)
        return True
    except Exception as e:
        return False

def get_group_room_data(group_id, username):
    try:
        user = User.objects.get(username=username)
        group = Group.objects.get(id=group_id)
        members = GroupMember.objects.filter(group=group).select_related('user')
        # Remove GroupUserOnline logic unless you add that model
        member_list = [{
            "user_id": m.user.id,
            "username": m.user.username,
            "profile_picture": getattr(m.user, "profile_picture", "/static/images/default.jpg"),
            "is_online": False,  # or implement online logic if needed
        } for m in members]
        messages = GroupMessage.objects.filter(group=group).select_related('user')
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
        memberships = GroupMember.objects.filter(user=user)
        group_ids = [m.group.id for m in memberships]
        if not group_ids:
            return []
        groups = Group.objects.filter(id__in=group_ids)
        return groups
    except Exception as e:
        return []