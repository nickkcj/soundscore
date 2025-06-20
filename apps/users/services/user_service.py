from django.db.models import Avg
from apps.users.models import User
from apps.reviews.models import Review

def get_user_profile_data(username):
    try:
        user = User.objects.get(username=username)
        profile_picture = (
            user.profile_picture.url if user.profile_picture else '/static/images/default.jpg'
        )

        reviews = Review.objects.filter(user=user)
        reviews_count = reviews.count()

        avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']
        avg_rating = round(avg_rating, 1) if avg_rating else 0

        return {
            'reviews_count': reviews_count,
            'avg_rating': avg_rating,
            'profile_picture_url': profile_picture
        }

    except User.DoesNotExist:
        return {
            'reviews_count': 0,
            'avg_rating': 0,
            'profile_picture_url': '/static/images/default.jpg'
        }
    


