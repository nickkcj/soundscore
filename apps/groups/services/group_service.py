from apps.users.services.supabase_client import authenticate_with_jwt
import uuid

def create_group(name, description, category, privacy, cover_image_file, username):
    client = authenticate_with_jwt()

    user_resp = client.table("soundscore_user").select("id").eq("username", username).limit(1).execute()
    if not user_resp.data:
        raise Exception("User not found")
    user_id = user_resp.data[0]['id']

    if cover_image_file:
        file_ext = cover_image_file.name.split('.')[-1]
        filename = f"group_covers/{uuid.uuid4()}.{file_ext}"
        file_bytes = cover_image_file.read()

        client.storage.from_("chat-media").upload(
            path=filename,
            file=file_bytes,
            file_options={"content-type": cover_image_file.content_type}
        )
        cover_url = client.storage.from_("chat-media").get_public_url(filename)
    else:
        cover_url = "/static/images/default.jpg"

    res = client.table("chat_group").insert({
        "name": name,
        "description": description,
        "category": category,
        "privacy": privacy,
        "cover_image": cover_url
    }).execute()

    group_id = res.data[0]['id']

    client.table("chat_group_member").insert({
        "group_id": group_id,
        "user_id": user_id
    }).execute()

    return group_id

def get_all_groups():
    client = authenticate_with_jwt()

    groups_response = client.table("chat_group").select("*").execute()
    all_groups = groups_response.data or []

    for group in all_groups:
        members_response = client.table("chat_group_member").select("*").eq("group_id", group["id"]).execute()
        group["member_count"] = len(members_response.data)

    trending = sorted(all_groups, key=lambda x: x.get("member_count", 0), reverse=True)[:4]
    return {"groups": all_groups, "trending_groups": trending}

def join_group(group_id, username):
    client = authenticate_with_jwt()

    user_resp = client.table("soundscore_user").select("id").eq("username", username).limit(1).execute()
    if not user_resp.data:
        raise Exception("User not found")
    user_id = user_resp.data[0]['id']

    existing = client.table("chat_group_member").select("*") \
        .eq("group_id", group_id).eq("user_id", user_id).execute()

    if not existing.data:
        client.table("chat_group_member").insert({
            "group_id": group_id,
            "user_id": user_id
        }).execute()

    return True

def get_group_room_data(group_id, username):
    client = authenticate_with_jwt()

    user_resp = client.table("soundscore_user").select("id").eq("username", username).limit(1).execute()
    if not user_resp.data:
        raise Exception("User not found")
    user_id = user_resp.data[0]['id']

    group = client.table("chat_group").select("*").eq("id", group_id).execute().data[0]

    members = client.table("chat_group_member") \
        .select("user_id, soundscore_user(username,profile_picture)") \
        .eq("group_id", group_id).execute().data

    online_rows = client.table("group_user_online") \
        .select("user_id").eq("group_id", group_id).eq("is_online", True).execute().data
    online_ids = {row["user_id"] for row in online_rows}

    member_list = [{
        "user_id": m["user_id"],
        "username": m.get("soundscore_user", {}).get("username", "Unknown"),
        "profile_picture": m.get("soundscore_user", {}).get("profile_picture", "/static/images/default.jpg"),
        "is_online": m["user_id"] in online_ids,
    } for m in members]

    messages = client.table("chat_group_message") \
        .select("*, soundscore_user(username,profile_picture)") \
        .eq("group_id", group_id).execute().data

    formatted_messages = [{
        "content": msg["content"],
        "username": msg["soundscore_user"]["username"] if "soundscore_user" in msg else "Unknown",
        "user_id": msg["user_id"],
        "profile_picture": msg["soundscore_user"].get("profile_picture", "/static/images/default.jpg") \
            if "soundscore_user" in msg else "/static/images/default.jpg"
    } for msg in messages]

    return {
        "group": group,
        "group_id": group_id,
        "member_count": len(member_list),
        "members": member_list,
        "recent_messages": formatted_messages,
        "current_username": username,
    }


def get_groups_by_user(username):
    client = authenticate_with_jwt()

    user_resp = client.table("soundscore_user").select("id").eq("username", username).limit(1).execute()
    if not user_resp.data:
        raise Exception("User not found")
    user_id = user_resp.data[0]['id']

    memberships = client.table("chat_group_member") \
        .select("group_id") \
        .eq("user_id", user_id).execute().data

    group_ids = [m['group_id'] for m in memberships]

    if not group_ids:
        return []

    groups = client.table("chat_group").select("*").in_("id", group_ids).execute().data

    return groups