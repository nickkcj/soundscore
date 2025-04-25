from ..user.supabase_client import authenticate_with_jwt


def create_notification(recipient_id, actor_id, notification_type, review_id=None, comment_id=None, message=None):
    """Create a new notification in Supabase"""
    client = authenticate_with_jwt()
    
    try:
        # Ensure we have integer IDs
        recipient_id = int(recipient_id) if recipient_id else None
        actor_id = int(actor_id) if actor_id else None
        review_id = int(review_id) if review_id else None
        comment_id = int(comment_id) if comment_id else None
        
        if not message:
            # Default messages based on notification type
            if notification_type == 'like':
                message = f"Someone liked your review!"
            elif notification_type == 'comment':
                message = f"Someone commented on your review!"
        
        notification_data = {
            'recipient_id': recipient_id,
            'actor_id': actor_id,
            'notification_type': notification_type,
            'message': message
        }
        
        # Add optional fields only if they exist
        if review_id:
            notification_data['review_id'] = review_id
        
        if comment_id:
            notification_data['comment_id'] = comment_id
        
        # Insert into Supabase
        result = client.table('soundscore_notification').insert(notification_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Notification creation error: {e}")
        print(f"Data that failed: {notification_data if 'notification_data' in locals() else 'Not created'}")
        return None

def get_user_notifications(user_id, limit=20, offset=0, unread_only=False):
    """Get notifications for a user with proper joins"""
    client = authenticate_with_jwt()
    try:
        user_id = int(user_id)
        
        # Use the correct join syntax - table name must match exactly
        query = client.table('soundscore_notification').select('''
            *,
            soundscore_user!actor_id(*),
            soundscore_review!review_id(*),
            soundscore_comment!comment_id(*)
        ''').eq('recipient_id', user_id).order('created_at', desc=True)
        
        if unread_only:
            query = query.eq('is_read', False)
        
        result = query.range(offset, offset + limit - 1).execute()
        return result.data
    except Exception as e:
        print(f"Error getting notifications: {e}")
        return []

def mark_notification_as_read(notification_id):
    """Mark a notification as read"""
    client = authenticate_with_jwt()
    try:
        notification_id = int(notification_id)
        return client.table('soundscore_notification').update({'is_read': True}).eq('id', notification_id).execute()
    except Exception as e:
        print(f"Error marking notification as read: {e}")
        return None

def mark_all_as_read(user_id):
    """Mark all notifications as read for a user"""
    client = authenticate_with_jwt()
    try:
        user_id = int(user_id)
        return client.table('soundscore_notification').update({'is_read': True}).eq('recipient_id', user_id).execute()
    except Exception as e:
        print(f"Error marking all notifications as read: {e}")
        return None

def get_unread_count(user_id):
    """Get count of unread notifications for a user"""
    client = authenticate_with_jwt()
    try:
        user_id = int(user_id)
        result = client.table('soundscore_notification').select('id', count='exact').eq('recipient_id', user_id).eq('is_read', False).execute()
        return result.count if hasattr(result, 'count') else 0
    except Exception as e:
        print(f"Error getting unread count: {e}")
        return 0

def get_user_notifications_with_details(user_id, limit=20, offset=0, unread_only=False):
    """Get notifications with formatted user details"""
    notifications = get_user_notifications(user_id, limit, offset, unread_only)
    
    # Format the data for easier consumption by the frontend
    for notification in notifications:
        # Add actor details if available
        actor = notification.get('soundscore_user')
        if actor:
            notification['actor'] = {
                'username': actor.get('username', ''),
                'profile_picture': actor.get('profile_picture', '')
            }
        
        # Add review details if available
        review = notification.get('soundscore_review')
        if review:
            notification['review_details'] = {
                'id': review.get('id'),
                'title': review.get('title', ''),
                'rating': review.get('rating')
            }
        
        # Add comment details if available
        comment = notification.get('soundscore_comment')
        if comment:
            notification['comment_details'] = {
                'id': comment.get('id'),
                'text': comment.get('text', '')
            }
    
    return notifications