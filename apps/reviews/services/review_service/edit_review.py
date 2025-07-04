from apps.reviews.models import Review
from datetime import datetime

def edit_review(review_id, rating, text=None, is_favorite=False):
    """
    Edit an existing review's rating, text, and favorite status.
    Parameters:
        review_id (int): ID of the review to edit
        rating (int): New rating (1-5)
        text (str): New review text (optional)
        is_favorite (bool): Whether the review is marked as favorite
    Returns:
        dict: Success or error message and updated review data
    """
    try:
        # Validate rating
        if not 1 <= rating <= 5:
            return {"error": "Rating must be between 1 and 5"}
        # Find the review
        review = Review.objects.filter(id=review_id).first()
        if not review:
            return {"error": "Review not found"}
        # Update fields
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