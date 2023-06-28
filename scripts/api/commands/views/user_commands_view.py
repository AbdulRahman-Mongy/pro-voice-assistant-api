from rest_framework.generics import ListAPIView

from scripts.api.commands.serializers.CommandForTableDTOSerializer import CommandForTableDTOSerializer
from scripts.models import BaseCommand


class UserCommands(ListAPIView):
    serializer_class = CommandForTableDTOSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = BaseCommand.objects.filter(owner=self.request.user.id)
        return queryset
