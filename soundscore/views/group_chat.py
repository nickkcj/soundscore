import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from soundscore.services.user.supabase_client import authenticate_with_jwt
from datetime import datetime, timedelta
from django.utils.timezone import now


class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_id = int(self.scope['url_route']['kwargs']['group_id'])
        self.group_name = f"group_{self.group_id}"
        self.user = self.scope["user"]

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Mark user as online
        await self.set_online_status(self.user.id, self.group_id, True)

        # Broadcast updated online users list
        await self.broadcast_online_users()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

        # Mark user as offline
        await self.set_online_status(self.user.id, self.group_id, False)

        # Broadcast updated online users list
        await self.broadcast_online_users()

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
            elif data.get("refresh_user"):
                await self.broadcast_online_users()
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

    async def broadcast_online_users(self):
        """
        Fetches all users in the group with their online status and broadcasts.
        """
        print(f"CONSUMER: Broadcasting online users for group {self.group_id}")
        # Ensure you have a method that returns the correct data structure
        # e.g., [{"username": "user1", "is_online": True, "profile_picture": "..."}, ...]
        users_with_status = await self.get_users_with_online_status(self.group_id) # Renamed for clarity
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "online_users", # This type is handled by frontend JS
                "users": users_with_status,
            }
        )

    async def online_users(self, event):
        """
        Sends the list of online users to the client that is part of this consumer instance.
        """
        print(f"CONSUMER: Sending online_users event to client: {event['users']}")
        await self.send(text_data=json.dumps({
            "type": "online_users", # Must match what frontend expects
            "users": event["users"],
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

    @database_sync_to_async
    def set_online_status(self, user_id, group_id, is_online):
        """
        Updates the user's online status in the database for a specific group.
        This is called by the consumer's connect/disconnect.
        """
        print(f"CONSUMER: Internal set_online_status via RPC: user_id={user_id}, group_id={group_id}, is_online={is_online}")
        supabase = authenticate_with_jwt()
        try:
            supabase.rpc("upsert_group_user_online", {
                "_group_id": group_id,
                "_user_id": user_id,
                "_is_online": is_online
            }).execute()
        except Exception as e:
            print(f"CONSUMER: Error in internal set_online_status RPC call: {e}")

    @database_sync_to_async
    def get_users_with_online_status(self, group_id): # Renamed for clarity
        """
        Fetches all members of the group and their current online status.
        """
        print(f"CONSUMER: Fetching users with online status for group {group_id}")
        supabase = authenticate_with_jwt()
        
        members_response = supabase.table("chat_group_member") \
            .select("user_id, soundscore_user(username, profile_picture)") \
            .eq("group_id", group_id).execute()
        
        if not members_response.data:
            print(f"CONSUMER: No members found for group {group_id}")
            return []

        member_details_map = {
            m["user_id"]: {
                "username": m["soundscore_user"]["username"] if m.get("soundscore_user") else "Unknown User",
                "profile_picture": m["soundscore_user"].get("profile_picture", "/static/images/default.jpg") if m.get("soundscore_user") else "/static/images/default.jpg"
            } for m in members_response.data
        }

        online_status_response = supabase.table("group_user_online") \
            .select("user_id, is_online") \
            .eq("group_id", group_id) \
            .in_("user_id", list(member_details_map.keys())) \
            .execute()
            
        online_status_map = {row["user_id"]: row["is_online"] for row in online_status_response.data}
        
        users_list = []
        for user_id, details in member_details_map.items():
            users_list.append({
                "username": details["username"],
                "profile_picture": details["profile_picture"], # Frontend might use this
                "is_online": online_status_map.get(user_id, False) # Default to False
            })
        print(f"CONSUMER: Fetched users for broadcast: {users_list}")
        return users_list

    # NEW HANDLER for the trigger message from the HTTP view
    async def trigger_broadcast_online_users(self, event):
        """
        Handles a message from the channel layer (sent by the HTTP view)
        to re-broadcast the online users list.
        """
        print(f"CONSUMER: Received trigger_broadcast_online_users event for group {self.group_id}. Broadcasting now.")
        await self.broadcast_online_users()


