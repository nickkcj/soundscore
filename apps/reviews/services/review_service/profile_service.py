from apps.users.models import User
from apps.reviews.models import Review
from django.db.models import Avg

def get_user_profile_data(username):
    """
    Get user profile data including review count and average rating.
    """
    try:
        user = User.objects.filter(username=username).first()
        if not user:
            return {
                'reviews_count': 0,
                'avg_rating': 0,
                'profile_picture_url': '/static/images/default.jpg'
            }
        reviews = Review.objects.filter(user=user)
        reviews_count = reviews.count()
        avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        return {
            'reviews_count': reviews_count,
            'avg_rating': round(avg_rating, 1),
            'profile_picture_url': user.profile_picture or '/static/images/default.jpg'
        }
    except Exception as e:
        print(f"Error getting user profile data: {e}")
        return {
            'reviews_count': 0,
            'avg_rating': 0,
            'profile_picture_url': '/static/images/default.jpg'
        }