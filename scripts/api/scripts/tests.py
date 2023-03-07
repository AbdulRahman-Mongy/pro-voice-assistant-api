from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework.status import *
import os


class TestScriptsOperations(APITestCase):
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    owner = None
    file = None
    dependency_file = None

    def setUp(self):
        super(TestScriptsOperations, self).setUp()
        self.owner = self.auth()
        file_name = 'new_file.txt'
        dependency_file_name = 'new_dep.txt'
        self.create_file(file_name, "This is a dummy script")
        self.create_file(dependency_file_name, "This is a dummy dependency")
        self.file = open(file_name, 'r')
        self.dependency_file = open(dependency_file_name, 'r')

    def tearDown(self):
        super(TestScriptsOperations, self).tearDown()
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

    def test_create_script(self):
        data = self.script_sample_data()
        response = self.client.post(reverse('scripts'), data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_fork_script(self):
        owner1 = self.owner
        script_id = self.create_script(owner=owner1)
        user_id = self.get_new_user("Bob")
        data = {
            'id': f'{script_id}',
            'owner': f"{user_id}",
            'name': 'This is a copy by Bob',
        }

        response = self.client.post(reverse('fork_scripts'), data)
        owner2 = response.data['owner']
        self.assertNotEqual(owner1, owner2)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_get_script(self):
        script_id = self.create_script(owner=self.owner)
        path = reverse('script_download', kwargs={'pk': script_id})
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTP_200_OK)
