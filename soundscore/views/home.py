from django.shortcuts import render
from ..services.review.latest_reviews import get_latest_reviews
from ..services.review.top_albums import get_top_3_albums
from django.views.decorators.http import require_GET

def home(request):
    latest_reviews = get_latest_reviews(limit=3)
    top_albums = get_top_3_albums()

    print(latest_reviews)

    if isinstance(latest_reviews, dict) and "error" in latest_reviews:
        latest_reviews = []
    if isinstance(top_albums, dict) and "error" in top_albums:
        top_albums = []

    print(latest_reviews, top_albums)

    context = {
        'latest_reviews': latest_reviews,
        'top_albums': top_albums
    }
    return render(request, 'home/home.html', context)

def about(request):
    return render(request, 'home/about.html')


from django.http import JsonResponse
import requests

@require_GET
def debug_check(request):
    debug_info = {}

    # Test 1 - Outbound internet access (basic)
    try:
        r = requests.get("https://www.google.com", timeout=5)
        debug_info['google_status'] = r.status_code
    except Exception as e:
        debug_info['google_status'] = f"Failed: {str(e)}"

    # Test 2 - Gemini API access
    try:
        r = requests.get("https://generativelanguage.googleapis.com", timeout=5)
        debug_info['gemini_status'] = r.status_code
    except Exception as e:
        debug_info['gemini_status'] = f"Failed: {str(e)}"

    # Test 3 - Check installed google-generativeai version
    try:
        import google.generativeai as genai
        debug_info['generativeai_version'] = getattr(genai, '__version__', 'Unknown')
    except Exception as e:
        debug_info['generativeai_version'] = f"Failed: {str(e)}"

    return JsonResponse(debug_info)
