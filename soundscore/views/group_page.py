from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from soundscore.services.user.supabase_client import authenticate_with_jwt
import uuid

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


from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

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


def group_room(request, group_id):
    supabase = authenticate_with_jwt()
    user_id = request.user.id

    # Auto-join the user to the group if not already a member
    existing = supabase.table("chat_group_member").select("*") \
        .eq("group_id", group_id) \
        .eq("user_id", user_id) \
        .execute()
    
    if not existing.data:
        supabase.table("chat_group_member").insert({
            "group_id": group_id,
            "user_id": user_id
        }).execute()

    # Get group details
    group = supabase.table("chat_group").select("*").eq("id", group_id).execute().data[0]
    
    # Get all members
    members = supabase.table("chat_group_member").select("user_id").eq("group_id", group_id).execute().data
    member_count = len(members)
    
    # Get online members
    online_members = supabase.table("group_user_online_detailed") \
        .select("username") \
        .eq("group_id", group_id) \
        .eq("is_online", True) \
        .execute().data
    
    # Get recent messages - without ordering by created_at
    recent_messages = supabase.table("chat_group_message") \
        .select("*, soundscore_user(username)") \
        .eq("group_id", group_id) \
        .limit(50) \
        .execute().data
    
    # Format messages for template - update to match the new structure
    formatted_messages = []
    for msg in recent_messages:
        username = msg["soundscore_user"]["username"] if "soundscore_user" in msg else "Unknown User"
        formatted_messages.append({
            "content": msg["content"],
            "username": username,
            "created_at": msg["created_at"],
            "user_id": msg["user_id"]
        })
    
    formatted_messages.reverse()  # Show oldest messages first
    
    return render(request, "groups/group_room.html", {
        "group": group,
        "group_id": group_id,
        "member_count": member_count,
        "online_members": online_members,
        "recent_messages": formatted_messages
    })


@login_required
def join_group(request, group_id):
    """Add the current user to a group if not already a member"""
    user_id = request.user.id
    
    # Check if the user is already a member
    supabase = authenticate_with_jwt()
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


