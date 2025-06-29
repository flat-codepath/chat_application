import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from .models import Thread, Message
import base64
from django.core.files.base import ContentFile

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.thread_id = self.scope["url_route"]["kwargs"]["thread_id"]
        print(self.scope['url_route'])
        print(self.scope['url_route']['kwargs']['thread_id'])

        self.room_group_name = f"chat_{self.thread_id}"
        print(self.channel_layer)
        print(self.channel_name,'------------------')

        # Join room
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        text = data.get("text", "")
        file_data = data.get('file') # The file data sent from JS
        reply_to = data.get("reply_to", None)

        sender = self.scope["user"]
        thread = await sync_to_async(Thread.objects.get)(id=self.thread_id)
        new_message = Message(thread=thread, sender=sender, text=text)

        # Save message
        # message = await self.save_message(user, text, reply_to)


        if file_data:
            # The file content is a Base64 encoded string with a data URI scheme
            # e.g., "data:image/png;base64,iVBORw0KGgo..."
            try:
                # 1. Split the metadata from the actual data
                _format, _content = file_data['content'].split(';base64,')
                # 2. Decode the base64 data
                decoded_file = base64.b64decode(_content)
                
                file_name = file_data['name']
                
                # 3. Save it to the appropriate model field
                #    Distinguish between images and other files based on MIME type
                if file_data['type'].startswith('image/'):
                    new_message.image.save(file_name, ContentFile(decoded_file), save=False)
                else:
                    new_message.file.save(file_name, ContentFile(decoded_file), save=False)
            
            except Exception as e:
                print(f"Error handling file: {e}")
                # Optionally handle the error, e.g., by not saving the message
                # or sending an error back to the client.


        await self.save_message(new_message)

        # Broadcast
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "user": sender.username,
                "text": text,
                "reply_to": reply_to,
                "timestamp": new_message.timestamp.strftime("%H:%M"),
                 'image_url': new_message.image.url if new_message.image else None,
                'file_url': new_message.file.url if new_message.file else None,
                'file_name': new_message.file.name.split('/')[-1] if new_message.file else None,
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @sync_to_async
    def save_message(self, message):
        message.save()