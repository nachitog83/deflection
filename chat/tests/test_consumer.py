import json

from asgiref.sync import sync_to_async
from channels.auth import AuthMiddlewareStack
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.conf import settings
from django.test import TransactionTestCase

from chat.models import Message
from chat.routing import websocket_urlpatterns
from chat.tests.factories import RoomFactory
from core.tests.factories import UserFactory


class TestConsumer(TransactionTestCase):
    def setUp(self):
        self.old_channel_layers = settings.CHANNEL_LAYERS
        settings.CHANNEL_LAYERS["default"] = {"BACKEND": "channels.layers.InMemoryChannelLayer"}

        self.user = UserFactory()
        self.room = RoomFactory()

    def tearDown(self):
        settings.CHANNEL_LAYERS = self.old_channel_layers

    async def test_consumer_disconnect_anonymous_user(self):
        communicator = WebsocketCommunicator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns)), f"ws/chat/{self.room.slug}/"
        )
        connected, _ = await communicator.connect()

        assert not connected

    async def test_consumer_disconnect_non_existent_room(self):
        communicator = WebsocketCommunicator(AuthMiddlewareStack(URLRouter(websocket_urlpatterns)), "ws/chat/no_room/")
        # Log user manually
        communicator.scope["user"] = self.user

        connected, _ = await communicator.connect()

        assert not connected

    async def test_send_and_save_message(self):
        @sync_to_async
        def get_messages_count(room, content):
            return Message.objects.filter(room=room, content=content).count()

        communicator = WebsocketCommunicator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
            f"ws/chat/{self.room.slug}/",
        )
        # Log user manually
        communicator.scope["user"] = self.user

        connected, _ = await communicator.connect()

        assert connected
        # Test sending text
        msg = "dummy message"
        await communicator.send_json_to(msg)

        # Check message is sent

        response = await communicator.receive_from()
        assert json.loads(response) == {"message": '"dummy message"'}

        # Check message is saved to db

        messages = await get_messages_count(self.room, json.loads(response)["message"])
        assert messages == 1

        # Close
        await communicator.disconnect()
