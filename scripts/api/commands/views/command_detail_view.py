from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from scripts.api.commands.serializers import BaseCommandDetailSerializer
from scripts.models import BaseCommand


# View
class CommandDetail(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BaseCommandDetailSerializer
    queryset = BaseCommand.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        user = self.request.user
        command = generics.get_object_or_404(queryset, id=self.kwargs['pk'], owner=user)
        self.check_object_permissions(self.request, command)
        return command
