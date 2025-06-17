from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import json

from apps.reviews.services.review_service.add_review import add_review_supabase
from apps.reviews.services.review_service.edit_review import edit_review_supabase
from apps.reviews.services.review_service.delete_review import delete_review_supabase
from apps.users.services.supabase_client import authenticate_with_jwt
from apps.reviews.services.spotify import search_albums


@login_required
def create_review_view(request):
    if request.method == 'POST':
        # POST é pela busca do álbum na criação
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
    data = json.loads(request.body)

    album_id = data.get('album_id')
    rating = data.get('rating')
    text = data.get('review_text', '')
    album_title = data.get('album_title')
    album_artist = data.get('album_artist')
    album_cover = data.get('album_cover')
    is_favorite = data.get('is_favorite', False)

    if not album_id or not rating:
        return JsonResponse({"error": "Album ID and rating are required"}, status=400)

    user = request.user.username

    client = authenticate_with_jwt()
    user_resp = client().table('soundscore_user').select('id').eq('username', user).limit(1).execute()
    if not user_resp.data:
        return JsonResponse({"error": "User not found"}, status=404)
    user_id = user_resp.data[0]['id']

    result = add_review_supabase(
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
    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        text = request.POST.get('review_text', '')
        is_favorite = 'is_favorite' in request.POST

        result = edit_review_supabase(review_id, rating, text, is_favorite)

        if result.get('error'):
            messages.error(request, result['error'])
        else:
            messages.success(request, 'Review updated successfully!')

        return redirect('reviews', username=request.user.username)

    return render(request, 'reviews/edit_review.html', {
        'review_id': review_id,
    })


@login_required
@require_POST
def delete_review_view(request, review_id):
    result = delete_review_supabase(request.user.username, review_id)

    if result.get('error'):
        messages.error(request, result['error'])
    else:
        messages.success(request, "Review deleted successfully!")

    return redirect('reviews', username=request.user.username)
