from ..user.supabase_client import authenticate_with_jwt, get_admin_client
import logging

from collections import defaultdict

def get_top_3_albums():
    try:
        client = get_admin_client()
        if not client:
            return {"error": "Could not connect to Supabase"}

        # Fetch all albums
        album_response = client.table('soundscore_album') \
            .select('id, title, artist, cover_image') \
            .execute()

        if not album_response.data:
            return {"error": "No albums found"}

        albums = {album['id']: album for album in album_response.data}
        album_ids = list(albums.keys())

        # Fetch all reviews for these albums
        review_response = client.table('soundscore_review') \
            .select('album_id, rating') \
            .in_('album_id', album_ids) \
            .execute()

        if not review_response.data:
            return {"error": "No reviews found"}

        # Calculate average rating per album
        rating_sum = defaultdict(int)
        rating_count = defaultdict(int)

        for review in review_response.data:
            aid = review['album_id']
            rating_sum[aid] += review['rating']
            rating_count[aid] += 1

        # Build list with rating info
        albums_with_ratings = []
        for aid, total in rating_sum.items():
            if aid in albums:
                avg = total / rating_count[aid]
                album = albums[aid]
                album.update({
                    'avg_rating': avg,
                    'avg_rating_rounded': round(avg),
                    'review_count': rating_count[aid]
                })
                albums_with_ratings.append(album)

        # Sort & return top 3
        albums_with_ratings.sort(key=lambda x: x['avg_rating'], reverse=True)
        return albums_with_ratings[:3]

    except Exception as e:
        return {"error": f"Error calculating top albums: {str(e)}"}

