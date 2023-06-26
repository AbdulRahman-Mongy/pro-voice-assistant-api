from scripts.api.commands.serializers import BaseCommandSerializer
from scripts.models import *
from django.db.models import Q

from rest_framework import generics, filters
from rest_framework.permissions import *


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
