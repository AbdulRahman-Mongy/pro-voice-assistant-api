from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from scripts.api.commands.interfaces import (
    build_script,
    remove_executable
)
from scripts.api.commands.serializers import BaseCommandDetailSerializer
from scripts.utils import FileHelper
from scripts.api.commands.utils import (
    assign_related_objects,
    _preprocess_edit_request,
    _should_rebuild,
    _should_retrain,
    _prepare_script_data,
)
from scripts.models import (
    BaseCommand,
    Patterns,
    Parameters, CommandApproveRequest
)


class CommandDetail(generics.RetrieveUpdateDestroyAPIView):
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
        script_data, parameters, patterns = _preprocess_edit_request(request)

        response = self.update(request, *args, **kwargs)

        if self.require_review(request, _should_rebuild(script_data)):
            self.request_approval()

        if _should_rebuild(script_data):
            self.update_script(script_data)

        if _should_retrain(parameters, patterns):
            self.update_patterns(patterns)
            self.update_parameters(parameters)
            # TODO: retrain
            pass

        if request.data.get('icon') is not None:
            self.update_icon_file(request.data.get('icon'))

        return response

    def request_approval(self):
        self.command.state = 'private'
        self.command.save()
        CommandApproveRequest.objects.filter(command=self.command).delete()
        CommandApproveRequest.objects.create(
            command=self.command,
            status='pending',
        )

    def require_review(self, request, should_rebuild):
        if self.command.state == 'public' and should_rebuild:
            return True

        if request.data.get('state') is not None:
            return request.data.get('state').lower() == 'public'

        return False

    def update_parameters(self, parameters):
        assign_related_objects(self.command, Parameters, parameters) if parameters else None

    def update_patterns(self, patterns):
        assign_related_objects(self.command, Patterns, patterns) if patterns else None

    def update_script(self, script_data):
        self.update_script_files(script_data)

        build_script(self.command.id, self.command.name) if script_data else None

    def update_script_files(self, script_data):
        # update method does not call file upload, so I had to do it like that
        FileHelper.remove_files([self.command.script.file, self.command.script.dependency])
        for attribute, value in _prepare_script_data(script_data).items():
            setattr(self.command.script, attribute, value)
        self.command.script.save()

    def update_icon_file(self, icon_file):
        FileHelper.remove_files([self.command.icon])
        self.command.icon = icon_file
        self.command.save()

    def delete(self, request, *args, **kwargs):
        self.command = self.get_object()
        self.clean_before_delete()
        return self.destroy(request, *args, **kwargs)

    def clean_before_delete(self):
        remove_executable(self.command.executable_url) if self.command.executable_url else None
        FileHelper.remove_files([
            self.command.script.file,
            self.command.script.dependency,
        ])


