from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
import json
from ..services.user.supabase_client import authenticate_with_jwt

@login_required
@require_POST
def post_comment(request):
    try:
        data = json.loads(request.body)
        review_id = data.get("review_id")
        text = data.get("text")
        parent_id = data.get("parent_id")

        if not review_id or not text:
            return JsonResponse({"error": "Missing review_id or text"}, status=400)

        client = authenticate_with_jwt()
        if not client:
            return JsonResponse({"error": "Supabase connection failed"}, status=500)

        user_resp = client.table("soundscore_user").select("id").eq("username", request.user.username).limit(1).execute()
        if not user_resp.data:
            return JsonResponse({"error": "User not found"}, status=404)

        user_id = user_resp.data[0]["id"]

        comment_data = {
            "review_id": review_id,
            "user_id": user_id,
            "text": text
        }

        if parent_id:
            comment_data["parent_id"] = parent_id

        response = client.table("soundscore_comment").insert(comment_data).execute()


        return JsonResponse({"success": True, "comment": response.data[0]})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required
@require_POST
def toggle_like(request):
    try:
        data = json.loads(request.body)
        review_id = data.get("review_id")

        if not review_id:
            return JsonResponse({"error": "Missing review_id"}, status=400)

        client = authenticate_with_jwt()
        if not client:
            return JsonResponse({"error": "Supabase connection failed"}, status=500)

        # Get current user
        user_resp = client.table("soundscore_user").select("id").eq("username", request.user.username).limit(1).execute()
        if not user_resp.data:
            return JsonResponse({"error": "User not found"}, status=404)
        
        user_id = user_resp.data[0]["id"]

        # Check if already liked
        like_check = client.table("soundscore_review_like").select("id") \
            .eq("user_id", user_id) \
            .eq("review_id", review_id) \
            .limit(1) \
            .execute()

        if like_check.data:
            # Unlike - delete the like record
            client.table("soundscore_review_like").delete().eq("id", like_check.data[0]["id"]).execute()
            liked = False
        else:
            # Like - add a like record
            client.table("soundscore_review_like").insert({
                "user_id": user_id,
                "review_id": review_id
            }).execute()
            liked = True

        # Get the current count DIRECTLY without using RPC
        count_query = client.table("soundscore_review_like") \
            .select("*", count="exact") \
            .eq("review_id", review_id) \
            .execute()
            
        # The count is in the count attribute of the response
        like_count = count_query.count if hasattr(count_query, 'count') else 0

        return JsonResponse({
            "success": True,
            "liked": liked,
            "count": like_count
        })

    except Exception as e:
        import traceback
        print(f"Error in toggle_like: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=500)
    

@login_required
@require_GET
def load_more_reviews(request):
    try:
        page = int(request.GET.get("page", 0))
        page_size = int(request.GET.get("page_size", 5))
        offset = page * page_size
        
        # Get list of IDs to exclude
        exclude_ids = []
        exclude_ids_param = request.GET.get("exclude_ids", "")
        if exclude_ids_param:
            exclude_ids = [int(id) for id in exclude_ids_param.split(',') if id.isdigit()]
        
        print(f"\n[DEBUG] ====== LOAD MORE REVIEWS ======")
        print(f"[DEBUG] Request params: page={page}, page_size={page_size}, offset={offset}")
        print(f"[DEBUG] Excluding {len(exclude_ids)} review IDs: {exclude_ids[:5]}{'...' if len(exclude_ids) > 5 else ''}")

        client = authenticate_with_jwt()
        if not client:
            print("[DEBUG] ❌ Supabase connection failed")
            return JsonResponse({"error": "Supabase connection failed"}, status=500)
        
        print(f"[DEBUG] ✓ Supabase connected, calling RPC 'get_feed_reviews'")
        
        # Add this debug SQL query
        try:
            # Debug: Check how many total reviews exist
            sql_response = client.rpc('execute_sql', {'sql_query': 'SELECT COUNT(*) FROM soundscore_review'}).execute()
            total_reviews = sql_response.data[0].get('count', 0) if sql_response.data else 0
            print(f"[DEBUG] Total reviews in database: {total_reviews}")
            
            # Debug: Check how many reviews should be available from this offset
            remaining_query = f"SELECT COUNT(*) FROM soundscore_review OFFSET {offset}"
            remaining_response = client.rpc('execute_sql', {'sql_query': remaining_query}).execute()
            remaining = remaining_response.data[0].get('count', 0) if remaining_response.data else 0
            print(f"[DEBUG] Reviews remaining from offset {offset}: {remaining}")
        except Exception as e:
            print(f"[DEBUG] Debug query error: {str(e)}")
        
        # Call the RPC with exclude_ids parameter
        response = client.rpc('get_feed_reviews', {
            'p_limit': page_size,
            'p_offset': offset,
            'p_exclude_ids': exclude_ids
        }).execute()
        
        # Don't access status_code - it doesn't exist
        print(f"[DEBUG] RPC response data type: {type(response.data)}")
        print(f"[DEBUG] RPC returned {len(response.data) if response.data else 0} reviews")
        
        if not response.data:
            print("[DEBUG] ❌ No reviews returned from RPC")
            return JsonResponse({"reviews": [], "has_more": False}, status=200)
        
        reviews = response.data
        processed_reviews = []
        print(f"[DEBUG] Processing {len(reviews)} reviews...")

        # Process each review
        for review in reviews:
            # Add any processing needed
            review_id = review.get('id')
            
            # Get comment count 
            try:
                comment_count_response = client.table('soundscore_comment') \
                    .select('*', count='exact') \
                    .eq('review_id', review_id) \
                    .execute()
                review['comment_count'] = comment_count_response.count if hasattr(comment_count_response, 'count') else 0
                
                # Get a few comments for display
                comments_response = client.table('soundscore_comment') \
                    .select('*, soundscore_user(username, profile_picture)') \
                    .eq('review_id', review_id) \
                    .order('created_at', desc=True) \
                    .limit(2) \
                    .execute()
                review['comments'] = comments_response.data if comments_response.data else []
            except Exception as e:
                print(f"[DEBUG] Error getting comments for review {review_id}: {str(e)}")
                review['comment_count'] = 0
                review['comments'] = []
            
            # Check if liked by current user
            try:
                user_resp = client.table("soundscore_user").select("id").eq("username", request.user.username).limit(1).execute()
                if user_resp.data:
                    user_id = user_resp.data[0]["id"]
                    like_check = client.table("soundscore_review_like") \
                        .select("id") \
                        .eq("user_id", user_id) \
                        .eq("review_id", review_id) \
                        .limit(1) \
                        .execute()
                    review['is_liked'] = bool(like_check.data)
                else:
                    review['is_liked'] = False
            except Exception as e:
                print(f"[DEBUG] Error checking likes for review {review_id}: {str(e)}")
                review['is_liked'] = False
            
            # Add the processed review to our results
            processed_reviews.append(review)

        # Better has_more check
        has_more = len(processed_reviews) > 0 and remaining > 0  

        print(f"[DEBUG] Returning {len(processed_reviews)} reviews with has_more={has_more}")
        return JsonResponse({"reviews": processed_reviews, "has_more": has_more})

    except Exception as e:
        import traceback
        print(f"[DEBUG] ❌ Error in load_more_reviews: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=500)