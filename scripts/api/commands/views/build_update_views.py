from scripts.api.commands.serializers.command_serializers import BaseCommandBuildSerializer
from scripts.models import BaseCommand
from scripts.api.commands.interfaces.web_socket import notify

from rest_framework import generics, status
from rest_framework.permissions import (
    AllowAny
)
from rest_framework.response import Response


class UpdateCommandAfterBuild(generics.UpdateAPIView):
    permission_classes = [AllowAny]
    serializer_class = BaseCommandBuildSerializer
    queryset = BaseCommand.objects.all()
    lookup_field = 'id'

    def put(self, request, *args, **kwargs):
        pk = kwargs.get('id')
        command = BaseCommand.objects.filter(pk=pk)
        if not command:
            return Response(status=status.HTTP_404_NOT_FOUND)
        user_id = command[0].owner.id
        notify(f'notification_{user_id}', 'send_notification', request.data)
        return self.update(request, *args, **kwargs)