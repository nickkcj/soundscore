import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from apps.groups.services.message_service import save_message, get_recent_messages
from apps.groups.services.user_status_service import is_user_online, set_online_status
from apps.groups.models import GroupMember
from apps.users.models import User

class GroupChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for group chat functionality.
    Handles connecting/disconnecting users, receiving/sending messages,
    and broadcasting online user status in real time.
    """

    async def connect(self):
        """
        Called when a WebSocket connection is opened.
        Adds the user to the group channel and marks them as online.
        """
        self.group_id = int(self.scope['url_route']['kwargs']['group_id'])
        self.group_name = f"group_{self.group_id}"
        self.user = self.scope["user"]

        # Add this connection to the group channel
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Set user as online and broadcast updated online users
        await database_sync_to_async(set_online_status)(self.user.username, self.group_id, True)
        await self.broadcast_online_users()

    async def disconnect(self, close_code):
        """
        Called when the WebSocket connection is closed.
        Removes the user from the group channel and marks them as offline.
        """
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await database_sync_to_async(set_online_status)(self.user.username, self.group_id, False)
        await self.broadcast_online_users()

    async def receive(self, text_data):
        """
        Called when a message is received from the WebSocket.
        Handles chat messages and requests to refresh online users.
        """
        data = json.loads(text_data)

        if "message" in data:
            # Handle a new chat message
            message = data["message"]
            username = self.user.username

            # Get user data for the sender
            user_data = await self.get_user_data_by_username(username)
            user_id = user_data.get("id")
            profile_pic = user_data.get("profile_picture", "/static/images/default.jpg")

            # Save the message to the database
            await database_sync_to_async(save_message)(self.group_id, user_id, message)

            # Broadcast the message to all group members
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
            # Handle request to refresh online users
            await self.broadcast_online_users()

    async def chat_message(self, event):
        """
        Handler for broadcasting chat messages to WebSocket clients.
        """
        await self.send(text_data=json.dumps({
            "type": "message",
            "message": event["message"],
            "user": event["user"],
            "user_id": event["user_id"],
            "profile_pic": event.get("profile_pic"),
        }))

    async def broadcast_online_users(self):
        """
        Broadcast the current list of online users to the group.
        """
        users_with_status = await self.get_users_with_online_status(self.group_id)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "online_users",
                "users": users_with_status,
            }
        )

    async def online_users(self, event):
        """
        Handler for sending the online users list to WebSocket clients.
        """
        await self.send(text_data=json.dumps({
            "type": "online_users",
            "users": event["users"],
        }))

    async def trigger_broadcast_online_users(self, event):
        """
        Handle the broadcast trigger from Redis status updates.
        """
        await self.broadcast_online_users()

    @database_sync_to_async
    def get_user_data_by_username(self, username):
        """
        Helper to get user data (id, username, profile picture) by username.
        """
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
        """
        Helper to get all group members and their Redis-based online status.
        """
        from apps.groups.models import GroupMember
        
        members = GroupMember.objects.filter(group_id=group_id).select_related('user')
        users = []
        for m in members:
            users.append({
                "username": m.user.username,
                "profile_picture": getattr(m.user, "profile_picture", "/static/images/default.jpg"),
                "is_online": is_user_online(m.user.username, group_id)  # Now uses Redis
            })
        return users
