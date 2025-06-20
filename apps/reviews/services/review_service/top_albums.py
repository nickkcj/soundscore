from apps.reviews.models import Album, Review
from django.db.models import Avg, Count

def get_top_3_albums():
    try:
        albums = (
            Album.objects.annotate(
                avg_rating=Avg('review__rating'),
                review_count=Count('review')
            )
            .filter(review_count__gt=0)
            .order_by('-avg_rating', '-review_count')[:3]
        )
        return [
            {
                'id': album.id,
                'title': album.title,
                'artist': album.artist,
                'cover_image': album.cover_image,
                'avg_rating': album.avg_rating,
                'avg_rating_rounded': round(album.avg_rating) if album.avg_rating else 0,
                'review_count': album.review_count,
            }
            for album in albums
        ]
    except Exception as e:
        return {"error": f"Error calculating top albums: {str(e)}"}

