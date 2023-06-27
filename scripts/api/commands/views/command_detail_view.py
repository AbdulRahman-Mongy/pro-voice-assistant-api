from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from scripts.api.commands.serializers import BaseCommandDetailSerializer
from scripts.models import BaseCommand


# View
class CommandDetail(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BaseCommandDetailSerializer
    queryset = BaseCommand.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        user = self.request.user
        command = generics.get_object_or_404(queryset, id=self.kwargs['pk'], owner=user)
        self.check_object_permissions(self.request, command)
        return command

    def partial_update(self, request, *args, **kwargs):
        # loop over request.data and the field
        print(request.data.keys())
        # TODO: require rebuild: parameters, script_data
        # TODO: require retrain: patterns, parameters
        # TODO : update fields in the db
        # TODO: Note: when updating patterns or parameters, remove all existing patterns and parameters and put the new
        # TODO: when updating script_data -> don't forget to remove the old files before saving the new infos
        return Response(status=status.HTTP_200_OK)
