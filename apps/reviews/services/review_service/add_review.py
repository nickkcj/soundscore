from apps.reviews.models import Review, Album
from apps.users.models import User
from datetime import datetime

def add_review(user_id, album_id, rating, album_title=None, album_artist=None, 
               album_cover=None, text=None, is_favorite=False):
    try:
        # Step 1: Get or create album
        album, created = Album.objects.get_or_create(
            spotify_id=album_id,
            defaults={
                'title': album_title or "",
                'artist': album_artist or "",
                'cover_image': album_cover or "",
            }
        )
        # Step 2: Get user
        user = User.objects.filter(id=user_id).first()
        if not user:
            return {"error": "User not found"}

        # Step 3: Check if user already reviewed this album
        review = Review.objects.filter(user=user, album=album).first()
        if review:
            # Update existing review
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
        # Step 4: Create new review
        review = Review.objects.create(
            user=user,
            album=album,
            rating=rating,
            text=text or "",
            is_favorite=is_favorite,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        return {
            "success": True,
            "message": "Review added successfully",
            "review": {
                "id": review.id,
                "rating": review.rating,
                "text": review.text,
                "is_favorite": review.is_favorite,
                "created_at": review.created_at,
                "updated_at": review.updated_at,
            }
        }
    except Exception as e:
        return {"error": str(e)}