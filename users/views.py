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
        self.create_notification(2, "This is a test notification")
        return HttpResponse("Notification sent")

    def create_notification(self, user_id, message):
        notification_data = {
            "id": 2,
            "name": "command_name",
            'status': 'success',
            'message': 'Command for the script "{script.name}" has been built successfully',
            'executable_url': "https://storage.googleapis.com/executables-ma/dist%5Copen-chrom.exe"
        }
        print(f"Sending notification to user {user_id}")
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'notification_{user_id}',
            {
                'type': 'send_notification',
                'message': notification_data
            }
        )
