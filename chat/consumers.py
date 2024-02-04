import json
import logging

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

from chat.exceptions import ThrottlingError
from chat.services import MessageThrottler

from .models import Message, Room

logger = logging.getLogger("chat")


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        self.user = self.scope["user"]
        self.room = await self.retrieve_room(self.room_name)

        if isinstance(self.user, AnonymousUser) or not self.room:
            await self.close()

        # Join room group

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        self.throttler = MessageThrottler()

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        try:
            self.throttler.check_throttle()
        except ThrottlingError:
            logger.warning(
                f"User {self.user.username} has reached {self.throttler.amount} messages per {self.throttler.unit}"
            )
            return

        logger.info(f"Room: {self.room.slug} - User: {self.user.username} - Message: {text_data}")

        await self.save_message(text_data)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": text_data,
            },
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                }
            )
        )

    @sync_to_async
    def save_message(self, message):
        Message.objects.create(user=self.user, room=self.room, content=message)

    @sync_to_async
    def retrieve_room(self, room_name):
        return Room.objects.filter(slug=room_name).first()
