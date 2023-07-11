from django.db.models import Q
from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated

from scripts.api.commands.interfaces import build_script
from scripts.api.commands.serializers import BaseCommandSerializer
from scripts.api.commands.utils import get_related_objects, assign_related_objects, handle_command_state, \
    submit_approval_request, add_command_to_nlp
from scripts.models import BaseCommand, BaseScript, Patterns, Parameters
from scripts.utils import FileHelper


class Commands(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BaseCommandSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    command = script_file = dependency_file = script_type = None

    def get_queryset(self):
        if self.request.user.is_staff:
            return BaseCommand.objects.all()
        domain = Q(owner=self.request.user.id) | Q(state='public')
        queryset = BaseCommand.objects.filter(domain)
        return queryset

    def post(self, request, *args, **kwargs):
        parameters, patterns = self._preprocess_request(request)
        is_public = handle_command_state(request)
        response = super(Commands, self).post(request, *args, **kwargs)
        self._postprocess_request(parameters, patterns)
        if is_public:
            submit_approval_request(self.command)
        return response

    def perform_create(self, serializer):
        script = self.create_script()
        self.command = serializer.save(owner=self.request.user, script=script)

    def _preprocess_request(self, request):
        self.script_file = request.data.pop('script_data.script', [FileHelper.get_file_from_request('script')])[0]
        self.dependency_file = \
            request.data.pop('script_data.requirements', [FileHelper.get_file_from_request('requirements')])[0]
        self.script_type = request.data.pop('script_data.scriptType', ['py'])[0]

        patterns = get_related_objects('patterns', request.data)
        parameters = get_related_objects('parameters', request.data)

        return parameters, patterns

    def _postprocess_request(self, parameters, patterns):
        assign_related_objects(self.command, Patterns, patterns)
        assign_related_objects(self.command, Parameters, parameters)
        build_script(self.command.id, self.command.name)
        add_command_to_nlp(self.command)

    def _prepare_script_data(self):
        return {
            'file': self.script_file,
            'dependency': self.dependency_file,
            'type': self.script_type,
            'owner': self.request.user,
            'name': self.script_file.name
        }

    def create_script(self):
        script_data = self._prepare_script_data()
        script = BaseScript.objects.create(**script_data)
        return script
