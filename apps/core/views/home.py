from django.shortcuts import render
from ..services.review.latest_reviews import get_latest_reviews
from ..services.review.top_albums import get_top_3_albums
from django.views.decorators.http import require_GET
from django.http import JsonResponse
import requests

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
