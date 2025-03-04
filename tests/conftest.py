import os
import pytest
import pytest_asyncio
from django.conf import settings
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from django.core.files.uploadedfile import SimpleUploadedFile
from collections.abc import AsyncGenerator
from face_detection.asgi import application

from face_detection.routing import websocket_urlpatterns


@pytest.fixture(scope="session")
def django_db_setup():
    """Setup database configuration for tests"""
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }


@pytest.fixture
def temp_media_root(tmpdir):
    """Create a temporary media root directory for tests"""
    temp_dir = tmpdir.mkdir("media")
    original_media_root = settings.MEDIA_ROOT
    settings.MEDIA_ROOT = str(temp_dir)

    # Create required subdirectories
    os.makedirs(os.path.join(temp_dir, "processed"), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, "uploaded"), exist_ok=True)

    yield str(temp_dir)

    settings.MEDIA_ROOT = original_media_root


@pytest.fixture
def sample_image():
    """Create a simple test image file"""
    return SimpleUploadedFile(
        name="test_image.jpg",
        content=open("tests/face_detector/testdata/face1.jpg", "rb").read(),
        content_type="image/jpeg",
    )


@pytest.fixture
def non_image_file():
    """Create a non-image file for testing validation"""
    return SimpleUploadedFile(
        name="test_file.txt",
        content=b"This is not an image file",
        content_type="text/plain",
    )


@pytest_asyncio.fixture
async def websocket_communicator() -> AsyncGenerator[WebsocketCommunicator, None]:
    """Create a test WebSocket communicator"""
    communicator = WebsocketCommunicator(URLRouter(websocket_urlpatterns), "/faces")
    connected, _ = await communicator.connect()
    assert connected
    yield communicator
    await communicator.disconnect()


@pytest.fixture(scope="session", autouse=True)
def configure_settings():
    """Configure settings for tests"""
    settings.CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [("0.0.0.0", 6379)],
            },
        },
    }
