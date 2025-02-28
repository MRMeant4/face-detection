import json
from channels.generic.websocket import AsyncWebsocketConsumer


class FaceDetectionConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time face detection notifications.
    """

    async def connect(self):
        """Handle connection setup for a new WebSocket client."""
        await self.channel_layer.group_add("faces", self.channel_name)
        await self.accept()
        await self.send(
            text_data=json.dumps(
                {
                    "type": "connection_established",
                    "message": "Connected to face detection service",
                }
            )
        )

    async def disconnect(self, close_code):
        """Handle disconnection of a WebSocket client."""
        await self.channel_layer.group_discard("faces", self.channel_name)

    async def receive(self, text_data):
        """Handle messages from WebSocket clients."""
        # Not expecting messages from clients for this application
        pass

    async def face_detection_notification(self, event):
        """Send face detection results to the WebSocket client."""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "face_detection_result",
                    "image_url": event["image_url"],
                    "faces_detected": event["faces_detected"],
                }
            )
        )
