import datetime

from django.db.models import Q
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

from jsonview.decorators import json_view

from service_centre.models import *

#records_from = datetime.datetime.now() - datetime.timedelta(days=5)


def get_transit_master_cluster_based(org_sc,dest_sc, added_time = None):
    if request.method == 'GET':
        cbag_form = ConsolidateBagForm()
        cbags = ConsolidatedBag.objects.filter(
            origin=request.user.employeemaster.service_centre, 
            created__gte=records_from, status__in=[1,2]
        ).order_by('-created')
        return render_to_response(
            "operations/consolidated_bags.html",
            {'cbag_form': cbag_form, 'cbags': cbags},
            context_instance=RequestContext(request))
