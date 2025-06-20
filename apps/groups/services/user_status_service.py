from apps.users.models import User
# from apps.groups.models import GroupUserOnline  # Only if you have this model
from apps.groups.models import Group
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def set_online_status(username, group_id, is_online):
    try:
        user = User.objects.get(username=username)
        group = Group.objects.get(id=group_id)
        # Implement GroupUserOnline if you want online tracking
        # obj, _ = GroupUserOnline.objects.update_or_create(
        #     group=group, user=user,
        #     defaults={'is_online': is_online}
        # )
        # Notify via channels
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"group_{group_id}",
            {"type": "trigger_broadcast_online_users"}
        )
    except Exception as e:
        raise Exception(f"Error setting online status: {e}")

