import json

from rest_framework.test import APITestCase
from unittest.mock import patch
from django.http import HttpResponse
from django.urls import reverse
from rest_framework.status import *
import os
from scripts.models import *


def mock_builder(command_id, command_name, files):
    return HttpResponse(status=202,
                        content=json.dumps(
                            {'command_id': command_id, 'job_id': 1,
                             'message': "command has been added to the queue"}),
                        content_type='application/json')


class TestCommandsOperations(APITestCase):

    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    owner = None
    file = None
    dependency_file = None

    def setUp(self):
        super(TestCommandsOperations, self).setUp()
        self.owner = self.auth()
        file_name = 'new_file.txt'
        dependency_file_name = 'new_dep.txt'
        self.create_file(file_name, "This_is_a_dummy_script")
        self.create_file(dependency_file_name, "This_is_a_dummy_dependency")
        self.file = open(file_name, 'r')
        self.dependency_file = open(dependency_file_name, 'r')

    def tearDown(self):
        super(TestCommandsOperations, self).tearDown()
        self.file.close()
        self.dependency_file.close()
        os.remove(f'{self.file.name}')
        os.remove(f'{self.dependency_file.name}')

    def create_user(self, name):
        credentials = {
            'username': f'{name}',
            'password1': 'admin_admin321',
            'password2': 'admin_admin321',
            'email': f"{name}@gmail.com"
        }
        self.client.post(reverse('register_user'), credentials)

    def login_user(self, credentials):
        response = self.client.post(reverse('user_login'), credentials)
        token = response.data['access_token']
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return response.data['user']['pk']

    def auth(self):
        self.create_user('TEST')
        user_id = self.login_user({
            'username': 'TEST',
            'password': 'admin_admin321',
            'email': "TEST@gmail.com"
        })
        return user_id

    def get_new_user(self, name):
        self.create_user(name)
        user_id = self.login_user(credentials={
            'username': name,
            'password': 'admin_admin321',
            'email': f"{name}@gmail.com"
        })
        return user_id

    def create_script(self, owner):
        data = self.script_sample_data(owner=owner)
        response = self.client.post(reverse('scripts'), data)

        # reset the cursor so that we can reread the files
        self.file.seek(0)
        self.dependency_file.seek(0)

        return response.data['id']

    def script_sample_data(self, **kwargs):
        data = {
            "name": "new script",
            "file": self.file,
            "dependency": self.dependency_file,
            "owner": f"{self.owner or 0}",
        }
        for key, value in kwargs.items():
            if value is not None:
                data[key] = value
        return data

    @staticmethod
    def create_file(file_name, content):
        file = open(file_name, "w+")
        file.write(content)
        file.close()

    def create_command(self, **kwargs):
        data = self.command_sample_data(**kwargs)
        response = self.client.post(reverse('commands'), data)
        return response.data['id']

    def command_sample_data(self, **kwargs):
        data = {
            "name": 'Test Command Name',
            "description": 'Test Command Description',
            "script_data.script": self.file,
            "script_data.requirements": self.dependency_file,
            "script_data.scriptType": ["py"],
            "patterns[0]": '{"syntax": "pat0"}',
            "parameters[0]": '{"order": 1, "name": "param0", "type": "string"}',
            "parameters[1]": '{"order": 2, "name": "param1", "type": "datetime"}',
        }
        # currently we have to declare script_data in this way due to serialization issues with the files
        for key, value in kwargs.items():
            if value is not None:
                data[key] = value
        return data

    # @patch('scripts.api.commands.views.build_script', mock_builder)
    def test_create_command(self):
        """
            Asserting the command created with correct values
        """

        data = self.command_sample_data()
        response = self.client.post(reverse('commands'), data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        created_command = BaseCommand.objects.get(pk=response.data['id'])
        self.assertEqual(created_command.owner, created_command.script.owner)
        self.assertEqual(1, len(Patterns.objects.filter(command=created_command)))
        self.assertEqual(2, len(Parameters.objects.filter(command=created_command)))
        created_script = created_command.script
        self.file.seek(0)
        self.assertEqual(created_script.file.read(), self.file.read().encode('utf-8'))
        self.file.seek(0)

    # def test_build_executable(self):
    #     command_id = self.create_command()
    #     command_name = "test_command"
    #     command = BaseCommand.objects.get(pk=command_id)
    #     files = {
    #         'script': command.script.file,
    #         'requirements': command.script.dependency
    #     }
    #     response = build_script(command_id, command_name, files)
    #     content = json.loads(response.content)
    #     self.assertEqual(response.status_code, HTTP_202_ACCEPTED)
    #     self.assertEqual(content.get('command_id', '0'), str(command_id))

    def test_get_exe_from_builder(self):

        link = 'https://www.google.com/'
        response = self.client.put(reverse('exec', kwargs={'id': 5}), data={
            'executable_url': link
        })
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

        command_id = self.create_command()
        response = self.client.put(reverse('exec', kwargs={'id': command_id}), data={
            'executable_url': link
        })
        self.assertEqual(response.status_code, HTTP_200_OK)
        command = BaseCommand.objects.get(pk=command_id)
        self.assertEqual(command.executable_url, link)

        # assert the command will not be updated if no link provided
        response = self.client.put(reverse('exec', kwargs={'id': command_id}), data={})
        command = BaseCommand.objects.get(pk=command_id)
        self.assertEqual(command.executable_url, link)

    # def test_update_command(self):
    #     data = self.command_sample_data()
    #     response = self.client.post(reverse('commands'), data)
    #     created_command = BaseCommand.objects.get(pk=response.data['id'])
    #
    #     self.assertEqual(created_command.script.type, "py")
    #     self.file.seek(0)
    #     self.dependency_file.seek(0)
    #     data['script_data.scriptType'] = ['js']
    #
    #     response = self.client.put(reverse('detail_commands', kwargs={'id': created_command.id}),
    #                                data)
    #     self.assertEqual(response.status_code, HTTP_200_OK)
    #     script = BaseCommand.objects.get(pk=response.data['id']).script
    #     self.assertEqual(script.type, 'js')
    #
    # def test_update_command_file(self):
    #     data = self.command_sample_data()
    #     response = self.client.post(reverse('commands'), data)
    #     created_command = BaseCommand.objects.get(pk=response.data['id'])
    #     self.dependency_file.seek(0)
    #     self.file.seek(0)
    #     new_file = 'update_script'
    #     blob_name = "this_is_an_updated_script"
    #     self.create_file(new_file, blob_name)
    #     new_created_file = open(new_file, 'r')
    #     data['script_data.script'] = new_created_file
    #     response = self.client.put(reverse('detail_commands', kwargs={'id': created_command.id}),
    #                                data)
    #     script = BaseCommand.objects.get(pk=response.data['id']).script
    #     self.assertEqual(response.status_code, HTTP_200_OK)
    #     self.assertIn(new_file, script.file.name)
    #
    #     # cleanup
    #     new_created_file.close()
    #     os.remove(f'{new_created_file.name}')
    #
    # def test_delete_my_command(self):
    #     command = self.create_command()
    #     response = self.client.delete(reverse('detail_commands', kwargs={'id': command}))
    #     self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
    #
    # def test_delete_unauthorized_command(self):
    #     command = self.create_command()
    #     self.client.logout()
    #     user_id = self.get_new_user("Unauthorized_User")
    #     response = self.client.delete(reverse('detail_commands', kwargs={'id': command}))
    #     self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_fork_command(self):
        created_command = BaseCommand.objects.get(pk=self.create_command())
        created_command.script.state = 'public'
        created_command.save()
        commands_before_fork = BaseCommand.objects.all().count()
        scripts_before_fork = BaseScript.objects.all().count()
        user_id = self.get_new_user("New_User")
        response = self.client.get(reverse('fork_commands', kwargs={'id': created_command.id}))
        commands_after_fork = BaseCommand.objects.all().count()
        scripts_after_fork = BaseScript.objects.all().count()
        self.assertEqual(commands_after_fork, commands_before_fork + 1)
        self.assertEqual(scripts_after_fork, scripts_before_fork + 1)
        forked_command = BaseCommand.objects.get(pk=response.data['id'])
        self.assertEqual(forked_command.owner.id, user_id)
        self.assertNotEqual(forked_command.owner.id, created_command.owner.id)
