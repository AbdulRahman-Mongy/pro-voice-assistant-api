from rest_framework import serializers
from scripts.models import *


class PatternsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patterns
        fields = ['syntax']


class BaseCommandSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    patterns = PatternsSerializer(many=True, required=False)

    class Meta:
        model = BaseCommand
        fields = (
            "id",
            "name",
            "description",
            "parameters",
            "patterns",
            "script",
        )

    def create(self, validated_data):
        patterns = validated_data.get('patterns', [])
        command = BaseCommand.objects.create(**validated_data)
        for pattern in patterns:
            Patterns.objects.create(command=command, **pattern)
        return command
