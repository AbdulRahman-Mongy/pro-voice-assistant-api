import json
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework.status import *


class TestScriptsOperations(APITestCase):

    def test_create_script(self):
        owner = self.auth()
        file = open('/home/invation/Desktop/GP_BACKEND/Programmable-Voice-Assistant-Backend/requirements.txt')
        data = {
            "name": "new script",
            "file": file,
            "state": "private",
            "description": "This is a test",
            "owner": f"{owner}",
        }
        response = self.client.post(reverse('scripts'), data)
        file.close()
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def auth(self):
        self.create_user('TEST')
        user_id = self.login_user({
            'username': 'TEST',
            'password': 'admin_admin321',
            'email': "TEST@gmail.com"
        })
        return user_id

    def create_script(self, owner):
        file = open('/home/invation/Desktop/GP_BACKEND/Programmable-Voice-Assistant-Backend/requirements.txt')
        data = {
            "name": "new script",
            "file": file,
            "state": "private",
            "description": "This is a test",
            "owner": f"{owner}",
        }
        response = self.client.post(reverse('scripts'), data)
        file.close()
        return response.data['id']

    def test_copy_script(self):
        self.create_user("Alice")
        user_id = self.login_user(credentials={
            'username': 'Alice',
            'password': 'admin_admin321',
            'email': "Alice@gmail.com"
        })
        script_id = self.create_script(owner=user_id)
        owner1 = user_id
        self.create_user("Bob")
        user_id = self.login_user(credentials={
            'username': 'Bob',
            'password': 'admin_admin321',
            'email': "Bob@gmail.com"
        })
        data = {
            'id': f'{script_id}',
            'owner': f"{user_id}",
            'name': 'This is a copy by Bob',
        }

        response = self.client.post(reverse('copy_scripts'), data)
        owner2 = response.data['owner']
        self.assertNotEqual(owner1, owner2)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

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
