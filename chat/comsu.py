import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from .models import Thread, Message
import base64
from django.core.files.base import ContentFile

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.thread_id = self.scope["url_route"]["kwargs"]["thread_id"]
        self.room_group_name = f"chat_{self.thread_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        print(message_type,'-----------')

        if message_type == 'chat_message':
            await self.handle_new_message(data)
        elif message_type == 'react':
            await self.handle_reaction(data)

    async def handle_new_message(self, data):
        text = data.get("text", "")
        files_data = data.get('files',[])
        reply_to_id = data.get("reply_to")
        sender = self.scope["user"]

        thread = await self.get_thread(self.thread_id)
        reply_to_message = await self.get_message(reply_to_id) if reply_to_id else None

        new_message = Message(thread=thread, sender=sender, text=text, reply_to=reply_to_message)

        # Handle file/image (optional)
        for file_data in files_data:
            try:
                _format, _content = file_data['content'].split(';base64,')
                decoded_file = base64.b64decode(_content)
                file_name = file_data['name']
                
                if file_data['type'].startswith('image/'):
                    new_message.image.save(file_name, ContentFile(decoded_file), save=False)
                else:
                    new_message.file.save(file_name, ContentFile(decoded_file), save=False)
            except Exception as e:
                print(f"Error handling file upload: {e}")

        await self.save_message(new_message)  # Save before using `.id` or `.timestamp`

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'broadcast_chat_message',
                'message': {
                    'id': new_message.id,
                    'sender': sender.username,
                    'text': new_message.text,
                    'reply_to': new_message.reply_to.text if new_message.reply_to else None,
                    'files': [file.url for file in new_message.files.all()] if new_message.file.exists() else None,
                    'image': new_message.image.url if hasattr(new_message, 'image') and new_message.image else None,
                    'reactions': new_message.reactions,
                    'timestamp': new_message.timestamp.strftime("%H:%M"),
                }
            }
        )

    async def handle_reaction(self, data):
        message_id = data.get("message_id")
        emoji = data.get("emoji")
        sender = self.scope["user"]

        updated_reactions = await self.update_reaction(message_id, emoji, sender.username)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'broadcast_reaction_update',
                'message_id': message_id,
                'emoji': emoji,
                'reactions': updated_reactions
            }
        )

    async def broadcast_chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message']
        }))

    async def broadcast_reaction_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'reaction_update',
            'message_id': event['message_id'],
            'emoji': event['emoji'],
            'reactions': event['reactions']
        }))

    # --- DATABASE METHODS ---

    @database_sync_to_async
    def save_message(self, message):
        message.save()

    @database_sync_to_async
    def get_thread(self, thread_id):
        return Thread.objects.get(id=thread_id)

    @database_sync_to_async
    def get_message(self, message_id):
        return Message.objects.get(id=message_id)

    @database_sync_to_async
    def update_reaction(self, message_id, emoji, username):
        message = Message.objects.get(id=message_id)
        reactions = message.reactions or {}

        users = set(reactions.get(emoji, []))
        if username in users:
            users.remove(username)
        else:
            users.add(username)

        reactions[emoji] = list(users)
        message.reactions = reactions
        message.save()
        return reactions