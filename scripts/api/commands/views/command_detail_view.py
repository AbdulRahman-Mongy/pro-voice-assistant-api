from rest_framework import generics
from rest_framework.permissions import AllowAny
from scripts.api.commands.interfaces import build_script
from scripts.api.commands.serializers import BaseCommandDetailSerializer
from scripts.utils import FileHelper
from scripts.api.commands.utils import (
    get_related_objects,
    assign_related_objects,
    handle_command_state,
    submit_approval_request
)
from scripts.models import (
    BaseCommand,
    Patterns,
    Parameters
)


# View
class CommandDetail(generics.RetrieveUpdateAPIView):
    permission_classes = [AllowAny]
    serializer_class = BaseCommandDetailSerializer
    queryset = BaseCommand.objects.all()

    command = script_file = dependency_file = script_type = None
    rebuild = retrain = is_public = False

    def get_object(self):
        queryset = self.get_queryset()
        user = self.request.user
        command = generics.get_object_or_404(queryset, id=self.kwargs['pk'], owner=user)
        self.check_object_permissions(self.request, command)
        return command

    def put(self, request, *args, **kwargs):
        parameters, patterns = self._preprocess_request(request)
        print(self.rebuild, self.retrain)
        self.update_script() if self.rebuild else None
        response = self.update(request, *args, **kwargs)
        self._postprocess_request(parameters, patterns)
        return response

    def _preprocess_request(self, request):
        self.command = self.get_object()
        self.script_file = request.data.pop('script_data.script', [self.command.script.file])[0]
        self.dependency_file = request.data.pop('script_data.requirements', [self.command.script.dependency])[0]
        self.script_type = request.data.pop('script_data.scriptType', [self.command.script.type])[0]

        patterns = get_related_objects('patterns', request.data)
        parameters = get_related_objects('parameters', request.data)

        self._rebuild()
        self._retrain(parameters, patterns)

        self.is_public = self.command.state == 'private' and handle_command_state(request)

        return parameters, patterns

    def _rebuild(self):
        required_for_rebuild = [self.script_type, self.dependency_file, self.script_file]
        self.rebuild = any(required_for_rebuild)

    def _retrain(self, parameters, patterns):
        required_for_retrain = [parameters, patterns]
        self.retrain = any(required_for_retrain)

    def _postprocess_request(self, parameters, patterns):
        assign_related_objects(self.command, Patterns, patterns) if patterns else None
        assign_related_objects(self.command, Parameters, parameters) if parameters else None
        build_script(self.command.id, self.command.name, {
            'script': self.script_file,
            'requirements': self.dependency_file,
            'old_executable_link': self.command.executable_url
        }) if self.rebuild else None
        submit_approval_request(self.command) if self.is_public else None
        if self.retrain:
            # TODO: update when training
            pass

    def _prepare_script_data(self):
        return {
            'file': self.script_file,
            'dependency': self.dependency_file,
            'type': self.script_type,
            'name': self.script_file.name
        }

    def update_script(self):
        script_data = self._prepare_script_data()
        FileHelper.remove_files([self.command.script.file, self.command.script.dependency])
        # update method does not call file upload so I had to do it like that
        for attribute, value in script_data.items():
            setattr(self.command.script, attribute, value)
        self.command.script.save()
