import datetime
import io
import mimetypes

import requests
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from .models import BaseCommand

BuilderTest = 'http://localhost:8001/build/python/'


class FileHelper:

    @staticmethod
    def copy_file(file):
        new_file = ContentFile(file.read())
        new_file.name = file.name.split('/')[-1]
        return new_file

    @staticmethod
    def get_file_from_request(default_name):
        created_name = f'{datetime.datetime.now()}-{default_name}.txt'
        content_type, charset = mimetypes.guess_type(created_name)
        return InMemoryUploadedFile(file=io.BytesIO(), name=created_name,
                                    field_name=None, content_type=content_type,
                                    charset=charset, size=0)


def build_script(command_id, command_name, files):
    # TODO: change the url
    script = BaseCommand.objects.get(pk=command_id).script
    response = requests.post(BuilderTest,
                             data={'command_id': command_id, 'command_name': command_name},
                             files={
                                 'script': script.file or files['script'],
                                 'requirements': script.dependency or files['requirements']
                             })
    return response
