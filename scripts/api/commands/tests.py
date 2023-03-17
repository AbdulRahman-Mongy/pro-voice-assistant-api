import json

from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework.status import *
import os
from scripts.api.scripts.tests import TestScriptsOperations
from scripts.models import BaseCommand


class TestCommandsOperations(TestScriptsOperations):

    def setUp(self):
        super(TestCommandsOperations, self).setUp()

    def tearDown(self):
        super(TestCommandsOperations, self).tearDown()

    def create_command(self, **kwargs):
        data = self.command_sample_data(**kwargs)
        response = self.client.post(reverse('commands'), data)
        return response.data['id']

    def command_sample_data(self, **kwargs):
        data = {
            "name": 'Test Command Name',
            "description": 'Test Command Description',
            "script_data.file": self.file,
            "script_data.dependency": self.dependency_file,
            "script_data.type": "py",
        }
        # currently we have to declare script_data in this way due to serialization issues with the files
        for key, value in kwargs.items():
            if value is not None:
                data[key] = value
        return data

    def test_create_command(self):
        data = self.command_sample_data()
        response = self.client.post(reverse('commands'), data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        created_command = BaseCommand.objects.get(pk=response.data['id'])
        self.assertEqual(created_command.owner, created_command.script.owner)

    # def test_create_command_with_unauthorized_script(self):
    #     user_id = self.get_new_user("Bobby")
    #     script_id = self.create_script(f"{user_id}")
    #     self.client.logout()
    #     self.owner = self.auth()
    #     data = self.command_sample_data(script=f'{script_id}')
    #     response = self.client.post(reverse('commands'), data)
    #     self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
    #
    def test_delete_my_command(self):
        command = self.create_command()
        response = self.client.delete(reverse('detail_commands', kwargs={'id': command}))
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

    def test_delete_unauthorized_command(self):
        command = self.create_command()
        self.client.logout()
        user_id = self.get_new_user("Unauthorized_User")
        response = self.client.delete(reverse('detail_commands', kwargs={'id': command}))
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
