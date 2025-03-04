import tempfile

from .settings import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}


MEDIA_ROOT = tempfile.mkdtemp()

THROTTLE_RATES = {
    "user": None,
    "anon": None,
}

MIDDLEWARE = [m for m in MIDDLEWARE if not m.endswith("CsrfViewMiddleware")]
