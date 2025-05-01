from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from soundscore.services.user.supabase_client import authenticate_with_jwt
import uuid

@login_required
def group_chat_page(request, group_id):
    return render(request, 'groups/room.html', {
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

@csrf_exempt
def create_group(request):
    if request.method == "POST":
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

    group = supabase.table("chat_group").select("*").eq("id", group_id).execute().data[0]
    members = supabase.table("chat_group_member").select("user_id").eq("group_id", group_id).execute().data
    member_count = len(members)

    return render(request, "groups/group_room.html", {
        "group": group,
        "group_id": group_id,
        "member_count": member_count
    })


