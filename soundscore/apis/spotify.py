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