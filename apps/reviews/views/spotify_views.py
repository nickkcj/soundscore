from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from apps.reviews.services.spotify_service.spotify import search_albums


@login_required
def search_albums_api_view(request):
    query = request.GET.get('q', '')

    if not query:
        return JsonResponse({"error": "Search query is required"}, status=400)

    albums = search_albums(query)
    return JsonResponse({"albums": albums})
