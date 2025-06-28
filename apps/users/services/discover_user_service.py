from apps.users.models import User
from apps.reviews.models import Review
from django.db.models import Avg

def search_users(query, limit=10):
    users_qs = User.objects.filter(username__icontains=query)[:limit]
    user_list = []
    for user in users_qs:
        reviews = Review.objects.filter(user=user)
        review_count = reviews.count()
        avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']
        avg_rating = round(avg_rating, 1) if avg_rating is not None else 'No ratings'
        if user.profile_picture:
            profile_picture_url = user.profile_picture.url
        else:
            profile_picture_url = None
        user_list.append({
            'username': user.username,
            'profile_picture_url': profile_picture_url,
            'review_count': review_count,
            'avg_rating': avg_rating
        })
    return user_list