from rest_framework import serializers

from scripts.api.commands.serializers.command_serializers import ParametersSerializer, PatternsSerializer
from scripts.models import BaseCommand


class CommandForTableDTOSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField(required=False)
    icon_link = serializers.SerializerMethodField()
    parameters = ParametersSerializer(many=True, required=False, source='parameters_set')
    patterns = PatternsSerializer(many=True, source='patterns_set')
    state = serializers.CharField()
    script_link = serializers.SerializerMethodField()
    requirements_link = serializers.SerializerMethodField()

    class Meta:
        model = BaseCommand
        fields = (
            'id',
            'name',
            'description',
            'icon_link',
            'parameters',
            'patterns',
            'state',
            'script_link',
            'requirements_link',
        )

    def get_icon_link(self, obj):
        if obj.icon:
            return self.context['request'].build_absolute_uri(obj.icon.url)
        return ''

    def get_script_link(self, obj):
        if obj.script:
            return self.context['request'].build_absolute_uri(obj.script.file.url)
        return ''

    def get_requirements_link(self, obj):
        if obj.script and obj.script.dependency:
            return self.context['request'].build_absolute_uri(obj.script.dependency.url)
        return ''
