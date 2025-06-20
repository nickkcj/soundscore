from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from apps.feed.services.notification_service import (
    get_user_notifications_service,
    mark_notification_as_read_service,
    mark_all_as_read_service,
    get_unread_count_service
)


@login_required
@require_GET
def get_notifications_view(request):
    try:
        user_id = request.user.id
        limit = int(request.GET.get('limit', 10))
        offset = int(request.GET.get('offset', 0))
        unread_only = request.GET.get('unread_only', 'false').lower() == 'true'

        notifications = get_user_notifications_service(user_id, limit, offset, unread_only)
        unread_count = get_unread_count_service(user_id)

        # If notifications are QuerySets, convert to list of dicts
        notifications_list = [
            {
                "id": n.id,
                "type": n.type,
                "message": n.message,
                "is_read": n.is_read,
                "created_at": n.created_at,
                "actor": getattr(n.actor, "username", None),
                "review_id": getattr(n, "review_id", None),
            }
            for n in notifications
        ]

        return JsonResponse({
            "notifications": notifications_list,
            "unread_count": unread_count,
            "has_more": len(notifications_list) == limit
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_POST
def mark_read_view(request, notification_id):
    try:
        mark_notification_as_read_service(notification_id)
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_POST
def mark_all_read_view(request):
    try:
        user_id = request.user.id
        mark_all_as_read_service(user_id)
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_GET
def get_unread_count_view(request):
    try:
        user_id = request.user.id
        count = get_unread_count_service(user_id)
        return JsonResponse({"unread_count": count})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
