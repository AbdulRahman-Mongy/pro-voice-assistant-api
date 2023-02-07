from django.core.files.base import ContentFile


class FileHelper:

    @staticmethod
    def copy_file(file):
        new_file = ContentFile(file.read())
        new_file.name = file.name.split('/')[-1]
        return new_file
