import json
from unittest.mock import AsyncMock, patch

from channels.testing import WebsocketCommunicator
from django.test import TestCase

from face_detector.consumers import FaceDetectionConsumer


class FaceDetectionConsumerTests(TestCase):
    """Test cases for FaceDetectionConsumer WebSocket consumer."""

    async def test_connect(self):
        """Test that a client can connect and receives the welcome message."""
        communicator = WebsocketCommunicator(FaceDetectionConsumer.as_asgi(), "/faces")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "connection_established")
        self.assertEqual(response["message"], "Connected to face detection service")

        await communicator.disconnect()

    @patch("channels.layers.get_channel_layer")
    async def test_disconnect(self, mock_get_channel_layer):
        """Test that a client is properly removed from the group on disconnect."""
        mock_channel_layer = AsyncMock()
        mock_get_channel_layer.return_value = mock_channel_layer

        consumer = FaceDetectionConsumer()
        consumer.channel_name = "test_channel_name"
        consumer.channel_layer = mock_channel_layer

        await consumer.disconnect(1000)

        mock_channel_layer.group_discard.assert_called_once_with(
            "faces", "test_channel_name"
        )

    async def test_face_detection_notification(self):
        """Test that face detection notifications are properly sent to the client."""
        communicator = WebsocketCommunicator(FaceDetectionConsumer.as_asgi(), "/faces")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.receive_json_from()

        consumer = FaceDetectionConsumer()
        consumer.send = AsyncMock()

        event = {
            "type": "face_detection_result",
            "image_url": "http://example.com/image.jpg",
            "faces_detected": 3,
        }
        await consumer.face_detection_notification(event)
        expected_data = json.dumps(
            {
                "type": "face_detection_result",
                "image_url": "http://example.com/image.jpg",
                "faces_detected": 3,
            }
        )
        consumer.send.assert_called_once_with(text_data=expected_data)

        await communicator.disconnect()

    async def test_receive_method_does_nothing(self):
        """Test that the receive method doesn't process any messages."""
        communicator = WebsocketCommunicator(FaceDetectionConsumer.as_asgi(), "/faces")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.receive_json_from()
        await communicator.send_json_to({"type": "test_message"})
        has_response = await communicator.wait(timeout=0.1)
        self.assertFalse(has_response)

        await communicator.disconnect()
