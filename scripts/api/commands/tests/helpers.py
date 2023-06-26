from django.urls import reverse
from .payloads import (
    user_sample_data,
    script_sample_data,
    command_sample_data
)


def create_user(obj, name):
    credentials = user_sample_data(name)
    obj.client.post(reverse('register_user'), credentials)


def login_user(obj, credentials):
    response = obj.client.post(reverse('user_login'), credentials)
    token = response.data['access_token']
    obj.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return response.data['user']['pk']


def auth(obj):
    create_user(obj, 'TEST')
    user_id = login_user(obj, {
        'username': 'TEST',
        'password': 'admin_admin321',
        'email': "TEST@gmail.com"
    })
    return user_id


def get_new_user(obj, name):
    create_user(obj, name)
    user_id = login_user(obj, credentials={
        'username': name,
        'password': 'admin_admin321',
        'email': f"{name}@gmail.com"
    })
    return user_id


def create_script(obj, owner):
    data = script_sample_data(obj, owner=owner)
    response = obj.client.post(reverse('scripts'), data)

    # reset the cursor so that we can reread the files
    obj.file.seek(0)
    obj.dependency_file.seek(0)

    return response.data['id']


def create_file(file_name, content):
    file = open(file_name, "w+")
    file.write(content)
    file.close()


def create_command(obj, **kwargs):
    data = command_sample_data(obj, **kwargs)
    response = obj.client.post(reverse('commands'), data)
    return response.data['id']
