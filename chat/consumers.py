import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from .models import Thread, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.thread_id = self.scope["url_route"]["kwargs"]["thread_id"]
        self.room_group_name = f"chat_{self.thread_id}"

        # Join room
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        text = data.get("text", "")
        reply_to = data.get("reply_to", None)

        user = self.scope["user"]

        # Save message
        message = await self.save_message(user, text, reply_to)

        # Broadcast
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "user": user.username,
                "text": text,
                "reply_to": reply_to,
                "timestamp": message.timestamp.strftime("%H:%M"),
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @sync_to_async
    def save_message(self, user, text, reply_to):
        reply_message = None
        if reply_to:
            reply_message = Message.objects.get(pk=reply_to)

        thread = Thread.objects.get(pk=self.thread_id)

        return Message.objects.create(thread=thread, sender=user, text=text, reply_to=reply_message)
