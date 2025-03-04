from .settings import *
import tempfile

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("0.0.0.0", 6379)],
        },
    },
}


MEDIA_ROOT = tempfile.mkdtemp()

THROTTLE_RATES = {
    "user": None,
    "anon": None,
}

MIDDLEWARE = [m for m in MIDDLEWARE if not m.endswith("CsrfViewMiddleware")]
