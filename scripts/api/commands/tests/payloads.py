

def user_sample_data(name, **kwargs):
    data = {
        'username': f'{name}',
        'password1': 'admin_admin321',
        'password2': 'admin_admin321',
        'email': f"{name}@gmail.com"
    }
    for key, value in kwargs.items():
        if value is not None:
            data[key] = value
    return data


def script_sample_data(obj, **kwargs):
    data = {
        "name": "new script",
        "file": obj.file,
        "dependency": obj.dependency_file,
        "owner": f"{obj.owner or 0}",
    }
    for key, value in kwargs.items():
        if value is not None:
            data[key] = value
    return data


def command_sample_data(obj, **kwargs):
    data = {
        "name": 'Test Command Name',
        "description": 'Test Command Description',
        "script_data.script": obj.file,
        "script_data.requirements": obj.dependency_file,
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
