from django.db.models import Avg, Count
from apps.users.models import User, UserRelationship
from apps.reviews.models import Review

def get_user_profile_data(username):
    try:
        user = User.objects.get(username=username)
        if user.profile_picture and hasattr(user.profile_picture, 'url'):
            profile_picture = user.profile_picture.url
        else:
            profile_picture = '/media/profile_pictures/default.jpg'

        # Get review data
        reviews = Review.objects.filter(user=user)
        reviews_count = reviews.count()
        avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']
        avg_rating = round(avg_rating, 1) if avg_rating else 0
        
        # Get follower/following counts
        followers_count = UserRelationship.objects.filter(following=user).count()
        following_count = UserRelationship.objects.filter(user_id=user).count()
        
        user_dict = {
            'username': user.username,
            'profile_picture_url': profile_picture
        }
        
        user_reviews = [
            {
                'id': review.id,
                'album': review.album.title if review.album else None,
                'rating': review.rating,
                'text': review.text,
                'created_at': review.created_at,
            }
            for review in reviews
        ]
        
        return {
            'user': user_dict,
            'user_reviews': user_reviews,
            'review_count': reviews_count,
            'avg_rating': avg_rating,
            'profile_picture_url': profile_picture,
            'followers_count': followers_count,
            'following_count': following_count,
        }

    except User.DoesNotExist:
        return {
            'user': None,
            'user_reviews': [],
            'review_count': 0,
            'avg_rating': 0,
            'profile_picture_url': '/media/profile_pictures/default.jpg',
            'followers_count': 0,
            'following_count': 0,
        }



