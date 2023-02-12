from .serializers import *
from scripts.models import *
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse


class ListCreateScripts(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = BaseScript.objects.all()
    serializer_class = BaseScriptSerializer


class CopyScripts(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = BaseScript.objects.all()
    serializer_class = BaseScriptCopySerializer


class DownloadScripts(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = BaseScript.objects.all()
    serializer_class = BaseScriptSerializer

    def get(self, request, *args, **kwargs):
        pk = int(kwargs.get('pk'))
        script = self.queryset.get(pk=pk)
        file_name = script.file.name
        return FileResponse(open(file_name, 'rb'), as_attachment=True)
