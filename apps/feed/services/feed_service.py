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
from apps.users.models import UserRelationship


@login_required
@require_GET
def load_more_reviews_service(request):
    """Load more reviews with pagination, sorting, and user-specific data, 
    when load more button is clicked in feed page."""

    try:
        # Get pagination and filtering parameters from the request
        page = int(request.GET.get("page", 0))
        page_size = int(request.GET.get("page_size", 5))
        comments_per_review = int(request.GET.get('comments_per_review', 10))
        sort_order = request.GET.get("sort_order", "desc").lower()

        # Validate sort order - default to "desc" if invalid
        if sort_order not in ["asc", "desc"]:
            sort_order = "desc"

        # Parse exclude_ids to avoid loading duplicate reviews
        # This allows the frontend to exclude certain reviews from the results
        exclude_ids_param = request.GET.get("exclude_ids", "")
        exclude_ids = [int(id) for id in exclude_ids_param.split(',') if id.isdigit()] if exclude_ids_param else []

        # Build the query to get reviews excluding already loaded ones
        reviews_qs = Review.objects.exclude(id__in=exclude_ids)
        
        # Apply sorting based on creation date
        if sort_order == "desc":
            reviews_qs = reviews_qs.order_by('-created_at')
        else:
            reviews_qs = reviews_qs.order_by('created_at')
        
        # Limit to requested page size
        reviews = reviews_qs[:page_size]

        # Process each review with its comments, likes, and user data
        processed_reviews = []
        for review in reviews:
            # Get limited comments for this review
            comment_qs = Comment.objects.filter(review=review).order_by('-created_at')[:comments_per_review]
            
            # Get total comment count for this review
            comment_count = Comment.objects.filter(review=review).count()
            
            # Check if the current user has liked this specific review
            is_liked = ReviewLike.objects.filter(review=review, user=request.user).exists()
            
            # Get total like count for this review
            like_count = ReviewLike.objects.filter(review=review).count()
            
            # Build the review data structure with all related information
            processed_reviews.append({
                "id": review.id,
                "soundscore_user": {  # User who created the review
                    "id": review.user.id,
                    "username": review.user.username,
                    "profile_picture": review.user.profile_picture.url if review.user.profile_picture else '/media/profile_pictures/default.jpg',
                },
                "soundscore_album": {  # Album being reviewed
                    "id": review.album.id,
                    "title": review.album.title,
                    "artist": review.album.artist,
                    "cover_image": review.album.cover_image,
                },
                "rating": review.rating,
                "text": review.text,
                "created_at": review.created_at,
                "is_favorite": review.is_favorite,
                "comments": [  # Recent comments on this review
                    {
                        "id": c.id,
                        "text": c.text,
                        "user": {
                            "id": c.user.id,
                            "username": c.user.username,
                            "profile_picture": c.user.profile_picture.url if c.user.profile_picture else '/media/profile_pictures/default.jpg',
                        },
                        "created_at": c.created_at,
                    } for c in comment_qs
                ],
                "comment_count": comment_count,
                "is_liked": is_liked,  # Whether current user liked this review
                "like_count": like_count,
            })

        # Calculate pagination metadata
        total_reviews = Review.objects.count()
        loaded_count = len(exclude_ids) + len(reviews)
        has_more = loaded_count < total_reviews

        # Return the processed data as JSON
        return JsonResponse({"reviews": processed_reviews, "has_more": has_more})

    except Exception as e:
        # Log error details for debugging
        import traceback
        print(f"[DEBUG] Error in load_more_reviews: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({"error": str(e), "reviews": [], "has_more": False}, status=500)


@cache_page(60)  # Cache for 60 seconds to improve performance
@login_required
def get_feed_service(request):
    """Get the main feed data including reviews, comments, likes, top albums, 
    user groups, and suggested users for the authenticated user's feed page."""
    
    # Get the latest 10 reviews with related album and user data
    reviews = Review.objects.select_related('album', 'user').order_by('-created_at')[:10]
    review_ids = [r.id for r in reviews]
    
    # Fetch all comments for these reviews in one query
    comments = Comment.objects.filter(review_id__in=review_ids).select_related('user').order_by('created_at')
    
    # Fetch all likes for these reviews
    likes = ReviewLike.objects.filter(review_id__in=review_ids)
    
    # Get reviews that the current user has liked (for UI state)
    user_likes = set(
        ReviewLike.objects.filter(
            review_id__in=review_ids, 
            user=request.user
        ).values_list('review_id', flat=True)
    )

    # Get additional feed data
    top_albums = get_top_3_albums()  # Top rated albums
    groups = get_groups_by_user(request.user.username)  # User's groups
    suggested_users_raw = get_suggested_users(request)  # Users to follow
    
    # Process suggested users and add follow status
    suggested_users = []
    if suggested_users_raw:
        # Get IDs of users that current user is already following
        following_ids = set(
            UserRelationship.objects.filter(
                user_id=request.user
            ).values_list('following__id', flat=True)
        )
        
        # Convert User objects to dictionaries with follow status
        for user in suggested_users_raw:
            # Handle both User objects and dictionaries
            if hasattr(user, 'id'):  # It's a User object
                user_dict = {
                    'id': user.id,
                    'username': user.username,
                    'profile_picture': user.profile_picture.url if user.profile_picture else '/media/profile_pictures/default.jpg',
                    'is_following': user.id in following_ids
                }
            else:  # It's already a dictionary
                user_dict = user.copy()
                user_dict['is_following'] = user.get('id') in following_ids
            
            suggested_users.append(user_dict)

    # Group comments by review ID for efficient lookup
    comment_map = {}
    for c in comments:
        comment_map.setdefault(c.review_id, []).append(c)

    # Group likes by review ID and count them
    like_count_map = {}
    for l in likes:
        like_count_map.setdefault(l.review_id, 0)
        like_count_map[l.review_id] += 1

    # Process each review with all its related data
    review_data = []
    for review in reviews:
        review_data.append({
            "id": review.id,
            "soundscore_user": {  # User who created the review
                "id": review.user.id,
                "username": review.user.username,
                "profile_picture": review.user.profile_picture.url if review.user.profile_picture else '/media/profile_pictures/default.jpg',
            },
            "soundscore_album": {  # Album being reviewed
                "id": review.album.id,
                "spotify_id": review.album.spotify_id,
                "title": review.album.title,
                "artist": review.album.artist,
                "cover_image": review.album.cover_image,
            },
            "rating": review.rating,
            "text": review.text,
            "created_at": review.created_at,
            "is_favorite": review.is_favorite,
            "comments": [  # First 3 comments for this review
                {
                    "id": c.id,
                    "text": c.text,
                    "user": {
                        "id": c.user.id,
                        "username": c.user.username,
                        "profile_picture": c.user.profile_picture.url,
                    },
                    "created_at": c.created_at,
                } for c in comment_map.get(review.id, [])[:3]
            ],
            "comment_count": len(comment_map.get(review.id, [])),  # Total comment count
            "is_liked": review.id in user_likes,  # Whether current user liked this review
            "like_count": like_count_map.get(review.id, 0),  # Total like count
        })

    # Prepare context data for the template
    context = {
        'reviews': review_data,
        'top_albums': top_albums,
        'groups': groups,
        'suggested_users': suggested_users,
    }
    
    # Render the feed template with all the data
    return render(request, 'feed/feed.html', context)