from .serializers import *
from scripts.models import *
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated


class ListCreateScripts(generics.ListCreateAPIView):
    queryset = BaseScript.objects.all()
    serializer_class = BaseScriptSerializer


class CopyScripts(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = BaseScript.objects.all()
    serializer_class = BaseScriptCopySerializer
