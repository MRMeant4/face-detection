import pytest
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.testing import WebsocketCommunicator

from face_detection.asgi import application
from face_detection.routing import websocket_urlpatterns


@pytest.mark.asyncio
async def test_asgi_application():
    """Test ASGI application configuration"""
    # Verify application is a ProtocolTypeRouter
    assert isinstance(application, ProtocolTypeRouter)

    # Verify WebSocket routing
    communicator = WebsocketCommunicator(application, "/faces")
    connected, _ = await communicator.connect()
    assert connected

    # Get the connection message
    response = await communicator.receive_json_from()
    assert response["type"] == "connection_established"

    await communicator.disconnect()
