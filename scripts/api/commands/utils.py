import json

from scripts.models import CommandApproveRequest


def get_related_objects(relation_name, data):
    related_list = [data[k] for k in data if k.startswith(relation_name)]
    to_remove = [k for k in data if k.startswith(relation_name)]
    for k in to_remove:
        data.pop(k)
    return related_list


def assign_related_objects(command_id, cls, data_list):
    # TODO: delete all before assigning
    cls.objects.filter(command=command_id).delete()
    for element in data_list:
        values = json.loads(element)
        cls.objects.create(**values, command=command_id)


def submit_approval_request(command):
    approval_request = CommandApproveRequest.objects.create(
        command=command,
        status='pending',
    )
    return approval_request


def handle_command_state(request):
    request.data['state'] = 'private'
    return request.data.pop('visibility', ['private'])[0].lower() == 'public'
