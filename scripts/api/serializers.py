from rest_framework import serializers
from scripts.models import *
from scripts.utils import *


class BaseScriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseScript
        fields = '__all__'


class BaseScriptCopySerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=BaseScript.objects.all(), many=False)

    class Meta:
        model = BaseScript
        fields = ['owner', 'id', 'name']

    def create(self, validated_data):
        original_script = BaseScript.objects.get(pk=validated_data['id'].id)
        new_file = FileHelper.copy_file(original_script.file)
        validated_data['file'] = new_file
        validated_data['id'] = None
        return super(BaseScriptCopySerializer, self).create(validated_data)
