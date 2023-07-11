# routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/notifications/(?P<user_id>\d+)/$', consumers.NotificationConsumer.as_asgi()),
    re_path(r'ws/rasa/notifications/(?P<user_id>\d+)/$', consumers.RasaNotificationConsumer.as_asgi()),
]
