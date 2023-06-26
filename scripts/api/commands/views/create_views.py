from scripts.api.commands.serializers import (
    BaseCommandSerializer
)
from scripts.models import (
    BaseCommand,
    BaseScript,
    Patterns,
    Parameters
)

from scripts.api.commands.utils import (
    get_related_objects,
    assign_related_objects
)

from scripts.utils import FileHelper
from scripts.api.commands.interfaces.executable_builder import build_script

from rest_framework import generics
from rest_framework.permissions import (
    IsAuthenticated
)


class CreateCommands(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = BaseCommand.objects.all()
    serializer_class = BaseCommandSerializer

    command = script_file = dependency_file = script_type = None

    def perform_create(self, serializer):
        script = self.create_script()
        self.command = serializer.save(owner=self.request.user, script=script)

    def post(self, request, *args, **kwargs):
        self.script_file = request.data.pop('script_data.script', [FileHelper.get_file_from_request('script')])[0]
        self.dependency_file = \
            request.data.pop('script_data.requirements', [FileHelper.get_file_from_request('requirements')])[0]
        self.script_type = request.data.pop('script_data.scriptType', ['py'])[0]

        patterns = get_related_objects('patterns', request.data)
        parameters = get_related_objects('parameters', request.data)

        response = super(CreateCommands, self).post(request, *args, **kwargs)

        assign_related_objects(self.command, Patterns, patterns)
        assign_related_objects(self.command, Parameters, parameters)

        build_script(self.command.id, self.command.name, {
            'script': self.script_file,
            'requirements': self.dependency_file
        })

        return response

    def create_script(self):
        script_data = self._prepare_script_data()
        script = BaseScript.objects.create(**script_data)
        return script

    def _prepare_script_data(self):
        return {
            'file': self.script_file,
            'dependency': self.dependency_file,
            'type': self.script_type,
            'owner': self.request.user,
            'name': self.script_file.name
        }
