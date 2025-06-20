import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from apps.groups.services.message_service import save_message, get_recent_messages
from apps.groups.services.user_status_service import set_online_status
from apps.groups.models import GroupMember
from apps.users.models import User


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

    @database_sync_to_async
    def get_user_data_by_username(self, username):
        try:
            user = User.objects.get(username=username)
            return {
                "id": user.id,
                "username": user.username,
                "profile_picture": getattr(user, "profile_picture", "/static/images/default.jpg"),
            }
        except User.DoesNotExist:
            return {}

    @database_sync_to_async
    def get_users_with_online_status(self, group_id):
        members = GroupMember.objects.filter(group_id=group_id).select_related('user')
        # If you have a GroupUserOnline model, use it here to get online status
        # Otherwise, set is_online to False or implement your own logic
        users = []
        for m in members:
            users.append({
                "username": m.user.username,
                "profile_picture": getattr(m.user, "profile_picture", "/static/images/default.jpg"),
                "is_online": False  # Replace with actual online status if implemented
            })
        return users
