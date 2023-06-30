import requests
from scripts.models import BaseCommand
BuilderTest = 'http://localhost:8001/build/python/'
DeleteURL = 'http://localhost:8001/executable'


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


def remove_executable(old_executable_link):
    response = requests.delete(DeleteURL, params={'old_executable_link': old_executable_link})
    return response
