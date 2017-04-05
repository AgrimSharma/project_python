from django.shortcuts import render_to_response,HttpResponse
from django.template import RequestContext
import json
from apps.projects.models.story import Story
from django.db.models import Q

def events_calendar(request):
    data = Story.objects.filter(~Q(due_date=None))
    return HttpResponse(json.dumps({"count":len(data)}))
    # return render_to_response("emailconfirmation/confirm_email.html", {
    #     "email_address": email_address,
    # }, context_instance=RequestContext(request))