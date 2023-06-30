from rest_framework.generics import ListAPIView

from scripts.api.commands.serializers import PublicCommandSerializer
from scripts.models import BaseCommand


class InstalledCommands(ListAPIView):
    serializer_class = PublicCommandSerializer
    pagination_class = None

    def get_queryset(self):
        return BaseCommand.objects.filter(state='public')\
            .filter(used_by=self.request.user)
