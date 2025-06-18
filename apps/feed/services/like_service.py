from apps.users.services.supabase_client import authenticate_with_jwt
from apps.feed.services.notification_service import create_notification_service


def toggle_like_service(review_id, username):
    client = authenticate_with_jwt()
    if not client:
        raise Exception("Supabase connection failed")

    user_resp = client.table("soundscore_user").select("id").eq("username", username).limit(1).execute()
    if not user_resp.data:
        raise Exception("User not found")
    user_id = user_resp.data[0]["id"]

    like_check = client.table("soundscore_review_like").select("id") \
        .eq("user_id", user_id).eq("review_id", review_id).limit(1).execute()

    if like_check.data:
        client.table("soundscore_review_like").delete().eq("id", like_check.data[0]["id"]).execute()
        liked = False
    else:
        client.table("soundscore_review_like").insert({
            "user_id": user_id,
            "review_id": review_id
        }).execute()
        liked = True

    count_query = client.table("soundscore_review_like") \
        .select("*", count="exact").eq("review_id", review_id).execute()

    like_count = count_query.count if hasattr(count_query, 'count') else 0

    if liked:
        author_resp = client.table('soundscore_review').select('user_id').eq('id', review_id).limit(1).execute()
        if author_resp.data and author_resp.data[0]['user_id'] != user_id:
            author_id = author_resp.data[0]['user_id']
            username_resp = client.table('soundscore_user').select('username').eq('id', user_id).limit(1).execute()
            username = username_resp.data[0]['username'] if username_resp.data else "Someone"

            message = f"@{username} liked your review!"
            create_notification_service(
                recipient_id=author_id,
                actor_id=user_id,
                notification_type='like',
                review_id=review_id,
                message=message
            )

    return {"liked": liked, "count": like_count}
