from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json
from apps.groups.services.group_service import (
    create_group, get_all_groups, get_group_room_data, join_group
)
from apps.groups.services.user_status_service import set_online_status

@login_required
def create_group_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description", "")
        category = request.POST.get("category")
        privacy = request.POST.get("privacy")
        cover_image = request.FILES.get("cover_image")

        group_id = create_group(name, description, category, privacy, cover_image, request.user.username)
        return redirect("group_room", group_id=group_id)

def all_groups_view(request):
    data = get_all_groups()
    return render(request, "groups/group_list.html", data)

@login_required
def group_room_view(request, group_id):
    data = get_group_room_data(group_id, request.user.username)
    return render(request, "groups/group_room.html", data)

@login_required
def join_group_view(request, group_id):
    join_group(group_id, request.user.username)
    return redirect("group_room", group_id=group_id)

@login_required
def set_online_status_view(request):
    try:
        data = json.loads(request.body)
        group_id = int(data.get("group_id"))
        is_online = data.get("is_online") is True

        set_online_status(request.user.username, group_id, is_online)
        return JsonResponse({"ok": True, "status": "online" if is_online else "offline"})

    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=500)
