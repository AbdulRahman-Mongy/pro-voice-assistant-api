from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from scripts.api.commands.serializers import InstallationCommandSerializer
from scripts.models import BaseCommand


class InstallCommand(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = BaseCommand.objects.all()
    serializer_class = InstallationCommandSerializer

    def get_object(self):
        queryset = self.get_queryset()
        command = generics.get_object_or_404(queryset, id=self.kwargs['pk'], state='public')
        return command

    def get(self, request, *args, **kwargs):
        command = self.get_object()
        user = self.request.user
        already_installed = BaseCommand.objects.filter(pk=command.id).filter(used_by__id=user.id) or False
        if not already_installed:
            command.used_by.add(user)
        return self.retrieve(request, *args, **kwargs)


class UninstallCommand(generics.DestroyAPIView):

    permission_classes = [IsAuthenticated]
    queryset = BaseCommand.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        command = generics.get_object_or_404(queryset, id=self.kwargs['pk'], state='public')
        return command

    def delete(self, request, *args, **kwargs):
        command = self.get_object()
        user = self.request.user
        already_installed = BaseCommand.objects.filter(pk=command.id).filter(used_by__id=user.id) or False
        if already_installed:
            command.used_by.remove(user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST, data={
            'msg': 'This Command is not installed'
        })
