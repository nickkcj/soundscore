from apps.users.models import User
from apps.reviews.models import Review
from django.db.models import Count


def get_suggested_users(request, limit=3):
    """Get users with the most reviews for the feed."""
    try:
        users = (
            User.objects.annotate(review_count=Count('reviews'))
            .order_by('-review_count', '-last_active')[:limit]
        )
        return users
    
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }

