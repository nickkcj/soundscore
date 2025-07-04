from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import json
from django.shortcuts import get_object_or_404
from apps.reviews.models import Review, Album
from django.db.models import Avg
from apps.users.models import User
from apps.reviews.services.review_service.profile_service import get_user_profile_data
from apps.reviews.services.review_service.add_review import add_review
from apps.reviews.services.review_service.edit_review import edit_review
from apps.reviews.services.review_service.delete_review import delete_review
from apps.reviews.services.spotify_service.spotify import search_albums, get_album_info, get_album_tracks


@login_required
def create_review_view(request):
    """
    Render the review creation page and handle album search.
    On POST: searches for albums by artist name.
    On GET: renders the empty form.
    """
    if request.method == 'POST':
        # Handle album search
        query = request.POST.get('artist_name', '').strip()
        search_results = []
        if query:
            search_results = search_albums(query)

        return render(request, 'reviews/create_review.html', {
            'search_results': search_results,
            'query': query,
        })

    return render(request, 'reviews/create_review.html')


@login_required
@require_POST
def create_review_api_view(request):
    """
    API endpoint to create a new review via AJAX.
    Expects JSON body with album and review data.
    Returns success or error as JSON.
    """
    data = json.loads(request.body)

    album_id = data.get('album_id')
    rating = data.get('rating')
    text = data.get('review_text', '')
    album_title = data.get('album_title')
    album_artist = data.get('album_artist')
    album_cover = data.get('album_cover')
    is_favorite = data.get('is_favorite', False)

    # Validate required fields
    if not album_id or not rating:
        return JsonResponse({"error": "Album ID and rating are required"}, status=400)

    user_id = request.user.id

    # Call service to add review
    result = add_review(
        user_id=user_id,
        album_id=album_id,
        rating=int(rating),
        album_title=album_title,
        album_artist=album_artist,
        album_cover=album_cover,
        text=text,
        is_favorite=is_favorite
    )

    if "error" in result:
        return JsonResponse({"error": result["error"]}, status=400)

    return JsonResponse({
        "success": True,
        "message": "Review saved successfully",
        "review_id": result.get("review", {}).get("id")
    })


@login_required
def edit_review_view(request, review_id):
    """
    Render the edit review page and handle review updates.
    Only the review owner can edit.
    """
    review = get_object_or_404(Review, id=review_id)

    # Permission check
    if review.user.username != request.user.username:
        return HttpResponseForbidden("You do not have permission to edit this review.")
    
    if request.method == 'POST':
        # Handle review update
        rating = int(request.POST.get('rating'))
        text = request.POST.get('review_text', '')
        is_favorite = 'is_favorite' in request.POST

        result = edit_review(review_id, rating, text, is_favorite)

        if result.get('error'):
            messages.error(request, result['error'])
        else:
            messages.success(request, 'Review updated successfully!')

        return redirect('reviews', username=request.user.username)

    return render(request, 'reviews/edit_review.html', {
        'review': review,
    })


@login_required
@require_POST
def delete_review_view(request, review_id):
    """
    Delete a review (POST only).
    Only the review owner can delete.
    """
    result = delete_review(request.user.username, review_id)

    if result.get('error'):
        messages.error(request, result['error'])
    else:
        messages.success(request, "Review deleted successfully!")

    return redirect('reviews', username=request.user.username)


@login_required
def user_profile_view(request, username):
    """
    Render a user's profile page with their reviews and favorite albums.
    """
    # Get user or 404
    user = get_object_or_404(User, username=username)
    # Get profile data (review count, avg rating, profile pic)
    profile_data = get_user_profile_data(username)
    # Get all reviews for this user
    all_reviews = (
        Review.objects
        .filter(user=user)
        .select_related('album')
        .order_by('-created_at')
    )
    # Favorite albums: reviews marked as favorite
    favorite_reviews = all_reviews.filter(is_favorite=True)
    # Prepare favorite albums data
    favorite_albums = [
        {
            "rating": review.rating,
            "soundscore_album": review.album,
        }
        for review in favorite_reviews
    ]
    # Prepare all reviews data
    all_reviews_data = [
        {
            "id": review.id,
            "rating": review.rating,
            "text": review.text,
            "created_at": review.created_at,
            "soundscore_album": review.album,
        }
        for review in all_reviews
    ]
    context = {
        "profile_user": {
            "username": user.username,
            "profile_picture_url": profile_data.get("profile_picture_url", '/media/profile_pictures/default.jpg'),
        },
        "total_reviews": profile_data.get("review_count", 0),
        "average_rating": profile_data.get("avg_rating", 0),
        "favorite_albums": favorite_albums,
        "all_reviews": all_reviews_data,
    }
    return render(request, "reviews/reviews.html", context)


def album_detail_view(request, spotify_id):
    """
    Render the album detail page, including album info, tracks, and reviews.
    """
    # Get album info and tracks from Spotify
    album_data = get_album_info(spotify_id)
    tracks = get_album_tracks(spotify_id)

    album = {
        "title": album_data.get("name"),
        "artist": ", ".join(album_data.get("artists", [])),
        "cover_image": album_data.get("images")[0] if album_data.get("images") else "/static/images/default_album.png",
        "release_date": album_data.get("release_date"),
        "genres": album_data.get("genres", []),
        "spotify_url": album_data.get("external_urls"),
        "album_type": album_data.get("album_type"),
        "total_tracks": album_data.get("total_tracks"),
    }

    # Try to find the album in the local DB for reviews
    album_obj = Album.objects.filter(spotify_id=spotify_id).first()
    reviews_data = []
    avg_rating = None
    if album_obj:
        db_reviews = Review.objects.filter(album=album_obj).select_related('user').order_by('-created_at')
        
        # Process each review to include profile picture URL
        for review in db_reviews:
            # Get profile data for the reviewer
            profile_data = get_user_profile_data(review.user.username)
            # Create an enriched review object
            reviews_data.append({
                'id': review.id,
                'user': review.user,
                'rating': review.rating,
                'text': review.text,
                'created_at': review.created_at,
                'profile_picture_url': profile_data.get('profile_picture_url', '/media/profile_pictures/default.jpg')
            })
            
        # Calculate average rating for the album
        avg_rating = db_reviews.aggregate(avg=Avg('rating'))['avg']
        if avg_rating is not None:
            avg_rating = round(avg_rating, 1)

    context = {
        'album': album,
        'tracks': tracks,
        'reviews': reviews_data,  # Use the enriched reviews data
        'avg_rating': avg_rating,
    }
    return render(request, 'reviews/album_detail.html', context)
