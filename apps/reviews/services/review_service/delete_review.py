from apps.reviews.models import Review
from apps.users.models import User

def delete_review(user, review_id):
    """
    Delete a review if it belongs to the given user.
    Parameters:
        user (str): Username of the user
        review_id (int): ID of the review to delete
    Returns:
        dict: Success or error message
    """
    try:
        # Find the user object
        user_obj = User.objects.filter(username=user).first()
        if not user_obj:
            return {"error": "User not found"}
        # Find the review belonging to this user
        review = Review.objects.filter(id=review_id, user=user_obj).first()
        if not review:
            return {"error": "Review not found"}
        # Delete the review
        review.delete()
        return {
            "success": True,
            "message": "Review deleted successfully"
        }
    except Exception as e:
        return {"error": str(e)}