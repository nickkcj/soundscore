from supabase import create_client
from decouple import config
import jwt

def get_supabase_client():
    url = config("SUPABASE_URL")
    key = config("SUPABASE_KEY")
    supabase = create_client(url, key)

    return supabase


def authenticate_with_jwt():
    client = get_supabase_client()
    response = client.auth.sign_in_with_password({
        'email': config("SUPABASE_EMAIL"),
        'password': config("SUPABASE_PASSWORD")
    })
    try:
        access_token = response.session.access_token
        client.postgrest.auth(access_token)
        response = client.table('soundscore_user').select('*').limit(1).execute()
        return client


    except Exception as e:
        print(f"JWT authentication error: {e}")
        return False
    


def get_admin_client():
    url = config("SUPABASE_URL")
    key = config("SUPABASE_SERVICE_KEY")  # Service key, NOT anon key!
    return create_client(url, key)

