from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json

from apps.groups.services.group_service import (
    create_group, get_all_groups, get_group_room_data, join_group, get_groups_by_user
)
from apps.groups.services.user_status_service import ping_user_online, set_online_status
from apps.groups.services.message_service import save_message, get_recent_messages

@login_required
def create_group_view(request):
    """
    Handle group creation form submission.
    On POST: creates a group and redirects to its room.
    On GET: renders the group creation form.
    """
    if request.method == "POST":
        # Get form data from POST request
        name = request.POST.get("name")
        description = request.POST.get("description", "")
        category = request.POST.get("category")
        privacy = request.POST.get("privacy")
        cover_image = request.FILES.get("cover_image")

        print("FILES:", request.FILES)
        print("cover_image:", cover_image)
        print("cover_image name:", getattr(cover_image, "name", None))
        print("cover_image size:", getattr(cover_image, "size", None))

        try:
            # Create the group and redirect to its chat room
            group_id = create_group(name, description, category, privacy, cover_image_file=cover_image, username=request.user.username)
            return redirect("group_room", group_id=group_id)
        except Exception as e:
            # Render form with error message if creation fails
            return render(request, "groups/create_group.html", {"error": str(e)})

    # Render the group creation form for GET requests
    # Render the group creation form for GET requests
    return render(request, "groups/create_group.html")
def all_groups_view(request):
    """
    Render the page listing all groups and trending groups.
    """
    data = get_all_groups()
    return render(request, "groups/group_list.html", data)

@login_required
def group_room_view(request, group_id):
    """
    Render the group chat room page for a specific group.
    """
    data = get_group_room_data(group_id, request.user.username)
    # Optionally, include recent messages
    data["recent_messages"] = get_recent_messages(group_id)
    return render(request, "groups/group_room.html", data)

@login_required
def join_group_view(request, group_id):
    """
    Add the current user to the group and redirect to the group room.
    """
    join_group(group_id, request.user.username)
    return redirect("group_room", group_id=group_id)

@csrf_exempt  # Add this decorator
@login_required
def set_online_status_view(request):
    """
    Handle online status updates via HTTP (Redis-based for production).
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            group_id = data.get("group_id")
            is_active = data.get("is_active", False)  # Changed from is_online to is_active
            
            if group_id:
                if is_active:
                    # Ping to keep user online (extends Redis TTL)
                    ping_user_online(request.user.username, group_id)
                else:
                    # Explicitly set offline
                    set_online_status(request.user.username, group_id, False)
                
                return JsonResponse({
                    "ok": True, 
                    "status": "online" if is_active else "offline"
                })
            else:
                return JsonResponse({"ok": False, "error": "group_id required"})
                
        except Exception as e:
            return JsonResponse({"ok": False, "error": str(e)})
    
    return JsonResponse({"ok": False, "error": "POST required"})

@login_required
def send_message_view(request, group_id):
    """
    API endpoint to send a message to a group chat (AJAX).
    Expects POST with 'content'.
    Returns the saved message as JSON.
    """
    if request.method == "POST":
        # Get message content from POST data
        content = request.POST.get("content")
        if not content:
            return JsonResponse({"ok": False, "error": "Message content required"}, status=400)
        # Save the message
        result = save_message(group_id, request.user.id, content)
        if result:
            return JsonResponse({"ok": True, "message": result})
        else:
            return JsonResponse({"ok": False, "error": "Failed to save message"}, status=500)
