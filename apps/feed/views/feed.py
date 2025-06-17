from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.http import JsonResponse
from apps.feed.services.feed_service import load_more_reviews_service
from django.views.decorators.cache import cache_page
from django.shortcuts import render
from apps.feed.services.feed_service import get_feed_service


@login_required
@require_GET
def load_more_reviews_view(request):
    try:
        page = int(request.GET.get("page", 0))
        page_size = int(request.GET.get("page_size", 5))
        comments_per_review = int(request.GET.get('comments_per_review', 10))
        sort_order = request.GET.get("sort_order", "desc").lower()
        exclude_ids_param = request.GET.get("exclude_ids", "")
        exclude_ids = [int(i) for i in exclude_ids_param.split(',') if i.isdigit()] if exclude_ids_param else []

        result = load_more_reviews_service(
            username=request.user.username,
            page=page,
            page_size=page_size,
            comments_per_review=comments_per_review,
            sort_order=sort_order,
            exclude_ids=exclude_ids
        )

        return JsonResponse(result)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    

@cache_page(60)
@login_required
def feed_view(request):
    try:
        result = get_feed_service(request.user.username)
        return render(request, 'reviews/feed.html', result)
    except Exception as e:
        return render(request, 'reviews/feed.html', {'error': str(e)})
