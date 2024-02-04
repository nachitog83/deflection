import json
import logging
from datetime import datetime, timedelta

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from django.contrib.auth.models import AnonymousUser

from chat.exceptions import ThrottlingConfigurationError, ThrottlingError

from .models import Message, Room

logger = logging.getLogger("chat")


class MessageThrottler:
    UNITS = ["year", "month", "day", "hour", "minute", "second"]

    def __init__(self):
        amount: str = settings.DJANGO_WEBSOCKET_THROTTLE.split("/")[0]
        unit: str = settings.DJANGO_WEBSOCKET_THROTTLE.split("/")[1]

        if not amount.isdigit() or unit not in self.UNITS:
            raise ThrottlingConfigurationError(
                f"Wrong format for throttling config: {settings.DJANGO_WEBSOCKET_THROTTLE}"
            )

        self.amount = int(amount)
        self.unit = unit

        self.set_current_time()
        self.set_new_limit()

    def set_current_time(self):
        self.now = datetime.now()

    def set_new_limit(self):
        self.limit = self.now + timedelta(**{self.unit + "s": 1})
        self.count = 0

    def check_throttle(self):
        self.set_current_time()
        if self.now < self.limit and self.count >= self.amount:
            raise ThrottlingError()
        elif self.now >= self.limit:
            self.set_new_limit()
        self.count += 1


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
