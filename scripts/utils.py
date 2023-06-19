import datetime
import io
import mimetypes

import requests
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile

BuilderTest = 'http://localhost:8000/build/python/'


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


def build_script(command_id, files):
    # TODO: change the url
    response = requests.post(BuilderTest, data={'command_id': command_id}, files={
                                 'script': files['script'],
                                 'requirements': files['requirements']
                             })
    return response
