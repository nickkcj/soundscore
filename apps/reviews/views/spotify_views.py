from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from apps.reviews.services.spotify_service.spotify import search_albums


@login_required
def search_albums_api_view(request):
    """
    API endpoint to search for albums using the Spotify API.
    Query params:
        q (str): Search query (artist name or album).
    Returns:
        JSON response with a list of albums or error.
    """
    query = request.GET.get('q', '')

    # Validate query parameter
    if not query:
        return JsonResponse({"error": "Search query is required"}, status=400)

    # Call the Spotify search service
    albums = search_albums(query)
    return JsonResponse({"albums": albums})
