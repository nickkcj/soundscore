from apps.reviews.models import Album, Review
from django.db.models import Avg

def search_albums_and_artists(query, search_type, search_albums_func, get_album_avg_rating_func):
    """
    Search for albums and/or artists using a Spotify search function and enrich with local DB data.
    Parameters:
        query (str): Search query
        search_type (str): 'all', 'albums', or 'artists'
        search_albums_func (callable): Function to search albums on Spotify
        get_album_avg_rating_func (callable): Function to get album average rating
    Returns:
        dict: Albums and artists with average ratings
    """
    results = {
        'albums': [],
        'artists': [],
    }
    spotify_album_results = []
    if search_type in ['all', 'albums', 'artists']:
        try:
            # Call the external search function (e.g., Spotify API)
            spotify_album_results = search_albums_func(query)
            if isinstance(spotify_album_results, dict) and 'error' in spotify_album_results:
                spotify_album_results = []
            if not isinstance(spotify_album_results, list):
                spotify_album_results = []
        except Exception:
            spotify_album_results = []

    # Process albums
    if search_type in ['all', 'albums'] and isinstance(spotify_album_results, list):
        processed_albums = []
        for album_data in spotify_album_results:
            spotify_id = album_data.get('id')
            if not spotify_id:
                continue
            current_album = album_data.copy()
            current_album['spotify_id'] = spotify_id
            # Try to find the album in the local DB by spotify_id
            album_obj = Album.objects.filter(spotify_id=spotify_id).first()
            if album_obj:
                avg_rating = Review.objects.filter(album=album_obj).aggregate(avg=Avg('rating'))['avg']
                if avg_rating is not None:
                    avg_rating = round(avg_rating, 1)
                    rating_display = f"{avg_rating} / 5"
                else:
                    rating_display = "No reviews yet"
            else:
                rating_display = "No reviews yet"
            current_album['avg_rating'] = rating_display
            processed_albums.append(current_album)
        results['albums'] = processed_albums

    # Process artists
    if search_type in ['all', 'artists'] and isinstance(spotify_album_results, list):
        artists_dict = {}
        for album_data in spotify_album_results:
            artist_name = album_data.get('artist')
            spotify_id = album_data.get('id')
            if not artist_name or not spotify_id:
                continue
            current_album_for_artist = album_data.copy()
            album_obj = Album.objects.filter(spotify_id=spotify_id).first()
            if album_obj:
                avg_rating = Review.objects.filter(album=album_obj).aggregate(avg=Avg('rating'))['avg']
                if avg_rating is not None:
                    avg_rating = round(avg_rating, 1)
                    rating_display = f"{avg_rating} / 5"
                else:
                    rating_display = "No reviews yet"
            else:
                rating_display = "No reviews yet"
            current_album_for_artist['avg_rating'] = rating_display
            if artist_name not in artists_dict:
                artists_dict[artist_name] = {'name': artist_name, 'albums': []}
            artists_dict[artist_name]['albums'].append(current_album_for_artist)
        results['artists'] = list(artists_dict.values())

    return results