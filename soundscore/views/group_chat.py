import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from soundscore.services.user.supabase_client import authenticate_with_jwt
from datetime import datetime


class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_id = int(self.scope['url_route']['kwargs']['group_id'])
        self.group_name = f"group_{self.group_id}"
        self.user = self.scope["user"]

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            if "message" in data:
                message = data["message"]
                username = self.user.username

                # Get user data from Supabase using username
                user_data = await self.get_user_data_by_username(username)
                user_id = user_data.get("id") if user_data else self.user.id
                profile_pic = user_data.get("profile_picture", "/static/images/default.jpg")

                # Save message with correct user_id
                await self.save_message(self.group_id, user_id, message)

                # Broadcast to group (including sender)
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "chat_message",
                        "message": message,
                        "user": username,
                        "user_id": user_id,
                        "profile_pic": profile_pic
                    }
                )
        except Exception as e:
            import traceback
            print("Exception in receive:", e)
            print(traceback.format_exc())
            await self.send(text_data=json.dumps({
                "type": "error",
                "error": str(e)
            }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "message",
            "message": event["message"],
            "user": event["user"],
            "user_id": event["user_id"],
            "profile_pic": event.get("profile_pic", "/static/images/default.jpg")
        }))

    @database_sync_to_async
    def get_user_data_by_username(self, username):
        supabase = authenticate_with_jwt()
        result = supabase.table("soundscore_user").select("id, username, profile_picture").eq("username", username).limit(1).execute()
        if result.data and len(result.data) > 0:
            return result.data[0]
        else:
            return None

    @database_sync_to_async
    def save_message(self, group_id, user_id, content):
        supabase = authenticate_with_jwt()
        supabase.table("chat_group_message").insert({
            "group_id": group_id,
            "user_id": user_id,
            "content": content,
        }).execute()


