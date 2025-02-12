from django.urls import reverse
from rest_framework import serializers

from scripts.api.commands.serializers import ParametersSerializer, PatternsSerializer
from scripts.models import BaseCommand


class PublicCommandSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField(required=False)
    icon_link = serializers.SerializerMethodField()
    parameters = ParametersSerializer(many=True, required=False, source='parameters_set')
    patterns = PatternsSerializer(many=True, source='patterns_set')
    owner = serializers.CharField(source='owner.username')
    used_by_count = serializers.IntegerField(source='used_by.count')

    class Meta:
        model = BaseCommand
        fields = (
            'id',
            'name',
            'description',
            'icon_link',
            'parameters',
            'patterns',
            'owner',
            'used_by_count',
        )

    def get_icon_link(self, obj):
        if obj.icon:
            # get the absolute url of the icon
            return reverse('download_icon', kwargs={'command_id': obj.id})
        return ''


class InstallationCommandSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    executable_url = serializers.CharField(required=False)

    class Meta:
        model = BaseCommand
        fields = (
            'id',
            'name',
            'executable_url'
        )
