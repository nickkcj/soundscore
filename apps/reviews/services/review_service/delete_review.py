from apps.users.services.supabase_client import authenticate_with_jwt

def delete_review_supabase(user, review_id):
    client = authenticate_with_jwt()
    if not client:
        return {"error": "Failed to authenticate with Supabase"}
    
    user_id = client.table('soundscore_user').select('id').eq('username', user).execute()

    supabase_user_id = user_id.data[0]['id']
    review_response = client.table('soundscore_review').select('*').eq('user_id', supabase_user_id).eq('id', review_id).execute()
    print(review_response)

    if not review_response.data:
        return {"error": "Review not found"}
    

    review_delete = client.table('soundscore_review').delete().eq('id', review_response.data[0].get('id')).execute()

    if not review_delete.data:
        return {"error": "Failed to delete review"}

    return {
        "success": True,
        "message": "Review deleted successfully"
    }