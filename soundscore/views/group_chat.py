import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from soundscore.services.user.supabase_client import authenticate_with_jwt 


class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_id = int(self.scope['url_route']['kwargs']['group_id'])
        self.group_name = f"group_{self.group_id}"
        self.user = self.scope["user"]

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        await self.set_user_online(self.user.id, self.group_id)
        await self.send_online_users()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.set_user_offline(self.user.id, self.group_id)
        await self.send_online_users()

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]

        if data.get("type") == "typing":
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "user_typing",
                    "user": self.user.username
                }
            )


        await self.save_message(self.group_id, self.user.id, message)

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat_message",
                "message": message,
                "user": self.user.username
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "user": event["user"]
        }))

    async def user_typing(self, event):
        await self.send(text_data=json.dumps({
            "type": "typing",
            "user": event["user"]
        }))


    async def send_online_users(self):
        users = await self.get_online_users(self.group_id)
        await self.send(text_data=json.dumps({
            "type": "online_users",
            "users": users  # retorna lista de user_id por enquanto
        }))

    # -----------------------------
    # SUPABASE INTEGRATIONS
    # -----------------------------

    @database_sync_to_async
    def save_message(self, group_id, user_id, content):
        supabase = authenticate_with_jwt()
        supabase.table("chat_group_message").insert({
            "group_id": group_id,
            "user_id": user_id,
            "content": content,
        }).execute()

    @database_sync_to_async
    def set_user_online(self, user_id, group_id):
        supabase = authenticate_with_jwt()
        supabase.table("chat_group_online_status").upsert({
            "group_id": group_id,
            "user_id": user_id,
            "is_online": True
        }, on_conflict=["group_id", "user_id"]).execute()

    @database_sync_to_async
    def set_user_offline(self, user_id, group_id):
        supabase = authenticate_with_jwt()
        supabase.table("chat_group_online_status").update({
            "is_online": False
        }).eq("group_id", group_id).eq("user_id", user_id).execute()

    @database_sync_to_async
    
    def get_online_users(self, group_id):
        supabase = authenticate_with_jwt()
        res = supabase.table("group_user_online_detailed") \
            .select("username") \
            .eq("group_id", group_id) \
            .eq("is_online", True) \
            .execute()
        return [row["username"] for row in res.data]
    
    @database_sync_to_async
    def get_last_seen(self, user_id, group_id):
        supabase = authenticate_with_jwt()
        res = supabase.table("chat_group_online_status") \
            .select("updated_at") \
            .eq("group_id", group_id) \
            .eq("user_id", user_id) \
            .execute()
        return res.data[0]["updated_at"] if res.data else None


