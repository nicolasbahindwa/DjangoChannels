from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from django.core.asgi import get_asgi_application
from chatapp.consumers import EchoConsumer, ChatConsumer
from channels.auth import AuthMiddlewareStack
# from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                path('ws/chatapp/<str:username>/', ChatConsumer.as_asgi()),
                path('ws/chatapp/', EchoConsumer.as_asgi()),
            ])
        )
    )
})


# application = ProtocolTypeRouter({
#     'websocket': URLRouter([
#             # path('ws/chatapp/<str:username>/', ChatConsumer.as_asgi()),
#             path('ws/chatapp/', EchoConsumer),
#         ])

# })



