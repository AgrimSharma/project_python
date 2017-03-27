# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.conf import settings
import pprint
import logging
logger = logging.getLogger(__name__)


pp = pprint.PrettyPrinter(indent=4)

def addons(request):
    context = {}
    print "addons function called"
    context['base_url'] = settings.BASE_URL
    return render_to_response("addons/addons.html",  context , context_instance=RequestContext(request) )
