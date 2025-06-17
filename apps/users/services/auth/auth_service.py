from apps.users.services.supabase_client import authenticate_with_jwt
from django.contrib.auth.hashers import make_password


def register_user(username, email, password):
    client = authenticate_with_jwt()

    client.table('soundscore_user').insert({
        'username': username,
        'email': email,
        'password': password
    }).execute()

    return {"username": username, "email": email}


def authenticate_user(username):
    client = authenticate_with_jwt()

    user_resp = client.table('soundscore_user') \
        .select('id, username, email, profile_picture') \
        .eq('username', username) \
        .limit(1) \
        .execute()

    if not user_resp.data:
        raise Exception("User does not exist")

    return user_resp.data[0]
