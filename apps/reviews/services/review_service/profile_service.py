from apps.users.models import User, UserRelationship
from apps.reviews.models import Review
from django.db.models import Avg

def get_user_profile_data(username):
    """
    Get user profile data including review count, average rating, and follower data.
    """
    try:
        user = User.objects.filter(username=username).first()
        if not user:
            return {
                'user': None,
                'user_reviews': [],
                'review_count': 0,
                'avg_rating': 0,
                'profile_picture_url': '/media/profile_pictures/default.jpg',
                'followers_count': 0,
                'following_count': 0,
            }
        
        reviews = Review.objects.filter(user=user)
        reviews_count = reviews.count()
        avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        
        # Get follower/following counts
        followers_count = UserRelationship.objects.filter(following=user).count()
        following_count = UserRelationship.objects.filter(user_id=user).count()
        
        if user.profile_picture and hasattr(user.profile_picture, 'url'):
            profile_picture_url = user.profile_picture.url
        else:
            profile_picture_url = '/media/profile_pictures/default.jpg'
            
        user_dict = {
            'username': user.username,
            'profile_picture_url': profile_picture_url
        }
        
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
            'profile_picture_url': '/media/profile_pictures/default.jpg',
            'followers_count': 0,
            'following_count': 0,
        }