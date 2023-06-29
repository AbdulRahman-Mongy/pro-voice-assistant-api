from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from scripts.api.commands.serializers import InstallationCommandSerializer
from scripts.models import BaseCommand


class InstallCommand(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = BaseCommand.objects.all()
    serializer_class = InstallationCommandSerializer

    def get_object(self):
        queryset = self.get_queryset()
        user = self.request.user
        command = generics.get_object_or_404(queryset, id=self.kwargs['pk'], state='public')
        command.used_by.add(user)
        return command
