import json
from django.http import HttpResponse


def mock_builder(command_id, command_name, files):
    return HttpResponse(status=202,
                        content=json.dumps(
                            {'command_id': command_id, 'job_id': 1,
                             'message': "command has been added to the queue"}),
                        content_type='application/json')
