from apps.reviews.models import ReviewLike
from apps.reviews.models import Review
from apps.users.models import User
from apps.feed.services.notification_service import create_notification_service


def toggle_like_service(review_id, username):
    user = User.objects.filter(username=username).first()
    if not user:
        raise Exception("User not found")
    review = Review.objects.filter(id=review_id).first()
    if not review:
        raise Exception("Review not found")

    like = ReviewLike.objects.filter(user=user, review=review).first()
    if like:
        like.delete()
        liked = False
    else:
        ReviewLike.objects.create(user=user, review=review)
        liked = True

    like_count = ReviewLike.objects.filter(review=review).count()

    if liked and review.user.id != user.id:
        message = f"@{user.username} liked your review!"
        create_notification_service(
            recipient_id=review.user.id,
            actor_id=user.id,
            notification_type='like',
            review_id=review.id,
            message=message
        )

    return {"liked": liked, "count": like_count}
