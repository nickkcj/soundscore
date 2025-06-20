from apps.reviews.models import Review
from datetime import datetime

def edit_review(review_id, rating, text=None, is_favorite=False):
    try:
        if not 1 <= rating <= 5:
            return {"error": "Rating must be between 1 and 5"}
        review = Review.objects.filter(id=review_id).first()
        if not review:
            return {"error": "Review not found"}
        review.rating = rating
        review.text = text or ""
        review.is_favorite = is_favorite
        review.updated_at = datetime.now()
        review.save()
        return {
            "success": True,
            "message": "Review updated successfully",
            "review": {
                "id": review.id,
                "rating": review.rating,
                "text": review.text,
                "is_favorite": review.is_favorite,
                "updated_at": review.updated_at,
            }
        }
    except Exception as e:
        return {"error": str(e)}