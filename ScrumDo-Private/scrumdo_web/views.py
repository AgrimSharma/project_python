# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
#
# This software is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy (See file COPYING) of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

from django.http import HttpResponse

from apps.projects.models import Project
from django.conf import settings
from django_redis import get_redis_connection
from django.template.loader import get_template
from django.shortcuts import render_to_response
from django.template import RequestContext

# We don't want to immiediately fail on redis errors, but we do want to eventually
# remove this instance from the cluster if it keeps failing.  So we'll keep track
# of how many failures there were.
redis_failures = 0

def status(request):
    global redis_failures

    Project.objects.all()[0]  # this will prevent an instance going live that can't load a project record, usually do to migrations.

    p = Project.objects.count()
    if p <= 0:
        raise Exception("Bad project count", "Bad")
    try:
        redis = get_redis_connection('default')
        redis.set("STATUS_CHECK", 1)
        cached = redis.get("STATUS_CHECK")
    except:
        redis_failures += 1
        if redis_failures >= 100:
            raise Exception("Could not connect to redis")

    return HttpResponse("ok")


def betaOptions(request):
    context = RequestContext(request)
    return render_to_response('beta_options.html', {'STATIC_URL': settings.STATIC_URL}, context_instance=context)

def staticurl(request):
    return HttpResponse(settings.STATIC_URL)


def server_error(request, template_name='500.html'):
    context = RequestContext(request)
    return render_to_response(template_name, {'STATIC_URL': settings.STATIC_URL}, context_instance=context)