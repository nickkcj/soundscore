from apps.users.services.supabase_client import authenticate_with_jwt
from datetime import datetime

def edit_review_supabase(review_id, rating, text=None, is_favorite=False):

   client = authenticate_with_jwt()
   if not client:
       return {"error": "Failed to authenticate with Supabase"}
   
   try:
       if not 1 <= rating <= 5:
           return {"error": "Rating must be between 1 and 5"}
       
       update_data = {
              'rating': rating,
              'text': text or "",
              'is_favorite': is_favorite,
              'updated_at': datetime.now().isoformat()
       }

       update_response = client.table('soundscore_review')\
            .update(update_data)\
            .eq('id', review_id)\
            .execute()
       
       if not update_response.data:
           return {"error": "Failed to update review"}
       
       return {
           "success": True,
           "message": "Review updated successfully",
           "review": update_response.data[0]
       }
   
   except Exception as e:
         print(f"Error updating review: {e}")
         return {"error": str(e)}