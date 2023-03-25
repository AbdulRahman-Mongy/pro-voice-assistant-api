from .serializers import *
from scripts.models import *
from rest_framework import generics, filters, status
from rest_framework.permissions import *
from django.db.models import Q
from rest_framework.response import Response


class CreateCommands(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = BaseCommand.objects.all()
    serializer_class = BaseCommandSerializer

    script_file = dependency_file = script_type = None

    def perform_create(self, serializer):
        script = self.create_script()
        serializer.save(owner=self.request.user, script=script)

    def post(self, request, *args, **kwargs):
        self.script_file = request.data.pop('script_data.file')[0]
        self.dependency_file = request.data.pop('script_data.dependency')[0]
        self.script_type = request.data.pop('script_data.type')[0]
        return super(CreateCommands, self).post(request, *args, **kwargs)

    def create_script(self):
        script_data = dict()
        script_data['file'] = self.script_file
        script_data['dependency'] = self.dependency_file
        script_data['type'] = self.script_type
        script_data['owner'] = self.request.user
        script_data['name'] = self.script_file.name
        script = BaseScript.objects.create(**script_data)
        return script


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
