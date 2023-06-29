from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import generics
from rest_framework.permissions import AllowAny

from scripts.models import CommandApproveRequest, BaseScript
from . import models
from . import serializers


class UserListView(generics.ListAPIView):
    queryset = models.CustomUser.objects.all()
    serializer_class = serializers.UserSerializer


@staff_member_required
def download_file(request, script_id, filename):
    script = get_object_or_404(BaseScript, id=script_id)
    file = getattr(script, filename)
    response = FileResponse(file)
    response['Content-Disposition'] = f'attachment; filename="{file.name}"'
    return response


@staff_member_required
def approval_requests(request):
    requests = CommandApproveRequest.objects.filter(status='pending')

    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        new_status = request.POST.get('new_status')

        approval_request = get_object_or_404(CommandApproveRequest, id=request_id)
        approval_request.status = new_status
        approval_request.save()

        return redirect('approval_requests')

    return render(request, 'approval_requests.html', {'requests': requests})


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
