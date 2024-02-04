import asyncio
from unittest.mock import patch

from channels.auth import AuthMiddlewareStack
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.conf import settings
from django.test import TransactionTestCase, override_settings

from chat.routing import websocket_urlpatterns
from chat.tests.factories import RoomFactory
from core.tests.factories import UserFactory


class TestThrottle(TransactionTestCase):
    def setUp(self):
        self.old_channel_layers = settings.CHANNEL_LAYERS
        settings.CHANNEL_LAYERS["default"] = {"BACKEND": "channels.layers.InMemoryChannelLayer"}

        self.user = UserFactory()
        self.room = RoomFactory()

    def tearDown(self):
        settings.CHANNEL_LAYERS = self.old_channel_layers

    @override_settings(WEBSOCKET_THROTTLE="1/minute")
    @patch("chat.consumers.logger")
    async def test_throttle_messages(self, mock_logger):
        communicator = WebsocketCommunicator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
            f"ws/chat/{self.room.slug}/",
        )
        # Log user manually
        communicator.scope["user"] = self.user

        connected, _ = await communicator.connect()

        assert connected
        # Test sending text
        for msg in ["message 1", "message 2"]:
            await communicator.send_json_to(msg)

        await asyncio.sleep(0.1)

        mock_logger.warning.assert_called_with(f"User {self.user.username} has reached 1 messages per minute")

        # Close
        await communicator.disconnect()

    @override_settings(WEBSOCKET_THROTTLE="1/second")
    @patch("chat.consumers.logger")
    async def test_avoid_throttling_messages(self, mock_logger):
        communicator = WebsocketCommunicator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
            f"ws/chat/{self.room.slug}/",
        )
        # Log user manually
        communicator.scope["user"] = self.user

        connected, _ = await communicator.connect()

        assert connected
        # Test sending text
        for msg in ["message 1", "message 2"]:
            await communicator.send_json_to(msg)
            await asyncio.sleep(1)

        await asyncio.sleep(0.1)

        assert not mock_logger.warning.called

        # Close
        await communicator.disconnect()
