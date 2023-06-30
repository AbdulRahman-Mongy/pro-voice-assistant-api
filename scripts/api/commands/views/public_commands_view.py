from rest_framework.generics import ListAPIView

from scripts.api.commands.serializers import PublicCommandSerializer
from scripts.models import BaseCommand


class PublicCommands(ListAPIView):
    serializer_class = PublicCommandSerializer
    pagination_class = None

    def get_queryset(self):
        # all public commands except the ones that the user own or used
        return BaseCommand.objects.filter(state='public')\
            .exclude(owner=self.request.user)\
            .exclude(used_by=self.request.user)
