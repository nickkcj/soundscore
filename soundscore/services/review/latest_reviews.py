from ..user.supabase_client import authenticate_with_jwt, get_admin_client

def get_latest_reviews(limit=3):
    try:
        client = get_admin_client()
        if not client:
            return {"error": "Could not connect to Supabase"}
        
        # Step 1: Get basic reviews
        response = client.table('soundscore_review') \
            .select('*') \
            .order('created_at', desc=True) \
            .limit(limit) \
            .execute()
        
        if hasattr(response, 'error') and response.error:
            return {"error": f"Error fetching reviews: {response.error}"}
        
        reviews = response.data
        
        # Step 2: Enrich with album and user data
        for review in reviews:
            # Get album data
            if review.get('album_id'):
                album_response = client.table('soundscore_album') \
                    .select('*') \
                    .eq('id', review['album_id']) \
                    .limit(1) \
                    .execute()
                if album_response.data:
                    review['soundscore_album'] = album_response.data[0]
            
            # Get user data
            if review.get('user_id'):
                user_response = client.table('soundscore_user') \
                    .select('*') \
                    .eq('id', review['user_id']) \
                    .limit(1) \
                    .execute()
                if user_response.data:
                    review['soundscore_user'] = user_response.data[0]
        
        return reviews
    
    except Exception as e:
        return {"error": f"Error fetching latest reviews: {str(e)}"}


