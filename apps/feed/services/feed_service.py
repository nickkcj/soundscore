from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from apps.feed.services.auth_service import authenticate_with_jwt
from apps.feed.services.album_service import get_top_3_albums
from apps.feed.services.group_service import get_groups_by_user
from apps.feed.services.user_service import get_suggested_users
from django.views.decorators.cache import cache_page
from django.shortcuts import render


@login_required
@require_GET
def load_more_reviews_service(request):
    try:
        page = int(request.GET.get("page", 0))
        page_size = int(request.GET.get("page_size", 5))
        comments_per_review = int(request.GET.get('comments_per_review', 10))
        
        # Calculate offset based on page and page_size
        offset = page * page_size  # Add this line - offset wasn't defined before
        
        # Add sort order parameter
        sort_order = request.GET.get("sort_order", "desc").lower()
        
        # Validate the sort order
        if sort_order not in ["asc", "desc"]:
            sort_order = "desc"
        
        # Get list of IDs to exclude
        exclude_ids = []
        exclude_ids_param = request.GET.get("exclude_ids", "")
        if exclude_ids_param:
            exclude_ids = [int(id) for id in exclude_ids_param.split(',') if id.isdigit()]
        
        print(f"\n[DEBUG] ====== LOAD MORE REVIEWS ======")
        print(f"[DEBUG] Request params: page={page}, page_size={page_size}, offset={offset}, sort_order={sort_order}")
        print(f"[DEBUG] Excluding {len(exclude_ids)} IDs: {exclude_ids}")
        print(f"[DEBUG] Comments per review: {comments_per_review}")
        
        client = authenticate_with_jwt()
        if not client:
            print("[DEBUG] ❌ Supabase connection failed")
            return JsonResponse({"error": "Supabase connection failed"}, status=500)
        
        print(f"[DEBUG] ✓ Supabase connected, calling RPC 'get_feed_reviews'")
        
        # Get total count
        try:
            # Count total reviews
            sql_response = client.rpc('execute_sql', {'sql_query': 'SELECT COUNT(*) FROM soundscore_review'}).execute()
            total_reviews = sql_response.data[0].get('count', 0) if sql_response.data else 0
            print(f"[DEBUG] Total reviews in database: {total_reviews}")
            
            # Count reviews excluding the ones we've seen
            if exclude_ids:
                exclude_list = ','.join(str(id) for id in exclude_ids)
                remaining_query = f"SELECT COUNT(*) FROM soundscore_review WHERE id NOT IN ({exclude_list})"
                remaining_response = client.rpc('execute_sql', {'sql_query': remaining_query}).execute()
                remaining = remaining_response.data[0].get('count', 0) if remaining_response.data else 0
                print(f"[DEBUG] Reviews remaining after excluding {len(exclude_ids)} IDs: {remaining}")
            else:
                remaining = total_reviews
        except Exception as e:
            print(f"[DEBUG] Debug query error: {str(e)}")
            remaining = 0  # Default to 0 if query fails
        
        # Call the RPC with exclude_ids parameter
        response = client.rpc('get_feed_reviews', {
            'p_limit': page_size,
            'p_offset': 0,  # Don't use offset with exclude_ids approach
            'p_exclude_ids': exclude_ids,
            'p_sort_order': sort_order
        }).execute()
        
        print(f"[DEBUG] RPC response data type: {type(response.data)}")
        print(f"[DEBUG] RPC returned {len(response.data) if response.data else 0} reviews")
        
        if not response.data:
            print("[DEBUG] ❌ No reviews returned from RPC")
            return JsonResponse({"reviews": [], "has_more": False}, status=200)
        
        reviews = response.data
        processed_reviews = []
        
        # Process reviews...
        print(f"[DEBUG] Processing {len(reviews)} reviews...")
        for review in reviews:
            review_id = review.get('id')
            
            # Get comment count
            try:
                comment_count_response = client.table('soundscore_comment') \
                    .select('*', count='exact') \
                    .eq('review_id', review_id) \
                    .execute()
                review['comment_count'] = comment_count_response.count if hasattr(comment_count_response, 'count') else 0
                
                # Get comments for display - use comments_per_review instead of hardcoded 2
                comments_response = client.table('soundscore_comment') \
                    .select('*, soundscore_user(username, profile_picture)') \
                    .eq('review_id', review_id) \
                    .order('created_at', desc=True) \
                    .limit(comments_per_review) \
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
        
        # Better has_more calculation
        loaded_count = len(exclude_ids) + len(reviews)
        has_more = loaded_count < total_reviews
        
        print(f"[DEBUG] Loaded so far: {loaded_count}/{total_reviews} reviews, has_more={has_more}")
        print(f"[DEBUG] Returning {len(processed_reviews)} processed reviews")
        return JsonResponse({"reviews": processed_reviews, "has_more": has_more})

    except Exception as e:
        import traceback
        print(f"[DEBUG] Error in load_more_reviews: {str(e)}")
        print(traceback.format_exc())
        # IMPORTANT: Return a JsonResponse in the exception handler
        return JsonResponse({"error": str(e), "reviews": [], "has_more": False}, status=500)
    

@cache_page(60)
@login_required
def get_feed_service(request):
    # Initialize reviews
    reviews = []
    
    client = authenticate_with_jwt()
    if not client:
        return render(request, 'reviews/feed.html', {'error': "Could not connect to Supabase."})
        
    try:
        # Fetch reviews - same as before
        reviews_response = client.table('soundscore_review')\
            .select('*, soundscore_album(*), soundscore_user(*)')\
            .order('created_at', desc=True)\
            .limit(10)  # REDUCED from 20 to 10
            
        # Execute the query
        reviews_response = reviews_response.execute()
        reviews = reviews_response.data or []
        
        # Get all review IDs at once
        review_ids = [review["id"] for review in reviews]
        
        # OPTIMIZATION 1: Batch fetch all comments at once
        if review_ids:
            all_comments = {}
            comments_response = client.table('soundscore_comment')\
                .select('*, soundscore_user(id, username, profile_picture)')\
                .in_('review_id', review_ids)\
                .order('created_at', desc=False)\
                .execute()
                
            # Group comments by review_id
            for comment in comments_response.data or []:
                review_id = comment['review_id']
                if review_id not in all_comments:
                    all_comments[review_id] = []
                all_comments[review_id].append(comment)
        
        # OPTIMIZATION 2: Batch count all likes at once
        all_likes = {}
        if review_ids:
            try:
                likes_count_response = client.table("soundscore_review_like")\
                    .select("review_id", count="exact")\
                    .in_("review_id", review_ids)\
                    .group_by('review_id')\
                    .execute()
                
                if likes_count_response.data:
                    for item in likes_count_response.data:
                        all_likes[item['review_id']] = item['count']
            except:
                # Fallback if group by fails
                for review_id in review_ids:
                    count_query = client.table("soundscore_review_like")\
                        .select("*", count="exact")\
                        .eq("review_id", review_id)\
                        .execute()
                    all_likes[review_id] = count_query.count if hasattr(count_query, 'count') else 0
                
        # OPTIMIZATION 3: If logged in, batch fetch user likes in one query
        user_liked_reviews = set()
        if request.user.is_authenticated and review_ids:
            user_resp = client.table("soundscore_user").select("id").eq("username", request.user.username).limit(1).execute()
            if user_resp.data:
                user_id = user_resp.data[0]["id"]
                user_likes = client.table("soundscore_review_like")\
                    .select("review_id")\
                    .eq("user_id", user_id)\
                    .in_("review_id", review_ids)\
                    .execute()
                
                user_liked_reviews = {like["review_id"] for like in user_likes.data or []}

        top_albums = get_top_3_albums()
        groups = get_groups_by_user(request)
        suggested_users = get_suggested_users(request)


        # Now assign all the data to each review
        for review in reviews:
            review_id = review["id"]
            # Assign comments (limited to 3 most recent)
            review["comments"] = all_comments.get(review_id, [])[:3] 
            review["comment_count"] = len(all_comments.get(review_id, []))
            
            # Assign like count
            review["like_count"] = all_likes.get(review_id, 0)
            
            # Assign liked status
            review["is_liked"] = review_id in user_liked_reviews

        context = {
            'reviews': reviews,
            'top_albums': top_albums,
            'groups': groups,
            'suggested_users': suggested_users,
        }
            
        # Render with optimized data
        return render(request, 'reviews/feed.html', context)
    
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return render(request, 'reviews/feed.html', {'error': f"Error fetching reviews: {str(e)}"})