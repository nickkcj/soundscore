from ..user.supabase_client import authenticate_with_jwt, get_admin_client
import logging

def get_top_3_albums():
    try:
        client = get_admin_client()
        if not client:
            logging.error("Failed to connect to Supabase")
            return {"error": "Could not connect to Supabase"}
        
        # Option 1: Using a PostgreSQL function through Supabase's RPC
        # This approach requires a function defined in your database
        try:
            # First attempt: Direct aggregate query through PostgreSQL
            response = client.table('soundscore_album') \
                .select('id, title, artist, cover_image') \
                .execute()
            
            if not response.data:
                return {"error": "No albums found"}
            
            # Get all album IDs to fetch their reviews
            album_ids = [album['id'] for album in response.data]
            
            # Get all reviews for these albums
            reviews_response = client.table('soundscore_review') \
                .select('album_id, rating') \
                .in_('album_id', album_ids) \
                .execute()
            
            if not reviews_response.data:
                return {"error": "No reviews found"}
            
            # Calculate average ratings
            album_ratings = {}
            album_review_counts = {}
            
            for review in reviews_response.data:
                album_id = review['album_id']
                rating = review['rating']
                
                if album_id not in album_ratings:
                    album_ratings[album_id] = 0
                    album_review_counts[album_id] = 0
                    
                album_ratings[album_id] += rating
                album_review_counts[album_id] += 1
            
            # Calculate averages
            for album_id in album_ratings:
                album_ratings[album_id] = album_ratings[album_id] / album_review_counts[album_id]
            
            # Sort albums by average rating
            albums_with_ratings = []
            for album in response.data:
                album_id = album['id']
                if album_id in album_ratings:
                    # Calculate both the exact average and a rounded version for stars
                    exact_avg = album_ratings[album_id]
                    albums_with_ratings.append({
                        **album,
                        'avg_rating': exact_avg,
                        'avg_rating_rounded': round(exact_avg),  # For full stars
                        'review_count': album_review_counts[album_id]
                    })
            
            # Sort by average rating (descending)
            albums_with_ratings.sort(key=lambda x: x['avg_rating'], reverse=True)
            
            # Return top 3
            return albums_with_ratings[:3]
            
        except Exception as e:
            logging.error(f"Error calculating top albums: {str(e)}")
            return {"error": f"Error calculating top albums: {str(e)}"}
            
    except Exception as e:
        logging.error(f"Error getting top albums: {str(e)}")
        return {"error": f"Error getting top albums: {str(e)}"}
