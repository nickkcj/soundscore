from apps.reviews.models import Review

def get_latest_reviews(limit=3):
    try:
        reviews = (
            Review.objects
            .select_related('album', 'user')
            .order_by('-created_at')[:limit]
        )
        return [
            {
                'id': r.id,
                'rating': r.rating,
                'text': r.text,
                'created_at': r.created_at,
                'is_favorite': r.is_favorite,
                'album': {
                    'id': r.album.id,
                    'title': r.album.title,
                    'artist': r.album.artist,
                    'cover_image': r.album.cover_image,
                    'spotify_id': getattr(r.album, 'spotify_id', None),
                },
                'user': {
                    'id': r.user.id,
                    'username': r.user.username,
                    'profile_picture': r.user.profile_picture,
                }
            }
            for r in reviews
        ]
    except Exception as e:
        return {"error": f"Error fetching latest reviews: {str(e)}"}




