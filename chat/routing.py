# chat/routing.py
from django.urls import re_path
from . import consumers

# Just like urls.py, but for WebSocket connections
websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<user_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
]
# ws/chat/5/ → connects to chat with user id=5