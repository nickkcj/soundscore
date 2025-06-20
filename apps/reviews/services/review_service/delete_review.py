from apps.reviews.models import Review
from apps.users.models import User

def delete_review(user, review_id):
    try:
        user_obj = User.objects.filter(username=user).first()
        if not user_obj:
            return {"error": "User not found"}
        review = Review.objects.filter(id=review_id, user=user_obj).first()
        if not review:
            return {"error": "Review not found"}
        review.delete()
        return {
            "success": True,
            "message": "Review deleted successfully"
        }
    except Exception as e:
        return {"error": str(e)}