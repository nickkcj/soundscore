from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import json
from apps.feed.services.comment_service import post_comment_service


@login_required
@require_POST
def post_comment_view(request):
    data = json.loads(request.body)
    review_id = data.get("review_id")
    text = data.get("text")
    parent_id = data.get("parent_id")

    if not review_id or not text:
        return JsonResponse({"error": "Missing review_id or text"}, status=400)

    try:
        comment = post_comment_service(review_id, text, request.user.username, parent_id)
        # Serialize comment for response
        comment_data = {
            "id": comment.id,
            "text": comment.text,
            "user": {
                "id": comment.user.id,
                "username": comment.user.username,
                "profile_picture": comment.user.profile_picture,
            },
            "created_at": comment.created_at,
            "parent_id": comment.parent.id if comment.parent else None,
        }
        return JsonResponse({"success": True, "comment": comment_data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
