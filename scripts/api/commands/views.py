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

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def post(self, request, *args, **kwargs):
        script = BaseScript.objects.get(pk=request.data['script'])
        if script.owner.id != self.request.user.id:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super(CreateCommands, self).post(request, *args, **kwargs)


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
        if self.is_allowed_to_delete_command(request, *args, **kwargs):
            return self.destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def is_allowed_to_delete_command(self, request, *args, **kwargs):
        pk = kwargs.get('id')
        command = BaseCommand.objects.filter(pk=pk)
        if command and command[0].owner.id != request.user.id:
            return False
        return True
