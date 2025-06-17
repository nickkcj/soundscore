from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from apps.feed.services.notification_service import (
    get_user_notifications_service,
    mark_notification_as_read_service,
    mark_all_as_read_service,
    get_unread_count_service
)
from apps.users.services.supabase_client import authenticate_with_jwt


@login_required
@require_GET
def get_notifications_view(request):
    try:
        client = authenticate_with_jwt()
        if not client:
            return JsonResponse({"error": "Authentication failed"}, status=401)

        user_response = client.table('soundscore_user').select('id') \
            .eq('username', request.user.username).limit(1).execute()
        if not user_response.data:
            return JsonResponse({"error": "User not found"}, status=404)

        user_id = user_response.data[0]['id']

        limit = int(request.GET.get('limit', 10))
        offset = int(request.GET.get('offset', 0))
        unread_only = request.GET.get('unread_only', 'false').lower() == 'true'

        notifications = get_user_notifications_service(user_id, limit, offset, unread_only)
        unread_count = get_unread_count_service(user_id)

        return JsonResponse({
            "notifications": notifications,
            "unread_count": unread_count,
            "has_more": len(notifications) == limit
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
        client = authenticate_with_jwt()
        if not client:
            return JsonResponse({"error": "Authentication failed"}, status=401)

        user_response = client.table('soundscore_user').select('id') \
            .eq('username', request.user.username).limit(1).execute()
        if not user_response.data:
            return JsonResponse({"error": "User not found"}, status=404)

        user_id = user_response.data[0]['id']

        mark_all_as_read_service(user_id)
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_GET
def get_unread_count_view(request):
    try:
        client = authenticate_with_jwt()
        if not client:
            return JsonResponse({"error": "Authentication failed"}, status=401)

        user_response = client.table("soundscore_user").select("id") \
            .eq("username", request.user.username).limit(1).execute()
        if not user_response.data:
            return JsonResponse({"error": "User not found"}, status=404)

        user_id = user_response.data[0]["id"]
        count = get_unread_count_service(user_id)
        return JsonResponse({"unread_count": count})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
