from ..user.supabase_client import authenticate_with_jwt

def get_comments_for_review(review_id, limit=3):
    client = authenticate_with_jwt()
    if not client:
        return []

    try:
        response = client.table("soundscore_comment")\
            .select("*")\
            .eq("review_id", review_id)\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()

        if not response.data:
            return []

        comments = response.data
        user_ids = [comment["user_id"] for comment in comments]

        users_response = client.table("soundscore_user")\
            .select("id, username, profile_picture")\
            .in_("id", user_ids)\
            .execute()

        users_dict = {user["id"]: user for user in users_response.data}

        for comment in comments:
            user_id = comment["user_id"]
            comment["soundscore_user"] = users_dict.get(user_id, {
                "username": "Unknown",
                "profile_picture": None
            })

        return comments

    except Exception as e:
        print(f"Error fetching comments: {e}")
        return []