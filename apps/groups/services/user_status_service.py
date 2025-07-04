from apps.users.models import User
# from apps.groups.models import GroupUserOnline  # Only if you have this model
from apps.groups.models import Group
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def set_online_status(username, group_id, is_online):
    """
    Set the online status of a user in a group and notify via channels.
    Parameters:
        username (str): Username of the user
        group_id (int): ID of the group
        is_online (bool): True if online, False if offline
    Raises:
        Exception: If user or group not found or error occurs
    """
    try:
        # Get user and group objects
        user = User.objects.get(username=username)
        group = Group.objects.get(id=group_id)
        # Optionally update a GroupUserOnline model if you have one
        # obj, _ = GroupUserOnline.objects.update_or_create(
        #     group=group, user=user,
        #     defaults={'is_online': is_online}
        # )
        # Notify all group members via Django Channels
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"group_{group_id}",
            {"type": "trigger_broadcast_online_users"}
        )
    except Exception as e:
        raise Exception(f"Error setting online status: {e}")

