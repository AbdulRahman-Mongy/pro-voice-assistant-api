import json


def get_related_objects(relation_name, data):
    related_list = [data[k] for k in data if k.startswith(relation_name)]
    to_remove = [k for k in data if k.startswith(relation_name)]
    for k in to_remove:
        data.pop(k)
    return related_list


def assign_related_objects(command_id, cls, data_list):
    for element in data_list:
        values = json.loads(element)
        cls.objects.create(**values, command=command_id)