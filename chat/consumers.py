# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Message


class ChatConsumer(AsyncWebsocketConsumer):

    # Called when browser connects via WebSocket
    async def connect(self):
        self.user = self.scope['user']  # logged-in user
        self.other_user_id = self.scope['url_route']['kwargs']['user_id']

        # Create a unique room name for this pair
        # e.g. user 3 and user 7 → "chat_3_7" (always sorted so it's the same either way)
        ids = sorted([self.user.id, int(self.other_user_id)])
        self.room_name = f"chat_{ids[0]}_{ids[1]}"

        # Join the room group
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()  # accept the WebSocket connection

    # Called when browser disconnects
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    # Called when browser sends a message through WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        content = data.get('message', '').strip()
        if not content:
            return

        # Save message to DB
        message = await self.save_message(content)

        # Send to everyone in the room (both users)
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_message',          # calls chat_message() below
                'message': content,
                'sender': self.user.username,
                'sender_id': self.user.id,
                'timestamp': message.timestamp.strftime('%H:%M'),
            }
        )

    # Called by group_send — sends data back to the browser
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'sender_id': event['sender_id'],
            'timestamp': event['timestamp'],
        }))

    # DB operations must be wrapped in this decorator (because DB is not async)
    @database_sync_to_async
    def save_message(self, content):
        other_user = User.objects.get(id=self.other_user_id)
        return Message.objects.create(
            sender=self.user,
            receiver=other_user,
            content=content,
        )