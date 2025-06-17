from .supabase_client import authenticate_with_jwt

def get_suggested_users(request, limit=3):
    """Get users with the most reviews"""
    client = authenticate_with_jwt()
    if not client:
        return []
    
    # Get current user to exclude
    current_username = request.user.username if request.user.is_authenticated else None
    
    try:
        # Query to get users with most reviews
        response = client.table('soundscore_user') \
            .select('id, username, profile_picture') \
            .not_.eq('username', current_username or '') \
            .execute()
            
        if not response.data:
            return []
            
        # Get review counts for each user
        suggested_users = []
        for user in response.data:
            review_count_response = client.table('soundscore_review') \
                .select('id') \
                .eq('user_id', user['id']) \
                .execute()
                
            review_count = len(review_count_response.data) if review_count_response.data else 0
            
            suggested_users.append({
                'username': user['username'],
                'profile_picture': user['profile_picture'] or '/static/images/default.jpg',
                'review_count': review_count
            })
        
        # Sort by review count and limit
        suggested_users.sort(key=lambda x: x['review_count'], reverse=True)
        return suggested_users[:limit]
        
    except Exception as e:
        print(f"Error getting suggested users: {e}")
        return []