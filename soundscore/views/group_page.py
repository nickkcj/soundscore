from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from soundscore.services.user.supabase_client import authenticate_with_jwt
import uuid
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@login_required
def group_chat_page(request, group_id):
    return render(request, 'groups/group_room.html', {
        'group_id': group_id
    })


def all_groups(request):
    supabase = authenticate_with_jwt()
    groups = supabase.table("chat_group").select("*").execute().data
    trending = groups[:4]  # Você pode melhorar isso depois com base em membros ou mensagens

    return render(request, "groups/group_list.html", {
        "groups": groups,
        "trending_groups": trending
    })


@login_required
@csrf_exempt
def create_group(request):
    if request.method == "POST":
        print(f"USER ID CHECK: {request.user.id}")
        name = request.POST.get("name")
        description = request.POST.get("description", "")
        category = request.POST.get("category")
        privacy = request.POST.get("privacy")
        user_id = request.user.id

        cover_image = request.FILES.get("cover_image")
        cover_url = None

        if cover_image:
            supabase = authenticate_with_jwt()
            file_bytes = cover_image.read()
            file_ext = cover_image.name.split(".")[-1]
            filename = f"group_covers/{uuid.uuid4()}.{file_ext}"

            supabase.storage.from_("chat-media").upload(
                path=filename,
                file=file_bytes,
                file_options={"content-type": cover_image.content_type}
            )

            cover_url = supabase.storage.from_("chat-media").get_public_url(filename)

        # Agora criamos o grupo com a URL da imagem
        supabase = authenticate_with_jwt()
        res = supabase.table("chat_group").insert({
            "name": name,
            "description": description,
            "category": category,
            "privacy": privacy,
            "cover_image": cover_url
        }).execute()

        group_id = res.data[0]["id"]

        # Adicionar o criador como membro
        supabase.table("chat_group_member").insert({
            "group_id": group_id,
            "user_id": user_id
        }).execute()

        return redirect("group_room", group_id=group_id)


@login_required
def group_room(request, group_id):
    supabase = authenticate_with_jwt()
    user_id = supabase.table("soundscore_user") \
        .select("id") \
        .eq("username", request.user.username) \
        .execute().data[0]["id"]

    # Auto-join logic...
    existing = supabase.table("chat_group_member").select("*") \
        .eq("group_id", group_id) \
        .eq("user_id", user_id) \
        .execute()
    if not existing.data:
        supabase.table("chat_group_member").insert({
            "group_id": group_id,
            "user_id": user_id
        }).execute()

    group = supabase.table("chat_group").select("*").eq("id", group_id).execute().data[0]
    members = supabase.table("chat_group_member") \
        .select("user_id, soundscore_user(username,profile_picture)") \
        .eq("group_id", group_id).execute().data

    # Get online members (user_id list)
    online_rows = supabase.table("group_user_online") \
        .select("user_id") \
        .eq("group_id", group_id) \
        .eq("is_online", True) \
        .execute().data
    online_ids = {row["user_id"] for row in online_rows}

    # Prepare member list for template
    member_list = []
    for m in members:
        user = m.get("soundscore_user", {})
        member_list.append({
            "user_id": m["user_id"],
            "username": user.get("username", "Unknown"),
            "profile_picture": user.get("profile_picture", "/static/images/default.jpg"),
            "is_online": m["user_id"] in online_ids,
        })

    # Get recent messages, including profile_picture
    recent_messages = supabase.table("chat_group_message") \
        .select("*, soundscore_user(username,profile_picture)") \
        .eq("group_id", group_id) \
        .execute().data

    formatted_messages = []
    for msg in recent_messages:
        username = msg["soundscore_user"]["username"] if "soundscore_user" in msg else "Unknown User"
        profile_picture = (
            msg["soundscore_user"].get("profile_picture")
            if "soundscore_user" in msg and msg["soundscore_user"].get("profile_picture")
            else "/static/images/default.jpg"
        )
        formatted_messages.append({
            "content": msg["content"],
            "username": username,
            "user_id": msg["user_id"],
            "profile_picture": profile_picture,
        })

    return render(request, "groups/group_room.html", {
        "group": group,
        "group_id": group_id,
        "member_count": len(member_list),
        "members": member_list,
        "recent_messages": formatted_messages,
        "current_username": request.user.username,
    })


@login_required
def join_group(request, group_id):
    """Add the current user to a group if not already a member"""
    supabase = authenticate_with_jwt()

    user_id = supabase.table("soundscore_user") \
        .select("id") \
        .eq("username", request.user.username) \
        .execute().data[0]["id"]
    
    print(f"Joining group {group_id} for user {user_id}")
    
    # Check if the user is already a member
    existing = supabase.table("chat_group_member").select("*") \
        .eq("group_id", group_id) \
        .eq("user_id", user_id) \
        .execute()
    
    # If not already a member, add them
    if not existing.data:
        supabase.table("chat_group_member").insert({
            "group_id": group_id,
            "user_id": user_id
        }).execute()
    
    # Redirect to the group room
    return redirect("group_room", group_id=group_id)


#@login_required
@csrf_exempt
def set_online_status(request):
    import json as pyjson
    print("=== set_online_status called ===")
    print("Request method:", request.method)
    print("Request body:", request.body)
    data = pyjson.loads(request.body)
    print("Parsed data:", data)

    group_id = int(data.get("group_id"))  # Ensure integer
    is_online = bool(data.get("is_online", False))
    print("group_id (int):", group_id)
    print("is_online (bool):", is_online)

    supabase = authenticate_with_jwt()
    user_query = supabase.table("soundscore_user") \
        .select("id") \
        .eq("username", request.user.username) \
        .execute()
    print("User query result:", user_query.data)
    user_id = int(user_query.data[0]["id"])
    print("user_id (int):", user_id)

    upsert_data = {
        "group_id": group_id,
        "user_id": user_id,
        "is_online": is_online
    }
    print("Upsert data:", upsert_data)

    try:
        result = supabase.rpc("upsert_group_user_online", {
            "_group_id": group_id,
            "_user_id": user_id,
            "_is_online": is_online
        }).execute()
        print("RPC upsert result:", result)
    except Exception as e:
        print("RPC upsert exception:", e)
        import traceback
        traceback.print_exc()
        return JsonResponse({"ok": False, "error": str(e)}, status=500)

    print("=== set_online_status finished ===")
    return JsonResponse({"ok": True})


