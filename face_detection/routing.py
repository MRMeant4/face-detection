from channels.routing import ProtocolTypeRouter, URLRouter
from face_detector.consumers import FaceDetectionConsumer
from django.urls import path

websocket_urlpatterns = [
    path(r"faces", FaceDetectionConsumer.as_asgi()),
]

application = ProtocolTypeRouter(
    {
        "websocket": URLRouter(websocket_urlpatterns),
    }
)
