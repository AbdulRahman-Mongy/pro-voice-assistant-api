from rest_framework.generics import ListAPIView

from scripts.api.commands.serializers import CommandForTableSerializer
from scripts.models import BaseCommand


class UserCommands(ListAPIView):
    serializer_class = CommandForTableSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = BaseCommand.objects.filter(owner=self.request.user.id)
        return queryset
