import os
from unittest.mock import patch

from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
)

from .mocks import mock_builder
from .payloads import command_sample_data
from .helpers import (
    auth,
    create_file,
    create_command,
    get_new_user
)

from scripts.models import (
    BaseCommand,
    BaseScript,
    Patterns,
    Parameters
)


@patch('scripts.api.commands.views.commands_view.build_script', mock_builder)
class TestCommandsOperations(APITestCase):

    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    owner = None
    file = None
    dependency_file = None

    def setUp(self):
        super(TestCommandsOperations, self).setUp()
        self.owner = auth(self)
        file_name = 'new_file.txt'
        dependency_file_name = 'new_dep.txt'
        create_file(file_name, "This_is_a_dummy_script")
        create_file(dependency_file_name, "This_is_a_dummy_dependency")
        self.file = open(file_name, 'r')
        self.dependency_file = open(dependency_file_name, 'r')

    def tearDown(self):
        super(TestCommandsOperations, self).tearDown()
        self.file.close()
        self.dependency_file.close()
        os.remove(f'{self.file.name}')
        os.remove(f'{self.dependency_file.name}')

    def test_create_command(self):
        """
            Asserting the command created with correct values
        """

        data = command_sample_data(self)
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

    def test_get_exe_from_builder(self):
        link = 'https://www.google.com/'
        response = self.client.put(reverse('exec', kwargs={'id': 5}), data={
            'executable_url': link
        })
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

        command_id = create_command(self)
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

    def test_fork_command(self):
        created_command = BaseCommand.objects.get(pk=create_command(self))
        created_command.state = 'public'
        created_command.save()
        commands_before_fork = BaseCommand.objects.count()
        params_before_fork = Parameters.objects.count()
        scripts_before_fork = BaseScript.objects.count()
        user_id = get_new_user(self, "New_User")
        response = self.client.post(reverse('fork_commands', kwargs={'id': created_command.id}))
        commands_after_fork = BaseCommand.objects.count()
        scripts_after_fork = BaseScript.objects.count()
        params_after_fork = Parameters.objects.count()

        self.assertEqual(commands_after_fork, commands_before_fork + 1)
        self.assertEqual(params_after_fork, params_before_fork + 2)
        self.assertEqual(scripts_after_fork, scripts_before_fork + 1)

        forked_command = BaseCommand.objects.get(pk=response.data['id'])
        self.assertEqual(forked_command.owner.id, user_id)
        self.assertEqual(forked_command.state, 'private')
        self.assertNotEqual(forked_command.owner.id, created_command.owner.id)

        # asserting new file was created with the same content
        self.assertNotEqual(forked_command.script.file.url, created_command.script.file.url)
        self.assertEqual(forked_command.script.file.read(), created_command.script.file.read())

