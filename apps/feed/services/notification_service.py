from apps.feed.models import Notification
from apps.users.models import User
from apps.reviews.models import Review


def create_notification_service(recipient_id, actor_id, notification_type, message, review_id=None):
    notification = Notification.objects.create(
        recipient_id=recipient_id,
        actor_id=actor_id,
        notification_type=notification_type,
        review_id=review_id,
        message=message,
        is_read=False
    )
    return notification


def get_user_notifications_service(user_id, limit=10, offset=0, unread_only=False):
    qs = Notification.objects.filter(recipient_id=user_id)
    if unread_only:
        qs = qs.filter(is_read=False)
    qs = qs.select_related('actor').order_by('-created_at')[offset:offset+limit]
    return list(qs)


def mark_notification_as_read_service(notification_id):
    Notification.objects.filter(id=notification_id).update(is_read=True)
    return {"success": True}


def mark_all_as_read_service(user_id):
    Notification.objects.filter(recipient_id=user_id).update(is_read=True)
    return {"success": True}


def get_unread_count_service(user_id):
    return Notification.objects.filter(recipient_id=user_id, is_read=False).count()
