from apps.groups.models import Group, GroupMember, GroupMessage
from apps.users.models import User
import uuid

def create_group(name, description, category, privacy, cover_image_file, username):
    """
    Create a new group and add the creator as a member.
    Parameters:
        name (str): Group name
        description (str): Group description
        category (str): Group category
        privacy (str): Privacy setting
        cover_image_file (File or None): Uploaded image file or None
        username (str): Username of the creator
    Returns:
        int: ID of the created group
    Raises:
        Exception: If creation fails
    """
    try:
        # Get the user who is creating the group
        user = User.objects.get(username=username)
        
        # Create the group (Django handles file upload for ImageField)
        group = Group.objects.create(
            name=name,
            description=description,
            category=category,
            privacy=privacy,
            cover_image=cover_image_file  # Can be None if no image uploaded
        )
        
        # Add the creator as a member of the group
        GroupMember.objects.create(group=group, user=user)
        return group.id
        
    except Exception as e:
        print(f"Error creating group: {e}")
        raise Exception(f"Error creating group: {e}")

def get_all_groups():
    """
    Retrieve all groups and calculate trending groups (top 4 by member count).
    Returns:
        dict: {
            "groups": list of all Group objects,
            "trending_groups": list of top 4 trending Group objects
        }
    """
    try:
        # Get all groups from the database
        all_groups = list(Group.objects.all())
        for group in all_groups:
            # Count members for each group
            group.member_count = GroupMember.objects.filter(group=group).count()
        # Sort groups by member count to get trending groups
        trending = sorted(all_groups, key=lambda x: getattr(x, "member_count", 0), reverse=True)[:4]
        return {
            "groups": all_groups,
            "trending_groups": trending
        }
    except Exception as e:
        return {"groups": [], "trending_groups": []}

def join_group(group_id, username):
    """
    Add a user to a group as a member.
    Parameters:
        group_id (int): ID of the group to join
        username (str): Username of the user joining
    Returns:
        bool: True if joined successfully, False otherwise
    """
    try:
        # Get user and group objects
        user = User.objects.get(username=username)
        group = Group.objects.get(id=group_id)
        # Add user as a member (does nothing if already a member)
        GroupMember.objects.get_or_create(group=group, user=user)
        return True
    except Exception as e:
        return False

def get_group_room_data(group_id, username):
    """
    Retrieve all data needed for a group chat room.
    Parameters:
        group_id (int): ID of the group
        username (str): Username of the requesting user
    Returns:
        dict: Group info, members, messages, etc.
    """
    try:
        # Get user and group objects
        user = User.objects.get(username=username)
        group = Group.objects.get(id=group_id)
        # Get all group members with related user info
        members = GroupMember.objects.filter(group=group).select_related('user')
        
        # Build member list with profile pictures
        member_list = []
        for m in members:
            profile_picture_url = "/static/images/default.jpg"
            if m.user.profile_picture:
                try:
                    profile_picture_url = m.user.profile_picture.url
                except:
                    pass
            
            member_list.append({
                "user_id": m.user.id,
                "username": m.user.username,
                "profile_picture": profile_picture_url,
                "is_online": False,  # Placeholder, implement online logic if needed
            })
        
        # Get all messages for this group
        messages = GroupMessage.objects.filter(group=group).select_related('user')
        
        # Build formatted message list with user profile pictures
        formatted_messages = []
        for msg in messages:
            profile_picture_url = "/static/images/default.jpg"
            if msg.user.profile_picture:
                try:
                    profile_picture_url = msg.user.profile_picture.url
                except:
                    pass
            
            formatted_messages.append({
                "content": msg.content,
                "username": msg.user.username,
                "user_id": msg.user.id,
                "profile_picture": profile_picture_url
            })
        
        # Return all room data
        return {
            "group": group,
            "group_id": group_id,
            "member_count": len(member_list),
            "members": member_list,
            "recent_messages": formatted_messages,
            "current_username": username,
        }
    except Exception as e:
        print(f"Error in get_group_room_data: {e}")
        return {}

def get_groups_by_user(username):
    """
    Get all groups that a user is a member of.
    Parameters:
        username (str): Username of the user
    Returns:
        list: Group objects the user belongs to
    """
    try:
        # Get the user object
        user = User.objects.get(username=username)
        # Find all group memberships for this user
        memberships = GroupMember.objects.filter(user=user)
        group_ids = [m.group.id for m in memberships]
        if not group_ids:
            return []
        # Get all groups by IDs
        groups = Group.objects.filter(id__in=group_ids)
        return groups
    except Exception as e:
        return []