from apps.reviews.models import Album, Review
from django.db.models import Avg, Count

def get_top_3_albums():
    try:
        albums = (
            Album.objects.annotate(
                avg_rating=Avg('reviews__rating'),
                review_count=Count('reviews')
            )
            .filter(review_count__gt=0)
            .order_by('-avg_rating', '-review_count')[:3]
        )
        return [
            {
                'id': album.id,
                'spotify_id': album.spotify_id,
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
    

def get_album_avg_rating(album_id):
    try:
        album = Album.objects.get(id=album_id)
        avg_rating = album.review.aggregate(avg=Avg('rating'))['avg']
        return round(avg_rating, 1) if avg_rating is not None else 'No ratings'
    except Album.DoesNotExist:
        return 'Album not found'
    except Exception as e:
        return f"Error calculating average rating: {str(e)}"


def get_trending_albums(limit=8):
    try:
        albums = (
            Album.objects.annotate(review_count=Count('reviews'))
            .filter(review_count__gt=0)
            .order_by('-review_count', 'title')[:limit]
        )
        return [
            {
                'id': album.id,
                'spotify_id': album.spotify_id,
                'title': album.title,
                'artist': album.artist,
                'cover_url': album.cover_image or '/static/images/default_album.png',
                'review_count': album.review_count,
            }
            for album in albums
        ]
    except Exception as e:
        return {"error": f"Error fetching trending albums: {str(e)}"}

