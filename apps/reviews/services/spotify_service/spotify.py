import requests
import base64
from django.conf import settings

def get_token():
    """
    Get a Spotify access token using client credentials flow.
    Returns:
        str: Access token string, or None if authentication fails.
    """
    client_id = settings.SPOTIFY_CLIENT_ID
    client_secret = settings.SPOTIFY_CLIENT_SECRET

    # Prepare the authorization header
    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}

    # Request the token from Spotify
    response = requests.post(url, headers=headers, data=data)
    response_data = response.json()

    # Return the access token or None
    return response_data.get("access_token")

def search_albums(artist_name):
    """
    Search for albums by artist name using the Spotify API.
    Parameters:
        artist_name (str): Name of the artist to search for.
    Returns:
        list or dict: List of album dicts, or error dict.
    """
    token = get_token()
    if not token:
        return {"error": "Could not authenticate with Spotify"}

    # Build the search URL and headers
    url = f"https://api.spotify.com/v1/search?q={artist_name}&type=album&limit=10"
    headers = {"Authorization": f"Bearer {token}"}

    # Make the request to Spotify
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {"error": "Failed to fetch data from Spotify"}

    data = response.json()
    albums = []

    # Parse the album data from the response
    for item in data.get("albums", {}).get("items", []):
        albums.append({
            "id": item["id"],
            "title": item["name"],
            "artist": item["artists"][0]["name"] if item["artists"] else "Unknown Artist",
            "cover_url": item["images"][0]["url"] if item["images"] else None,
            "release_date": item.get("release_date", "Unknown")
        })

    return albums

def get_album_info(spotify_id):
    """
    Fetch detailed album info from Spotify by album ID.
    Parameters:
        spotify_id (str): Spotify album ID.
    Returns:
        dict: Album information or error dict.
    """
    token = get_token()
    if not token:
        return {"error": "Could not authenticate with Spotify"}

    url = f"https://api.spotify.com/v1/albums/{spotify_id}"
    headers = {"Authorization": f"Bearer {token}"}

    # Request album info from Spotify
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {"error": "Failed to fetch album info from Spotify"}

    data = response.json()
    # Return relevant album info
    return {
        "album_type": data.get("album_type"),
        "total_tracks": data.get("total_tracks"),
        "external_urls": data.get("external_urls", {}).get("spotify"),
        "images": [img.get("url") for img in data.get("images", [])],
        "name": data.get("name"),
        "release_date": data.get("release_date"),
        "artists": [artist.get("name") for artist in data.get("artists", [])],
    }

def get_album_tracks(spotify_id, market=None, limit=50, offset=0):
    """
    Fetch tracks for a given album from Spotify.
    Parameters:
        spotify_id (str): Spotify album ID.
        market (str): Optional market code.
        limit (int): Number of tracks to return (default 50).
        offset (int): Offset for pagination (default 0).
    Returns:
        list: List of track dicts, or empty list on error.
    """
    token = get_token()
    if not token:
        return []
    # Build the URL for tracks endpoint
    url = f"https://api.spotify.com/v1/albums/{spotify_id}/tracks?limit={limit}&offset={offset}"
    if market:
        url += f"&market={market}"
    headers = {"Authorization": f"Bearer {token}"}
    # Request tracks from Spotify
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return []
    data = resp.json()
    return data.get("items", [])



