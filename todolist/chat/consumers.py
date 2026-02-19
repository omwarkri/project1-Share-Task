import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.exceptions import ObjectDoesNotExist
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract task_id and receiver_id from URL parameters
        self.task_id = self.scope["url_route"]["kwargs"].get("task_id")
        self.receiver_id = self.scope["url_route"]["kwargs"].get("receiver_id")

        if not self.task_id or not self.receiver_id:
            await self.close()
            return

        # Create room_name for grouping WebSocket connections
        self.room_name = f"chat_{self.task_id}"
                
        print(f"✅ WebSocket connected: User { self.receiver_id} joined {self.room_name}")
        # Add user to the WebSocket group
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Ensure room_name exists before using it
        if hasattr(self, "room_name"):
            await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "").strip()
        sender_id = self.user.id

        if message:
            from .models import Message
            from django.contrib.auth import get_user_model

            User = get_user_model()

            try:
                receiver = await User.objects.aget(id=self.receiver_id)
                msg = await Message.objects.acreate(sender_id=sender_id, receiver=receiver, content=message)

                # Broadcast message
                await self.channel_layer.group_send(
                    self.room_name,
                    {
                        "type": "chat_message",
                        "message": msg.content,
                        "sender_id": sender_id,
                        "receiver_id": self.receiver_id,
                        "timestamp": msg.timestamp.isoformat(),
                        "attachment": msg.attachment.url if msg.attachment else None
                    }
                )
            except ObjectDoesNotExist:
                print(f"Receiver with ID {self.receiver_id} does not exist.")

    async def chat_message(self, event):
        """ Sends message to the receiver """
        print(event)
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
            "receiver": event["receiver"],
            "timestamp": event["timestamp"],
            "attachment": event["attachment"]
        }))


import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from asgiref.sync import sync_to_async
from .models import TeamChat
from user.models import CustomUser
from task.models import Team

class TeamChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.team_id = self.scope["url_route"]["kwargs"]["team_id"]
        self.room_group_name = f"team_chat_{self.team_id}"

        print(self.room_group_name, "group name")

        # Join team chat room
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave team chat room
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "")
        attachment_url = data.get("attachment", None)
        user = self.scope["user"]

        if isinstance(user, AnonymousUser):
            return

        sender = user.username
        team = await sync_to_async(Team.objects.get)(id=self.team_id)
        sender_user = await sync_to_async(CustomUser.objects.get)(username=sender)

        # Save message to database (handle attachment separately)
        new_message = await sync_to_async(TeamChat.objects.create)(
            team=team,
            sender=sender_user,
            message=message,
            attachment=attachment_url if attachment_url else None,
        )

        # Send message to WebSocket group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "team_chat_message",
                "message": new_message.message,
                "sender": sender,
                "created_at": "just now",
                "attachment": new_message.attachment.url if new_message.attachment else None,
            }
        )

    async def team_chat_message(self, event):
        # Send message to WebSocket client
        await self.send(text_data=json.dumps(event))


