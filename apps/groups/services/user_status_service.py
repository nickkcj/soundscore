import redis
import os
from apps.users.models import User
from apps.groups.models import Group
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Redis connection for production
redis_client = redis.StrictRedis.from_url(
    os.environ.get('REDIS_URL', 'redis://localhost:6379'),
    decode_responses=True
)

def set_online_status(username, group_id, is_online):
    """
    Set the online status of a user in a group using Redis.
    Parameters:
        username (str): Username of the user
        group_id (int): ID of the group
        is_online (bool): True if online, False if offline
    """
    try:
        # Redis key for this user in this group
        key = f"online:{group_id}:{username}"
        
        if is_online:
            # Set user as online with 60 second expiration (auto-cleanup if no ping)
            redis_client.setex(key, 60, "1")
            print(f"User {username} is now ONLINE in group {group_id}")
        else:
            # Remove user from online list
            redis_client.delete(key)
            print(f"User {username} is now OFFLINE in group {group_id}")
        
        # Trigger broadcast to update all clients
        trigger_broadcast_online_users(group_id)
        
    except Exception as e:
        print(f"Error setting online status: {e}")

def is_user_online(username, group_id):
    """
    Check if a user is online in a specific group.
    """
    try:
        key = f"online:{group_id}:{username}"
        return redis_client.exists(key) > 0
    except Exception as e:
        print(f"Error checking online status: {e}")
        return False

def get_online_users_in_group(group_id):
    """
    Get all online users in a group.
    """
    try:
        pattern = f"online:{group_id}:*"
        keys = redis_client.keys(pattern)
        usernames = [key.split(":")[-1] for key in keys]
        return usernames
    except Exception as e:
        print(f"Error getting online users: {e}")
        return []

def get_online_users_count(group_id):
    """
    Get count of online users in a group.
    """
    try:
        pattern = f"online:{group_id}:*"
        return len(redis_client.keys(pattern))
    except Exception as e:
        print(f"Error getting online count: {e}")
        return 0

def ping_user_online(username, group_id):
    """
    Refresh a user's online status (extend TTL).
    Call this from your HTTP ping endpoint.
    """
    set_online_status(username, group_id, True)

def trigger_broadcast_online_users(group_id):
    """
    Trigger broadcast of online users to all WebSocket connections in the group.
    """
    try:
        channel_layer = get_channel_layer()
        group_name = f"group_{group_id}"
        
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "trigger_broadcast_online_users",
            }
        )
    except Exception as e:
        print(f"Error broadcasting online users: {e}")

def cleanup_expired_users():
    """
    Optional: Manual cleanup of expired keys (Redis TTL handles this automatically).
    """
    # Redis automatically removes expired keys, so this is optional
    pass

