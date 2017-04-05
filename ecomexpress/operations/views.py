import datetime

from django.db.models import Q
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

from jsonview.decorators import json_view

from service_centre.models import Bags
from .forms import ConsolidateBagForm
from .models import ConsolidatedBag, ConsolidatedBagCollection

records_from = datetime.datetime.now() - datetime.timedelta(days=5)


def consolidated_bags(request):
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


def dashboard(request):
   cbags = ConsolidatedBag.objects.filter(
       origin=request.user.employeemaster.service_centre, 
       created__gte=records_from, status__in=[7, 8]
   ).order_by('-created')
   return render_to_response(
       "operations/cbag_dashboard.html", {'cbags': cbags},
       context_instance=RequestContext(request))



@csrf_exempt
@json_view
def create_consolidated_bag(request):
    if request.method == 'POST':
        cbag_form = ConsolidateBagForm(request.POST)
        if cbag_form.is_valid():
            cbag = cbag_form.save(request.user.employeemaster)
            message = 'Consolidated bag {0} created'.format(cbag.bag_number)
            success = True
            form = ConsolidateBagForm()
            html = render_to_string('operations/form.html', {'form': form})
            bag_row = render_to_string(
                'operations/cbag_row.html', {'cbags': [cbag]})
        else:
            message = 'Consolidated bag creation failed'
            success = False
            html = render_to_string(
                'operations/form.html', {'form': cbag_form})
            bag_row = ''
        return {
            'success': success, 'form': html, 
            'message': message, 'bag_row': bag_row}


@json_view
def cbag_details(request):
    cbag_num = request.GET.get('cbag_num')
    cbag = ConsolidatedBag.objects.get(bag_number=cbag_num)
    cbag_collection = ConsolidatedBagCollection.objects.filter(
        consolidated_bag=cbag, status=1)
    html = render_to_string(
        'operations/cbag_include_row.html', {'bags': cbag_collection})
    return {'html': html}


@csrf_exempt
@json_view
def cbag_include(request):
    if request.method == 'POST':
        cbag_num = request.POST.get('cbag_num')
        bag_num = request.POST.get('bag_num')
        success = False

        try:
            cbag = ConsolidatedBag.objects.get(
                Q(status=1) | Q(status=4), bag_number=cbag_num,
                origin=request.user.employeemaster.service_centre)
        except ConsolidatedBag.DoesNotExist:
            message = "Consolidated Bag already closed from this Service Center"
            return {'success': success, 'message': message, 'bag': cbag_num}

        try:
            bag = Bags.objects.get(
                bag_number=bag_num, bag_status__in =[1, 3, 6], 
                current_sc=request.user.employeemaster.service_centre)
        except Bags.DoesNotExist:
            message = "Bag({0}) cannot be included to Consolidated bag({1})".format(bag_num, cbag_num)
            return {'success': success, 'message': message}

        try:
            cbag_collection = ConsolidatedBagCollection.objects.get(
                bag=bag, consolidated_bag=cbag)
            # if already deleted bag exists, just change its status
            if cbag_collection.status == 0:
                ConsolidatedBagCollection.objects.filter(
                    bag=bag, consolidated_bag=cbag).update(status=1)
                cbag_collection = ConsolidatedBagCollection.objects.get(
                    bag=bag, consolidated_bag=cbag)
                success = True
            else:
                message = 'Bag already included in Consolidated Bag {0}'.format(cbag_num)
                return {'success': success, 'message': message}
        except ConsolidatedBagCollection.DoesNotExist:
            cbag_collection = ConsolidatedBagCollection.objects.create(
                bag=bag, consolidated_bag=cbag)
            success = True

        message = 'Bag {0} succesfully Included'.format(bag_num)
        html = render_to_string(
            'operations/cbag_include_row.html', {'bags': [cbag_collection]})

        return {'success': success, 'message': message, 'html': html}


@csrf_exempt
@json_view
def cbag_remove(request):
    if request.method == 'POST':
        cbag_num = request.POST.get('cbag_num')
        bag_num = request.POST.get('bag_num')
        success = False

        try:
            cbag = ConsolidatedBag.objects.get(
                ~Q(status=1) | ~Q(status=4), bag_number=cbag_num,
                origin=request.user.employeemaster.service_centre)
        except ConsolidatedBag.DoesNotExist:
            message = "Consolidated Bag already closed from this Service Center"
            return {'success': success, 'message': message, 'bag': cbag_num}

        try:
            bag = Bags.objects.get(
                bag_number=bag_num, bag_status__in =[1, 3, 6], 
                current_sc=request.user.employeemaster.service_centre)
        except Bags.DoesNotExist:
            message = "Bag({0}) cannot be removed from Consolidated bag({1})".format(bag_num, cbag_num)
            return {'success': success, 'message': message}

        try:
            ConsolidatedBagCollection.objects.get(
                bag=bag, consolidated_bag=cbag, status=1)
            ConsolidatedBagCollection.objects.filter(
                bag=bag, consolidated_bag=cbag, status=1).update(status=0)
            message = 'Bag({0}) successfully removed from Consolidated Bag {1}'.format(bag_num, cbag_num)
            success = True
        except ConsolidatedBagCollection.DoesNotExist:
            message = 'ALERT: BAG ({0}) NOT REMOVED'.format(bag_num)

        return {'success': success, 'message': message}


@json_view
def cbag_close(request):
    if request.method == 'POST':
        cbag_num = request.POST.get('cbag_num')
        cbag = ConsolidatedBag.objects.get(bag_number=cbag_num)
        updated = cbag.close_bag()
        if not updated:
            success = False
            message = "{0} Close operation failed".format(cbag_num)
        else:
            success = True
            message = "Consolidated Bag ({0}) successfully closed".format(cbag_num)
        return {'success': success, 'message': message}


@json_view
def cbag_inscan(request):
    pass
