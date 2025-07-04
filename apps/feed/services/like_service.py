from apps.reviews.models import ReviewLike
from apps.reviews.models import Review
from apps.users.models import User
from apps.feed.services.notification_service import create_notification_service


def toggle_like_service(review_id, username):
    """Toggle the like status for a review by a specific user.
    Creates a like if it doesn't exist, removes it if it does.
    Also creates a notification for the review author when liked (but not when unliked).
    Returns the new like status and updated like count."""
    
    # Find the user who is performing the like/unlike action
    user = User.objects.filter(username=username).first()
    if not user:
        raise Exception("User not found")
    
    # Find the review that is being liked/unliked
    review = Review.objects.filter(id=review_id).first()
    if not review:
        raise Exception("Review not found")

    # Check if this user has already liked this review
    like = ReviewLike.objects.filter(user=user, review=review).first()
    
    if like:
        # User has already liked this review, so remove the like (unlike)
        like.delete()
        liked = False
    else:
        # User hasn't liked this review yet, so create a new like
        ReviewLike.objects.create(user=user, review=review)
        liked = True

    # Get the updated total like count for this review
    like_count = ReviewLike.objects.filter(review=review).count()

    # Create a notification only when liking (not unliking) and only if the liker
    # is not the same person who wrote the review (no self-notifications)
    if liked and review.user.id != user.id:
        # Create a personalized notification message
        message = f"@{user.username} liked your review!"
        
        # Send notification to the review author
        create_notification_service(
             recipient_id=review.user.id,  # Person who wrote the review
             actor_id=user.id,             # Person who liked the review
             notification_type='like',     # Type of notification
             review_id=review.id,          # Reference to the liked review
             message=message               # Human-readable message
         )

    # Return the current like status and updated count for the frontend
    return {"liked": liked, "count": like_count}
