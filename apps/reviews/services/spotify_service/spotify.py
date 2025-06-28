import requests
import base64
from django.conf import settings

def get_token():
    """Get Spotify access token"""
    client_id = settings.SPOTIFY_CLIENT_ID
    client_secret = settings.SPOTIFY_CLIENT_SECRET

    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}

    response = requests.post(url, headers=headers, data=data)
    response_data = response.json()

    return response_data.get("access_token")

def search_albums(artist_name):
    """Search albums by artist name"""
    token = get_token()
    if not token:
        return {"error": "Could not authenticate with Spotify"}

    url = f"https://api.spotify.com/v1/search?q={artist_name}&type=album&limit=10"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {"error": "Failed to fetch data from Spotify"}

    data = response.json()
    albums = []

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
    """Fetch detailed album info from Spotify by album ID"""
    token = get_token()
    if not token:
        return {"error": "Could not authenticate with Spotify"}

    url = f"https://api.spotify.com/v1/albums/{spotify_id}"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {"error": "Failed to fetch album info from Spotify"}

    data = response.json()
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
    """Fetch album tracks from Spotify by album ID"""
    token = get_token()
    if not token:
        return []
    url = f"https://api.spotify.com/v1/albums/{spotify_id}/tracks?limit={limit}&offset={offset}"
    if market:
        url += f"&market={market}"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return []
    data = resp.json()
    return data.get("items", [])



