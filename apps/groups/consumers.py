import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from apps.groups.services.message_service import save_message, get_recent_messages
from apps.groups.services.user_status_service import set_online_status
from apps.users.services.supabase_client import authenticate_with_jwt


class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_id = int(self.scope['url_route']['kwargs']['group_id'])
        self.group_name = f"group_{self.group_id}"
        self.user = self.scope["user"]

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        await database_sync_to_async(set_online_status)(self.user.username, self.group_id, True)
        await self.broadcast_online_users()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await database_sync_to_async(set_online_status)(self.user.username, self.group_id, False)
        await self.broadcast_online_users()

    async def receive(self, text_data):
        data = json.loads(text_data)

        if "message" in data:
            message = data["message"]
            username = self.user.username

            user_data = await database_sync_to_async(self.get_user_data_by_username)(username)
            user_id = user_data.get("id")
            profile_pic = user_data.get("profile_picture", "/static/images/default.jpg")

            await database_sync_to_async(save_message)(self.group_id, user_id, message)

            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "user": username,
                    "user_id": user_id,
                    "profile_pic": profile_pic,
                }
            )

        elif data.get("refresh_user"):
            await self.broadcast_online_users()

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "message",
            "message": event["message"],
            "user": event["user"],
            "user_id": event["user_id"],
            "profile_pic": event.get("profile_pic"),
        }))

    async def broadcast_online_users(self):
        users_with_status = await database_sync_to_async(self.get_users_with_online_status)(self.group_id)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "online_users",
                "users": users_with_status,
            }
        )

    async def online_users(self, event):
        await self.send(text_data=json.dumps({
            "type": "online_users",
            "users": event["users"],
        }))

    async def trigger_broadcast_online_users(self, event):
        await self.broadcast_online_users()

    # Helpers que acessam Supabase
    @database_sync_to_async
    def get_user_data_by_username(self, username):
        supabase = authenticate_with_jwt()
        result = supabase.table("soundscore_user") \
            .select("id, username, profile_picture") \
            .eq("username", username).limit(1).execute()
        return result.data[0] if result.data else {}

    @database_sync_to_async
    def get_users_with_online_status(self, group_id):
        supabase = authenticate_with_jwt()

        members_response = supabase.table("chat_group_member") \
            .select("user_id, soundscore_user(username, profile_picture)") \
            .eq("group_id", group_id).execute().data

        online_response = supabase.table("group_user_online") \
            .select("user_id, is_online") \
            .eq("group_id", group_id).execute().data

        online_map = {item["user_id"]: item["is_online"] for item in online_response}

        users = []
        for m in members_response:
            users.append({
                "username": m.get("soundscore_user", {}).get("username", "Unknown"),
                "profile_picture": m.get("soundscore_user", {}).get("profile_picture", "/static/images/default.jpg"),
                "is_online": online_map.get(m["user_id"], False)
            })
        return users
