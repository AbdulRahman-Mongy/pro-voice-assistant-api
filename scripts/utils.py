import datetime
import io, os
import mimetypes
import logging
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings


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

    @staticmethod
    def remove_files(files):
        for file in files:
            file_path = f'{settings.BASE_DIR}{file.url}'
            if not os.path.isfile(file_path):
                logging.info(f"Error on file {file_path}\n This file no longer exists")
            else:
                try:
                    os.remove(file_path)
                except Exception as e:
                    logging.info(f"Something went wrong: {e}")
