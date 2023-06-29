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
    Parameters, CommandApproveRequest
)


# View
def _preprocess_request(request):
    script_data = parameters = patterns = None

    if request.data.get('script_data') is not None:
        script_data = {
            "script_file": request.data.get('script_data.scriptFile')[0],
            "dependency_file": request.data.get('script_data.requirements')[0],
            "script_type": request.data.get('script_data.scriptType')[0]
        }

    if request.data.get('parameters') is not None:
        parameters = get_related_objects('parameters', request.data)

    if request.data.get('patterns') is not None:
        patterns = get_related_objects('patterns', request.data)

    return script_data, parameters, patterns


def _should_rebuild(script_data):
    return script_data is not None


def _should_retrain(parameters, patterns):
    required_for_retrain = [parameters, patterns]
    return any(required_for_retrain)


def _prepare_script_data(script_data):
    return {
        'file': script_data.script_file,
        'dependency': script_data.dependency_file,
        'type': script_data.script_type,
        'name': script_data.script_file.name
    }


class CommandDetail(generics.RetrieveUpdateAPIView):
    permission_classes = [AllowAny]
    serializer_class = BaseCommandDetailSerializer
    queryset = BaseCommand.objects.all()

    command = None

    def get_object(self):
        queryset = self.get_queryset()
        user = self.request.user
        command = generics.get_object_or_404(queryset, id=self.kwargs['pk'], owner=user)
        self.check_object_permissions(self.request, command)
        return command

    def put(self, request, *args, **kwargs):
        self.command = self.get_object()
        script_data, parameters, patterns = _preprocess_request(request)

        _should_retrain(parameters, patterns)
        is_public = request.data.get('state', ['private'])[0].lower() == 'public'

        # update command
        response = self.update(request, *args, **kwargs)

        if is_public:
            self.command.state = 'private'
            self.command.save()
            CommandApproveRequest.objects.filter(command=self.command).delete()
            CommandApproveRequest.objects.create(
                command=self.command,
                status='pending',
            )

        if _should_rebuild(script_data):
            self.update_script_files(script_data)

        if _should_retrain(parameters, patterns):
            # TODO: retrain
            pass

        if request.data.get('icon') is not None:
            self.update_icon_file(request.data.get('icon')[0])

        self._postprocess_request(script_data, parameters, patterns)
        return response

    def _postprocess_request(self, script_data, parameters, patterns):
        assign_related_objects(self.command, Patterns, patterns) if patterns else None
        assign_related_objects(self.command, Parameters, parameters) if parameters else None

        build_script(self.command.id, self.command.name, {
            'script': script_data.script_file,
            'requirements': script_data.dependency_file,
            'old_executable_link': self.command.executable_url
        }) if script_data else None

    def update_script_files(self, script_data):
        FileHelper.remove_files([self.command.script.file, self.command.script.dependency])
        # update method does not call file upload so I had to do it like that
        for attribute, value in _prepare_script_data(script_data).items():
            setattr(self.command.script, attribute, value)
        self.command.script.save()

    def update_icon_file(self, icon_file):
        FileHelper.remove_files([self.command.icon])
        self.command.icon = icon_file
        self.command.save()
