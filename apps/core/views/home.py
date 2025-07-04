from django.shortcuts import render
from apps.reviews.services.review_service.latest_reviews import get_latest_reviews
from apps.reviews.services.review_service.top_albums import get_top_3_albums
from django.views.decorators.http import require_GET
from django.http import JsonResponse
import requests

def home(request):
    """Render the Home page with latest reviews and top albums."""

    # Fetch latest reviews and top albums
    latest_reviews = get_latest_reviews(limit=3)
    top_albums = get_top_3_albums()

    # Handle cases where the services return an error
    if isinstance(latest_reviews, dict) and "error" in latest_reviews:
        latest_reviews = []
    if isinstance(top_albums, dict) and "error" in top_albums:
        top_albums = []


    # Organize the context being passed to the html
    context = {
        'latest_reviews': latest_reviews,
        'top_albums': top_albums
    }
    return render(request, 'core/home.html', context)
