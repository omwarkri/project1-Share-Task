from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chat.consumers import ChatConsumer
from django.core.asgi import get_asgi_application

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<task_id>\d+)/(?P<receiver_id>\d+)/$", ChatConsumer.as_asgi()),
]
# Make sure HTTP requests are handled correctly
application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Fix for handling HTTP requests
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
