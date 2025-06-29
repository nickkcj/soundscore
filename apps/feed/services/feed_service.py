from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.views.decorators.cache import cache_page
from django.shortcuts import render

from apps.reviews.models import Review
from apps.reviews.models import Comment, ReviewLike
from apps.users.models import User
from apps.reviews.services.review_service.top_albums import get_top_3_albums
from apps.groups.services.group_service import get_groups_by_user
from apps.users.services.retrieve_users import get_suggested_users


@login_required
@require_GET
def load_more_reviews_service(request):
    try:
        page = int(request.GET.get("page", 0))
        page_size = int(request.GET.get("page_size", 5))
        comments_per_review = int(request.GET.get('comments_per_review', 10))
        sort_order = request.GET.get("sort_order", "desc").lower()
        if sort_order not in ["asc", "desc"]:
            sort_order = "desc"
        exclude_ids_param = request.GET.get("exclude_ids", "")
        exclude_ids = [int(id) for id in exclude_ids_param.split(',') if id.isdigit()] if exclude_ids_param else []

        reviews_qs = Review.objects.exclude(id__in=exclude_ids)
        if sort_order == "desc":
            reviews_qs = reviews_qs.order_by('-created_at')
        else:
            reviews_qs = reviews_qs.order_by('created_at')
        reviews = reviews_qs[:page_size]

        processed_reviews = []
        for review in reviews:
            comment_qs = Comment.objects.filter(review=review).order_by('-created_at')[:comments_per_review]
            comment_count = Comment.objects.filter(review=review).count()
            is_liked = ReviewLike.objects.filter(review=review, user=request.user).exists()
            processed_reviews.append({
                "id": review.id,
                "user": {
                    "id": review.user.id,
                    "username": review.user.username,
                    "profile_picture": review.user.profile_picture,
                },
                "album": {
                    "id": review.album.id,
                    "title": review.album.title,
                    "artist": review.album.artist,
                    "cover_image": review.album.cover_image,
                },
                "rating": review.rating,
                "text": review.text,
                "created_at": review.created_at,
                "is_favorite": review.is_favorite,
                "comments": [
                    {
                        "id": c.id,
                        "text": c.text,
                        "user": {
                            "id": c.user.id,
                            "username": c.user.username,
                            "profile_picture": c.user.profile_picture,
                        },
                        "created_at": c.created_at,
                    } for c in comment_qs
                ],
                "comment_count": comment_count,
                "is_liked": is_liked,
                "like_count": ReviewLike.objects.filter(review=review).count(),
            })

        total_reviews = Review.objects.count()
        loaded_count = len(exclude_ids) + len(reviews)
        has_more = loaded_count < total_reviews

        return JsonResponse({"reviews": processed_reviews, "has_more": has_more})

    except Exception as e:
        import traceback
        print(f"[DEBUG] Error in load_more_reviews: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({"error": str(e), "reviews": [], "has_more": False}, status=500)


@cache_page(60)
@login_required
def get_feed_service(request):
    reviews = Review.objects.select_related('album', 'user').order_by('-created_at')[:10]
    review_ids = [r.id for r in reviews]
    comments = Comment.objects.filter(review_id__in=review_ids).select_related('user').order_by('created_at')
    likes = ReviewLike.objects.filter(review_id__in=review_ids)
    user_likes = set(l.review_id for l in likes if l.user_id == request.user.id)

    top_albums = get_top_3_albums()
    groups = get_groups_by_user(request.user.username)
    suggested_users = get_suggested_users(request)

    # Group comments by review
    comment_map = {}
    for c in comments:
        comment_map.setdefault(c.review_id, []).append(c)

    # Group likes by review
    like_map = {}
    for l in likes:
        like_map.setdefault(l.review_id, []).append(l)

    review_data = []
    for review in reviews:
        review_data.append({
            "id": review.id,
            "soundscore_user": {  # Changed from "user" to "soundscore_user"
                "id": review.user.id,
                "username": review.user.username,
                "profile_picture": review.user.profile_picture.url if review.user.profile_picture else '/media/profile_pictures/default.jpg',
            },
            "soundscore_album": {  # Also standardizing the album key
                "id": review.album.id,
                "title": review.album.title,
                "artist": review.album.artist,
                "cover_image": review.album.cover_image,
            },
            "rating": review.rating,
            "text": review.text,
            "created_at": review.created_at,
            "is_favorite": review.is_favorite,
            "comments": [
                {
                    "id": c.id,
                    "text": c.text,
                    "user": {
                        "id": c.user.id,
                        "username": c.user.username,
                        "profile_picture": c.user.profile_picture,
                    },
                    "created_at": c.created_at,
                } for c in comment_map.get(review.id, [])[:3]
            ],
            "comment_count": len(comment_map.get(review.id, [])),
            "is_liked": review.id in user_likes,
            "like_count": len(like_map.get(review.id, [])),
        })

    context = {
        'reviews': review_data,
        'top_albums': top_albums,
        'groups': groups,
        'suggested_users': suggested_users,
    }
    return render(request, 'feed/feed.html', context)