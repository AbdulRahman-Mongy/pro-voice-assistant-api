import requests
from scripts.models import BaseCommand
BuilderTest = 'http://localhost:8001/build/python/'


def build_script(command_id, command_name, files):
    # TODO: change the url
    script = BaseCommand.objects.get(pk=command_id).script
    response = requests.post(BuilderTest,
                             data={'command_id': command_id, 'command_name': command_name},
                             files={
                                 'script': script.file.url or files['script'],
                                 'requirements': script.dependency.url or files['requirements']
                             })
    return response
