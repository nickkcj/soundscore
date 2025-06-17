from apps.users.services.supabase_client import authenticate_with_jwt


def post_comment_service(review_id, text, username, parent_id=None):
    client = authenticate_with_jwt()
    if not client:
        raise Exception("Supabase connection failed")

    user_resp = client.table("soundscore_user").select("id") \
        .eq("username", username).limit(1).execute()
    if not user_resp.data:
        raise Exception("User not found")

    user_id = user_resp.data[0]["id"]
    comment_data = {
        "review_id": review_id,
        "user_id": user_id,
        "text": text
    }
    if parent_id:
        comment_data["parent_id"] = parent_id

    response = client.table("soundscore_comment").insert(comment_data).execute()
    return response.data[0]
