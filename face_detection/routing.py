from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

from face_detector.consumers import FaceDetectionConsumer

websocket_urlpatterns = [
    path(r"faces", FaceDetectionConsumer.as_asgi()),
]

application = ProtocolTypeRouter(
    {
        "websocket": URLRouter(websocket_urlpatterns),
    }
)
