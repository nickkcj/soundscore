from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.reviews.services.review_service.latest_reviews import get_latest_reviews
from apps.reviews.services.review_service.top_albums import get_top_3_albums
from apps.reviews.services.spotify_service.spotify import search_albums
from apps.reviews.services.review_service.profile_service import get_user_profile_data


def discover_view(request):
    query = request.GET.get('q', '')
    if query:
        albums = search_albums(query)
    else:
        albums = []

    return render(request, 'reviews/discover.html', {
        'query': query,
        'albums': albums,
    })


@login_required
def user_profile_view(request, username):
    data = get_user_profile_data(username)
    return render(request, 'reviews/user_profile.html', data)
