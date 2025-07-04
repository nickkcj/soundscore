from apps.feed.models import Notification
from apps.users.models import User
from apps.reviews.models import Review


def create_notification_service(recipient_id, actor_id, notification_type, message, review_id=None):
    """Create a new notification for a user about an action performed by another user.
    Used for likes, comments, follows, and other social interactions.
    Automatically prevents self-notifications (when recipient = actor)."""
    
    # Prevent users from getting notifications about their own actions
    if recipient_id == actor_id:
        # No need to create a notification if the recipient is the same as the actor
        return None

    # Create the notification record in the database
    notification = Notification.objects.create(
        recipient_id=recipient_id,        # User who will receive the notification
        actor_id=actor_id,               # User who performed the action
        notification_type=notification_type,  # Type: 'like', 'comment', 'follow', etc.
        review_id=review_id,             # Optional: related review ID
        message=message,                 # Human-readable notification text
        is_read=False                    # New notifications start as unread
    )
    return notification


def get_user_notifications_service(user_id, limit=10, offset=0, unread_only=False):
    """Retrieve notifications for a specific user with pagination and filtering options.
    Used to display notifications in the user's notification dropdown/page."""
    
    # Start with all notifications for this user
    qs = Notification.objects.filter(recipient_id=user_id)
    
    # Filter to only unread notifications if requested
    if unread_only:
        qs = qs.filter(is_read=False)
    
    # Include related actor data to avoid additional database queries
    # Order by most recent first and apply pagination
    qs = qs.select_related('actor').order_by('-created_at')[offset:offset+limit]
    
    # Convert QuerySet to list for easier manipulation
    return list(qs)


def mark_notification_as_read_service(notification_id):
    """Mark a specific notification as read when the user views it.
    Used when user clicks on a notification or visits the related content."""
    
    # Update the notification's read status
    Notification.objects.filter(id=notification_id).update(is_read=True)
    
    # Return success confirmation for the frontend
    return {"success": True}


def mark_all_as_read_service(user_id):
    """Mark all notifications for a user as read.
    Used when user clicks 'Mark all as read' button."""
    
    # Update all unread notifications for this user
    Notification.objects.filter(recipient_id=user_id).update(is_read=True)
    
    # Return success confirmation for the frontend
    return {"success": True}


def get_unread_count_service(user_id):
    """Get the count of unread notifications for a user.
    Used to display the notification badge number in the UI."""
    
    # Count only unread notifications for this user
    return Notification.objects.filter(recipient_id=user_id, is_read=False).count()
