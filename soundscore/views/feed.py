from django.http import JsonResponse
from django.views.decorators.http import require_POST
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