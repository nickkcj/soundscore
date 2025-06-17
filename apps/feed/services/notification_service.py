from apps.users.services.supabase_client import authenticate_with_jwt


def create_notification_service(recipient_id, actor_id, notification_type, review_id, message):
    client = authenticate_with_jwt()
    if not client:
        raise Exception("Supabase connection failed")

    response = client.table("soundscore_notification").insert({
        "recipient_id": recipient_id,
        "actor_id": actor_id,
        "type": notification_type,
        "review_id": review_id,
        "message": message,
        "is_read": False
    }).execute()

    return response.data[0] if response.data else None


def get_user_notifications_service(user_id, limit=10, offset=0, unread_only=False):
    client = authenticate_with_jwt()
    if not client:
        raise Exception("Supabase connection failed")

    query = client.table("soundscore_notification").select("*, actor:soundscore_user(username, profile_picture)") \
        .eq("recipient_id", user_id)

    if unread_only:
        query = query.eq("is_read", False)

    query = query.order("created_at", desc=True).range(offset, offset + limit - 1)

    response = query.execute()
    return response.data or []


def mark_notification_as_read_service(notification_id):
    client = authenticate_with_jwt()
    if not client:
        raise Exception("Supabase connection failed")

    client.table("soundscore_notification").update({"is_read": True}).eq("id", notification_id).execute()
    return {"success": True}


def mark_all_as_read_service(user_id):
    client = authenticate_with_jwt()
    if not client:
        raise Exception("Supabase connection failed")

    client.table("soundscore_notification").update({"is_read": True}).eq("recipient_id", user_id).execute()
    return {"success": True}


def get_unread_count_service(user_id):
    client = authenticate_with_jwt()
    if not client:
        raise Exception("Supabase connection failed")

    count_response = client.table("soundscore_notification") \
        .select("*", count="exact") \
        .eq("recipient_id", user_id) \
        .eq("is_read", False) \
        .execute()

    return count_response.count if hasattr(count_response, 'count') else 0
