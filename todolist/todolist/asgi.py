import os
from django.core.asgi import get_asgi_application
from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chat.consumers import ChatConsumer,TeamChatConsumer

# Set the Django settings module before importing get_asgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todolist.settings')

# Django ASGI application to handle HTTP requests
django_asgi_app = get_asgi_application()

# WebSocket URL routing
websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<task_id>\d+)/(?P<receiver_id>\d+)/$", ChatConsumer.as_asgi()),
    re_path(r"ws/team/(?P<team_id>\d+)/$", TeamChatConsumer.as_asgi()),
]

# Define the ASGI application
application = ProtocolTypeRouter({
    "http": django_asgi_app,  # Handle HTTP requests
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
