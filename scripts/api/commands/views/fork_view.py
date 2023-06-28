from scripts.api.commands.serializers.command_serializers import BaseCommandCopySerializer
from scripts.models import (
    BaseCommand,
    Patterns,
    Parameters
)
from django.db.models import Q

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class ForkCommands(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BaseCommandCopySerializer
    queryset = BaseCommand.objects.all()

    def get_queryset(self):
        if self.request.user.is_staff:
            return BaseCommand.objects.all()
        domain = Q(owner=self.request.user.id) | Q(state='public')
        queryset = BaseCommand.objects.filter(domain)
        return queryset

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('id')
        command = self.queryset.get(pk=pk)
        fork_command = self.get_forked_command(command, request, *args, **kwargs)
        serializer = BaseCommandCopySerializer(fork_command, many=False)
        return Response(serializer.data)

    def get_forked_command(self, command, request, *args, **kwargs):
        owner = self.request.user
        # django trick to duplicate objects
        script = command.script
        script.pk = None
        script.owner = owner
        script.save()
        created_command = BaseCommand.objects.get(pk=command.pk)
        created_command.pk = None
        created_command.owner = owner
        created_command.script = script
        created_command.save()

        parameters = Parameters.objects.filter(command=command.id)
        patterns = Patterns.objects.filter(command=command.id)
        for param in parameters:
            param.pk = None
            param.command = created_command
            param.save()
        for pattern in patterns:
            pattern.pk = None
            pattern.command = created_command
            pattern.save()
        return created_command
