from rest_framework import serializers
from scripts.models import *


class BaseCommandSerializer(serializers.ModelSerializer):

    class Meta:
        model = BaseCommand
        fields = (
            "name",
            "description",
            "parameters",
            "script",
        )
