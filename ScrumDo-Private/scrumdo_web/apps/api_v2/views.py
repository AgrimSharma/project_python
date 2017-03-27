from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from piston.models import Consumer
from forms import *
# from apps.projects.story_views import _calculate_rank

def docs(request):
    return render_to_response("api_v2/swagger.html", {"SSL_BASE_URL":settings.SSL_BASE_URL}, context_instance = RequestContext(request) )

def resources(request, resource_name=None):
    if resource_name:
        return render_to_response("api_v2/discovery/%s" % resource_name, {"SSL_BASE_URL":settings.SSL_BASE_URL}, context_instance = RequestContext(request) )
    else:
        return render_to_response("api_v2/discovery/resources.json", {"SSL_BASE_URL":settings.SSL_BASE_URL}, context_instance = RequestContext(request) )

@login_required
def oauth_apps(request):
    
    if request.method == "POST":
        form = ConsumerForm(request.POST)
        if form.is_valid():
            consumer = form.save(commit=False)
            consumer.user = request.user
            consumer.status = 1
            consumer.generate_random_codes()
    else:
        form = ConsumerForm()

    existing_apps = Consumer.objects.filter(user=request.user)
    return render_to_response("api_v2/oauth/apps.html", {"form":form, "existing_apps":existing_apps, "SSL_BASE_URL":settings.SSL_BASE_URL}, context_instance = RequestContext(request) )

@login_required
def oauth_access():
    pass
