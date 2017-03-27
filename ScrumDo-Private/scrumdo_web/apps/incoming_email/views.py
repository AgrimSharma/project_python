from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


from .manager import handle_incoming_project_email, handle_incoming_story_email, send_error_response

import json

@csrf_exempt
def project_hook(request):
    events = json.loads(request.POST.get('mandrill_events',[]))
    for event in events:
        if event['event'] == 'inbound':
            status, reason = handle_incoming_project_email(event['msg'])
            if not status and reason is not None:
                send_error_response(event['msg'],
                                    "We received your email to create a card, but couldn't because:",
                                    reason)
    return HttpResponse('ok')


@csrf_exempt
def story_hook(request):
    events = json.loads(request.POST.get('mandrill_events',[]))
    for event in events:
        if event['event'] == 'inbound':
            status, reason = handle_incoming_story_email(event['msg'])
            if not status and reason is not None:
                send_error_response(event['msg'],
                                    "We received your response to a card notification, but couldn't add a comment to the card because:",
                                    reason)
    return HttpResponse('ok')
