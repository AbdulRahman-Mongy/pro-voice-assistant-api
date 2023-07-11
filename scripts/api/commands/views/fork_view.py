from scripts.models import (
    BaseCommand,
    Patterns,
    Parameters
)
from scripts.api.commands.utils import (
    copy_obj, add_command_to_nlp
)
from scripts.utils import FileHelper
from scripts.api.commands.interfaces import (
    build_script
)
from django.db.models import Q

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class ForkCommands(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    patterns = parameters = script = command = forked_command = icon = None

    def get_queryset(self):
        if self.request.user.is_staff:
            return BaseCommand.objects.all()
        domain = Q(owner=self.request.user.id) | Q(state='public')
        queryset = BaseCommand.objects.filter(domain)
        return queryset

    def post(self, request, *args, **kwargs):
        id_ = kwargs.get('id', 0)
        queryset = self.get_queryset()
        self.command = generics.get_object_or_404(queryset, id=id_)
        self._preprocess_command()
        self.fork_command()
        self._postprocess_command()
        return Response(status=status.HTTP_201_CREATED, data={'id': self.forked_command.id})

    def _preprocess_command(self):
        file = FileHelper.copy_file(self.command.script.file)
        dependency = FileHelper.copy_file(self.command.script.dependency)
        self.icon = FileHelper.copy_file(self.command.icon)
        self.script = copy_obj(self.command.script,
                               owner=self.request.user,
                               file=file,
                               dependency=dependency)
        self.parameters = Parameters.objects.filter(command=self.command)
        self.patterns = Patterns.objects.filter(command=self.command)

    def fork_command(self):
        self.forked_command = copy_obj(self.command,
                                       owner=self.request.user,
                                       script=self.script,
                                       icon=self.icon,
                                       state='private')

    def _postprocess_command(self):
        for pattern in self.patterns:
            copy_obj(pattern, command=self.forked_command)
        for parameter in self.parameters:
            copy_obj(parameter, command=self.forked_command)
        build_script(self.forked_command.id, self.forked_command.name)
        add_command_to_nlp(self.forked_command)
