from .supabase_client import authenticate_with_jwt
from datetime import datetime

def add_user_supabase(username, password, email):
    client = authenticate_with_jwt()
    if not client:
        return {"error": "Failed to authenticate with Supabase"}
    
    try:
        existing_user = client.table('soundscore_user').select('*')\
            .or_('username.eq.' + username + ',email.eq.' + email).execute()
        
        if existing_user.data:
            return {"error": "Username or email already exists"}
        
        user_data = {
            'username': username,
            'password': password,
            'email': email,
            'created_at': datetime.now().isoformat(),
            'is_superuser': False,
            'is_active': True,
            'is_staff': False,
        }
        
        user_insert = client.table('soundscore_user').insert(user_data).execute()
        
        if not user_insert.data:
            return {"error": "Failed to create user record"}
        
        return {
            "success": True,
            "message": "User created successfully",
            "user_id": user_insert.data[0].get('id')
        }
    
    except Exception as e:
        return {"error": str(e)}