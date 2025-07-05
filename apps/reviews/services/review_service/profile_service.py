from apps.users.models import User, UserRelationship
from apps.reviews.models import Review
from django.db.models import Avg
from django.conf import settings

def get_user_profile_data(username):
    """
    Get user profile data including review count, average rating, and follower/following data.
    Parameters:
        username (str): Username of the user
    Returns:
        dict: User profile data, reviews, counts, and profile picture URL
    """
    try:
        # Find the user
        user = User.objects.filter(username=username).first()
        if not user:
            return {
                'user': None,
                'user_reviews': [],
                'review_count': 0,
                'avg_rating': 0,
                'profile_picture_url': settings.DEFAULT_PROFILE_PICTURE,
                'followers_count': 0,
                'following_count': 0,
            }
        
        # Get all reviews by the user
        reviews = Review.objects.filter(user=user)
        reviews_count = reviews.count()
        avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        
        # Get follower/following counts
        followers_count = UserRelationship.objects.filter(following=user).count()
        following_count = UserRelationship.objects.filter(user_id=user).count()
        
        # Get profile picture URL or default
        if user.profile_picture:
            profile_picture_url = user.profile_picture
        else:
            profile_picture_url = settings.DEFAULT_PROFILE_PICTURE
            
        user_dict = {
            'username': user.username,
            'profile_picture_url': profile_picture_url
        }
        
        # Build review list for the user
        user_reviews = [
            {
                'id': review.id,
                'rating': review.rating,
                'text': review.text,
                'created_at': review.created_at,
                'soundscore_album': {
                    'title': review.album.title if review.album else '',
                    'artist': review.album.artist if review.album else '',
                    'cover_image': review.album.cover_image if review.album and review.album.cover_image else '/static/images/default_album.png',
                }
            }
            for review in reviews
        ]

        return {
            'user': user_dict,
            'user_reviews': user_reviews,
            'review_count': reviews_count,
            'avg_rating': round(avg_rating, 1),
            'profile_picture_url': profile_picture_url,
            'followers_count': followers_count,
            'following_count': following_count,
        }
    except Exception as e:
        print(f"Error getting user profile data: {e}")
        return {
            'user': None,
            'user_reviews': [],
            'review_count': 0,
            'avg_rating': 0,
            'profile_picture_url': settings.DEFAULT_PROFILE_PICTURE,
            'followers_count': 0,
            'following_count': 0,
        }