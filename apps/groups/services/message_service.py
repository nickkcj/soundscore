from apps.users.services.supabase_client import authenticate_with_jwt

def save_message(group_id, user_id, content):
    client = authenticate_with_jwt()
    response = client.table("chat_group_message").insert({
        "group_id": group_id,
        "user_id": user_id,
        "content": content,
    }).execute()
    return response.data[0] if response.data else None

def get_recent_messages(group_id, limit=50):
    client = authenticate_with_jwt()
    messages = client.table("chat_group_message")\
        .select("*, soundscore_user(username,profile_picture)")\
        .eq("group_id", group_id)\
        .order("created_at", desc=True)\
        .limit(limit)\
        .execute().data

    formatted_messages = [{
        "content": msg["content"],
        "username": msg["soundscore_user"]["username"] if "soundscore_user" in msg else "Unknown",
        "user_id": msg["user_id"],
        "profile_picture": msg["soundscore_user"].get("profile_picture", "/static/images/default.jpg")\
            if "soundscore_user" in msg else "/static/images/default.jpg"
    } for msg in messages]

    return formatted_messages
