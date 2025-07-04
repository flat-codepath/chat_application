"""
ASGI config for chatproject project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

# import os
# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatproject.settings')
# django_asgi_app = get_asgi_application()

# from channels.routing import ProtocolTypeRouter, URLRouter
# from chat.routing import websocket_urlpatterns

# application = ProtocolTypeRouter({
#     "http": django_asgi_app,
#     "websocket": URLRouter(websocket_urlpatterns),  # ✅ Must be here
# })

import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatproject.settings')
django.setup()

django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chat.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(  # ✅ This is the KEY
        URLRouter(websocket_urlpatterns)
    ),
})