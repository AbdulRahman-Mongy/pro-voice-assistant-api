from rest_framework import serializers
from scripts.models import *


class BaseCommandSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = BaseCommand
        fields = (
            "id",
            "name",
            "description",
            "parameters",
            "script",
        )
