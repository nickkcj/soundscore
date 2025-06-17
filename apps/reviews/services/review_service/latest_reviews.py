from ..user.supabase_client import authenticate_with_jwt, get_admin_client

def get_latest_reviews(limit=3):
    try:
        client = get_admin_client()
        if not client:
            return {"error": "Could not connect to Supabase"}

        response = client.table('soundscore_review') \
            .select(
                'id, rating, text, created_at, is_favorite, '
                'soundscore_album(id, title, artist, cover_image, spotify_id), '
                'soundscore_user(id, username, profile_picture)'
            ) \
            .order('created_at', desc=True) \
            .limit(limit) \
            .execute()

        if not response.data:
            return {"error": "No reviews found"}

        return response.data

    except Exception as e:
        return {"error": f"Error fetching latest reviews: {str(e)}"}




