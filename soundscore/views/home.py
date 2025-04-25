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

    try:
        import google.generativeai as genai
        from decouple import config

        api_key = config("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        gemini_response = model.generate_content("Hello, are you alive?")

        debug_info['gemini_api_response'] = gemini_response.text[:100] if hasattr(gemini_response, 'text') else "No text in response"
    except Exception as e:
        debug_info['gemini_api_response'] = f"Error: {type(e).__name__}: {str(e)}"

    return JsonResponse(debug_info)

