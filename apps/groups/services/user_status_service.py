from apps.users.services.supabase_client import authenticate_with_jwt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def set_online_status(username, group_id, is_online):
    client = authenticate_with_jwt()

    user_resp = client.table("soundscore_user").select("id") \
        .eq("username", username).limit(1).execute()
    if not user_resp.data:
        raise Exception("User not found")

    user_id = user_resp.data[0]['id']

    client.rpc("upsert_group_user_online", {
        "_group_id": group_id,
        "_user_id": user_id,
        "_is_online": is_online
    }).execute()

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"group_{group_id}",
        {"type": "trigger_broadcast_online_users"}
    )

