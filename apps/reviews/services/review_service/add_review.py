from ..user.supabase_client import authenticate_with_jwt
from datetime import datetime

def add_review_supabase(user_id, album_id, rating, album_title=None, album_artist=None, 
                       album_cover=None, text=None, is_favorite=False):
    # Use authenticated client instead of anonymous client
    client = authenticate_with_jwt()
    if not client:
        return {"error": "Failed to authenticate with Supabase"}
    
    try:
        # Step 1: Check if album exists
        album_response = client.table('soundscore_album').select('*').eq('spotify_id', album_id).execute()
        
        # Step 2: Create album if it doesn't exist
        if not album_response.data:
            if not album_title or not album_artist:
                return {"error": "Album title and artist are required to create a new album"}
                
            album_data = {
                'spotify_id': album_id,
                'title': album_title,
                'artist': album_artist,
                'cover_image': album_cover,
            }
            
            album_insert = client.table('soundscore_album').insert(album_data).execute()
            if not album_insert.data:
                return {"error": "Failed to create album record"}
                
            album_record = album_insert.data[0]
            db_album_id = album_record.get('id')
        else:
            # Album exists, get its ID
            db_album_id = album_response.data[0].get('id')
        
        # Step 3: Check if user has already reviewed this album
        existing_review = client.table('soundscore_review').select('*')\
            .eq('user_id', user_id).eq('album_id', db_album_id).execute()
        
        if existing_review.data:
            # Update existing review
            review_update = client.table('soundscore_review')\
                .update({
                    'rating': rating,
                    'text': text or "",
                    'is_favorite': is_favorite,
                    'updated_at': datetime.now().isoformat()
                })\
                .eq('id', existing_review.data[0].get('id'))\
                .execute()
                
            if review_update.data:
                return {
                    "success": True,
                    "message": "Review updated successfully",
                    "review": review_update.data[0]
                }
            else:
                return {"error": "Failed to update review"}
        
        # Step 4: Create new review
        review_data = {
            'user_id': user_id,
            'album_id': db_album_id,
            'rating': rating,
            'text': text or "",
            'is_favorite': is_favorite,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        review_insert = client.table('soundscore_review').insert(review_data).execute()
        
        if review_insert.data:
            return {
                "success": True,
                "message": "Review added successfully",
                "review": review_insert.data[0]
            }
        else:
            return {"error": "Failed to add review"}
            
    except Exception as e:
        return {"error": str(e)}