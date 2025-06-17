from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import json
from apps.feed.services.like_service import toggle_like_service


@login_required
@require_POST
def toggle_like_view(request):
    data = json.loads(request.body)
    review_id = data.get("review_id")

    if not review_id:
        return JsonResponse({"error": "Missing review_id"}, status=400)

    try:
        result = toggle_like_service(review_id, request.user.username)
        return JsonResponse({
            "success": True,
            "liked": result["liked"],
            "count": result["count"]
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
