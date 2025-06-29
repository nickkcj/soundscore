from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.http import JsonResponse
from apps.feed.services.feed_service import load_more_reviews_service, get_feed_service
from django.views.decorators.cache import cache_page
from django.shortcuts import render


@login_required
@require_GET
def load_more_reviews_view(request):
    try:
        return load_more_reviews_service(request)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    

@cache_page(60)
@login_required
def feed_view(request):
    try:
        return get_feed_service(request)
    except Exception as e:
        return render(request, 'feed/feed.html', {'error': str(e)})
