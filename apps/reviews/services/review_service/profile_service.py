from apps.users.services.supabase_client import authenticate_with_jwt

def get_user_profile_data(username):
    """
    Get user profile data including review count and average rating.
    """
    client = authenticate_with_jwt()
    if not client:
        return {
            'reviews_count': 0,
            'avg_rating': 0,
            'profile_picture_url': '/static/images/default.jpg'
        }

    try:
        # Get user data
        user_response = client.table('soundscore_user').select('id, profile_picture').eq('username', username).limit(1).execute()
        if not user_response.data:
            return {
                'reviews_count': 0,
                'avg_rating': 0,
                'profile_picture_url': '/static/images/default.jpg'
            }

        user_id = user_response.data[0]['id']
        profile_picture = user_response.data[0].get('profile_picture', '/static/images/default.jpg')

        # Get review stats
        reviews_response = client.table('soundscore_review').select('rating').eq('user_id', user_id).execute()
        reviews = reviews_response.data if reviews_response.data else []
        
        reviews_count = len(reviews)
        avg_rating = sum(review['rating'] for review in reviews) / reviews_count if reviews_count > 0 else 0

        return {
            'reviews_count': reviews_count,
            'avg_rating': round(avg_rating, 1),
            'profile_picture_url': profile_picture
        }

    except Exception as e:
        print(f"Error getting user profile data: {e}")
        return {
            'reviews_count': 0,
            'avg_rating': 0,
            'profile_picture_url': '/static/images/default.jpg'
        } 