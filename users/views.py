from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import HttpResponse
from rest_framework import generics
from rest_framework.permissions import AllowAny

from . import models
from . import serializers


class UserListView(generics.ListAPIView):
    queryset = models.CustomUser.objects.all()
    serializer_class = serializers.UserSerializer


# TODO: remove after integration
class TestNotifications(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        self.create_notification(1, "This is a test notification")
        return HttpResponse("Notification sent")

    def create_notification(self, user_id, message):
        notification_data = {
            'message': message
        }
        print(f"Sending notification to user {user_id}")
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'notification_{user_id}',
            {
                'type': 'send_notification',
                'notification': notification_data
            }
        )