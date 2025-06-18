from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from apps.reviews.services.review_service import (
    get_review_by_id,
    get_reviews_by_user,
    get_reviews_by_album,
    get_all_reviews
)

@require_http_methods(["GET"])
def review_list(request):
    """Get all reviews."""
    reviews = get_all_reviews()
    return JsonResponse({"reviews": reviews})

@require_http_methods(["GET"])
def review_detail(request, pk):
    """Get a specific review by ID."""
    review = get_review_by_id(pk)
    if review:
        return JsonResponse(review)
    return JsonResponse({"error": "Review not found"}, status=404)

@require_http_methods(["GET"])
def user_reviews(request, username):
    """Get all reviews by a specific user."""
    reviews = get_reviews_by_user(username)
    return JsonResponse({"reviews": reviews})

@require_http_methods(["GET"])
def album_reviews(request, album_id):
    """Get all reviews for a specific album."""
    reviews = get_reviews_by_album(album_id)
    return JsonResponse({"reviews": reviews}) 