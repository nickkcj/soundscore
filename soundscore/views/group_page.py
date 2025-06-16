from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from soundscore.services.user.supabase_client import authenticate_with_jwt
import uuid
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from channels.layers import get_channel_layer # Import
from asgiref.sync import async_to_sync      # Import

@login_required
def group_chat_page(request, group_id):
    return render(request, 'groups/group_room.html', {
        'group_id': group_id
    })


def all_groups(request):
    supabase = authenticate_with_jwt()
    
    # Fetch all groups
    groups_response = supabase.table("chat_group").select("*").execute()
    all_groups = groups_response.data
    
    # For each group, fetch and count its members
    for group in all_groups:
        members_response = supabase.table("chat_group_member").select("*").eq("group_id", group["id"]).execute()
        group["member_count"] = len(members_response.data)
    
    # Sort groups by member count in Python (not in SQL)
    # Get top 4 groups with most members
    trending_groups = sorted(all_groups.copy(), key=lambda x: x.get("member_count", 0), reverse=True)[:4]
    
    return render(request, "groups/group_list.html", {
        "groups": all_groups,
        "trending_groups": trending_groups
    })


@login_required
@csrf_exempt
def create_group(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description", "")
        category = request.POST.get("category")
        privacy = request.POST.get("privacy")
        supabase = authenticate_with_jwt()
        user_id = supabase.table("soundscore_user") \
            .select("id") \
            .eq("username", request.user.username) \
            .execute().data[0]["id"]

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

        else:
            cover_url = "/static/images/default.jpg"  

        # Agora criamos o grupo com a URL da imagem
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
    import json as pyjson # Keep local import if preferred
    print("=== set_online_status called ===")
    print("Request method:", request.method)
    print("Request body:", request.body)
    
    try:
        data = pyjson.loads(request.body)
        print("Parsed data:", data)
    except Exception as e:
        print("Error parsing request body:", e)
        return JsonResponse({"ok": False, "error": "Invalid request body"}, status=400)

    # Get group_id
    try:
        group_id = int(data.get("group_id"))
        # print("group_id (int):", group_id) # Already have this
    except (ValueError, TypeError) as e:
        print("Invalid group_id:", e)
        return JsonResponse({"ok": False, "error": "Invalid group_id"}, status=400)

    # Get is_online - use strict boolean check
    is_online_from_request = data.get("is_online")
    if is_online_from_request is True:
        is_online_for_db = True
    else:
        is_online_for_db = False
    # print(f"is_online (STRICT bool for DB): {is_online_for_db}") # Already have this

    # Get user ID
    supabase = authenticate_with_jwt() # Ensure this is correctly configured
    if not request.user.is_authenticated: # Important check
         print("User not authenticated in set_online_status")
         return JsonResponse({"ok": False, "error": "User not authenticated"}, status=401)

    user_query = supabase.table("soundscore_user") \
        .select("id") \
        .eq("username", request.user.username) \
        .execute()
    if not user_query.data:
        print(f"User not found in Supabase: {request.user.username}")
        return JsonResponse({"ok": False, "error": "User not found"}, status=404)
        
    user_id = int(user_query.data[0]["id"])
    # print("user_id (int):", user_id) # Already have this

    # Update status in database
    # print("Upsert data:", upsert_data) # Already have this

    try:
        result = supabase.rpc("upsert_group_user_online", {
            "_group_id": group_id,
            "_user_id": user_id,
            "_is_online": is_online_for_db
        }).execute()
        print("RPC upsert result:", result) # Log the raw result

        # CRITICAL: After successful DB update, trigger a broadcast
        # Check if the RPC call was successful. This depends on your Supabase client.
        # A simple check is that no exception was raised.
        # For supabase-py, you might check result.error or result.status_code
        # Assuming no exception means success for now:
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"group_{group_id}",  # This must match the group_name in your consumer
            {
                "type": "trigger_broadcast_online_users", # A new custom message type
            }
        )
        print(f"SUCCESS: Sent trigger_broadcast_online_users to channel group: group_{group_id}")

    except Exception as e:
        print(f"ERROR: RPC upsert or channel layer send exception in set_online_status: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({"ok": False, "error": str(e)}, status=500)

    print("=== set_online_status finished ===")
    return JsonResponse({"ok": True, "status": "online" if is_online_for_db else "offline"})


