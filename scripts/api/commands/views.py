import json

from .serializers import *
from scripts.models import *
from rest_framework import generics, filters, status
from rest_framework.permissions import *
from django.db.models import Q
from rest_framework.response import Response
from scripts.utils import FileHelper


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

        patterns = self.get_related_objects('patterns', request.data)
        parameters = self.get_related_objects('parameters', request.data)

        response = super(CreateCommands, self).post(request, *args, **kwargs)

        self.assign_related_objects(self.command, Patterns, patterns)
        self.assign_related_objects(self.command, Parameters, parameters)

        return response

    @staticmethod
    def get_related_objects(relation_name, data):
        related_list = [data[k] for k in data if k.startswith(relation_name)]
        to_remove = [k for k in data if k.startswith(relation_name)]
        for k in to_remove:
            data.pop(k)
        return related_list

    @staticmethod
    def assign_related_objects(command_id, cls, data_list):
        for element in data_list:
            values = json.loads(element)
            cls.objects.create(**values, command=command_id)

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


class ListCommands(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = BaseCommandSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        if self.request.user.is_staff:
            return BaseCommand.objects.all()
        domain = Q(owner=self.request.user.id) | Q(state='public')
        queryset = BaseCommand.objects.filter(domain)
        return queryset


class DetailCommands(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AllowAny]
    serializer_class = BaseCommandSerializer
    queryset = BaseCommand.objects.all()
    lookup_field = 'id'

    def get_queryset(self):
        if self.request.user.is_staff:
            return BaseCommand.objects.all()
        domain = Q(owner=self.request.user.id) | Q(state='public')
        queryset = BaseCommand.objects.filter(domain)
        return queryset

    def delete(self, request, *args, **kwargs):
        if self.is_allowed_to_delete_or_update_command(request, *args, **kwargs):
            return self.destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def put(self, request, *args, **kwargs):
        if self.is_allowed_to_delete_or_update_command(request, *args, **kwargs):
            self.update_scripts(request, *args, **kwargs)
            return self.update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def update_scripts(self, request, *args, **kwargs):
        script_file = request.data.pop('script_data.file')[0] or ''
        dependency_file = request.data.pop('script_data.dependency')[0] or ''
        script_type = request.data.pop('script_data.type')[0] or ''
        pk = kwargs.get('id')
        command = BaseCommand.objects.filter(pk=pk)
        if command:
            script = command[0].script
            script.type = script_type if script_type else script.type
            script.file = script_file if script_file else script.file
            script.dependency = dependency_file if dependency_file else script.dependency
            script.save()

    def is_allowed_to_delete_or_update_command(self, request, *args, **kwargs):
        pk = kwargs.get('id')
        command = BaseCommand.objects.filter(pk=pk)
        if command and command[0].owner.id != request.user.id:
            return False
        return True


class ForkCommands(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BaseCommandCopySerializer
    queryset = BaseCommand.objects.all()

    def get_queryset(self):
        if self.request.user.is_staff:
            return BaseCommand.objects.all()
        domain = Q(owner=self.request.user.id) | Q(state='public')
        queryset = BaseCommand.objects.filter(domain)
        return queryset

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('id')
        command = self.queryset.get(pk=pk)
        fork_command = self.get_forked_command(command, request, *args, **kwargs)
        serializer = BaseCommandCopySerializer(fork_command, many=False)
        return Response(serializer.data)

    def get_forked_command(self, command, request, *args, **kwargs):
        owner = self.request.user
        # django trick to duplicate objects
        script = command.script
        script.pk = None
        script.owner = owner
        script.save()
        created_command = BaseCommand.objects.get(pk=command.pk)
        created_command.pk = None
        created_command.owner = owner
        created_command.script = script
        created_command.save()

        parameters = Parameters.objects.filter(command=command.id)
        patterns = Patterns.objects.filter(command=command.id)
        for param in parameters:
            param.pk = None
            param.command = created_command
            param.save()
        for pattern in patterns:
            pattern.pk = None
            pattern.command = created_command
            pattern.save()
        return created_command
