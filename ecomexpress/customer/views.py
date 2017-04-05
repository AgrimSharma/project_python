#===============================================================================
# Copyright, 2012, All Rights Reserved.
# File Name:views.py
# Project Name:ecomm
# To create views for customer
# Revision: 1
# Developer: Jignesh Vasani
#===============================================================================

import os

#import django.contrib.localflavor.in_.in_states.STATE_CHOICES
from customer.models import Customer, FuelSurcharge,\
    Shipper, CashOnDelivery, FreightSlab, FreightSlabZone, BrandedFullTimeEmployeeCustomer, BrandedFleetCustomer,\
    SubcustomerDetailsUpload, ShipperMapping, RateVersion, ForwardFreightRate, FreightSlabOriginZone, FreightSlabCity, FreightSlabDestZone
#from ecomm_admin.models import FuelSurcharge
from customer.forms import AddCustomerForm,\
    BrentrateForm, Shipper, AddPriceForm,FuelSurchargeForm, AddFreightSlabZoneForm,ShipperForm, SubCustomerUploadForm
from django.http import  HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
#from django.contrib.auth.models import User
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.utils import simplejson
from django.core.urlresolvers import reverse
#from django.forms.formsets import formset_factory
#from django.core import urlresolvers
#import sys, traceback
from location.forms import AddressForm, Address2Form, ContactForm, Zone
from random import randint
from datetime import date, datetime
from django.views.decorators.csrf import csrf_exempt
import json
from location.models import *
from customer.read_subcustomer_excel import update_subcustomers_list
from xlsxwriter.workbook import Workbook
import xlrd, xlwt
from reports.report_api import ReportGenerator
from django.conf import settings

def customer_home(request):
    ''' View to display home page'''
    active_customers = Customer.objects.filter(activation_status=True)
    inactive_customers = Customer.objects.filter(activation_status=False)
    form    = AddCustomerForm()
    return render_to_response('customer/home.html',
            {'active_customers':active_customers,
             'inactive_customers':inactive_customers, 'form':form},
            context_instance=RequestContext(request))



def add_customer(request):
#    if request.is_ajax:
    ''' User submitted the form '''
    if request.method == 'POST':
        customer_form = AddCustomerForm(request.POST)
        address_form = Address2Form(request.POST)
        contact_form = ContactForm(request.POST, prefix="contact")
        decision_form = ContactForm(request.POST, prefix="decision")

        if customer_form.is_valid() and address_form.is_valid() and contact_form.is_valid() and decision_form.is_valid():
#            return HttpResponse("customer_form")
            ''' Create a customer object and save it '''
            customer = customer_form.save()
            address = address_form.save()
            contact = contact_form.save()
            decision = decision_form.save()
            customer.address = address
            customer.contact_person = contact
            customer.decision_maker = decision
            id_len = len(str(customer.id))
            if id_len == 1:
                customer_code = "00"+str(customer.id)
            elif id_len == 2:
                customer_code = "0"+str(customer.id)
            else:
                customer_code = str(customer.id)

            customer.code = str(randint(10,99)) + customer_code
            customer.save()
#            customer = Customer.objects.filter(name=form.cleaned_data['name'])
            # next = request.META.get('HTTP_REFERER', None) or '/'
            #return  HttpResponseRedirect(next)
            #return HttpResponseRedirect(urlresolvers.reverse('add_customer_weight_rate')
            #customer_id= customer.id
            return HttpResponseRedirect('/customer/')
        else:
#            return HttpResponse("%s" % customer_form)
            myform = render_to_string('customer/add_customer.html', {'customer_form':customer_form,
                                                                     'address_form':address_form,
                                                                     'contact_form':contact_form,
                                                                     'decision_form':decision_form,
                                                                     }, context_instance=RequestContext(request))
            return HttpResponse("%s" % myform)
    else:
        ''' User in not submitting form , reset the form '''
        customer_form    = AddCustomerForm()
        address_form    = Address2Form()
        contact_form    = ContactForm(prefix="contact")
        decision_form    = ContactForm(prefix="decision")
        return render_to_response('customer/add_customer.html',
                    {'customer_form':customer_form,
                     'address_form':address_form,
                     'contact_form':contact_form,
                     'decision_form':decision_form},
                     context_instance=RequestContext(request)
        )

def edit_customer(request, c_id):
#    if request.is_ajax:
    ''' User submitted the form '''
    c = Customer.objects.get(id=c_id)
    save_form = False
    edit_form = True
    if request.method == 'POST':
        customer_form = AddCustomerForm(request.POST, instance=c)
        address_form = Address2Form(request.POST, instance=c.address)
        contact_form = ContactForm(request.POST, prefix="contact", instance=c.contact_person)
        decision_form = ContactForm(request.POST, prefix="decision", instance=c.decision_maker)
        if customer_form.is_valid() and address_form.is_valid() and contact_form.is_valid() and decision_form.is_valid():
#            return HttpResponse("%s" % customer_form)
            customer_form.cleaned_data['id'] = c.id
            contact_form.cleaned_data['id'] = c.contact_person.id
            decision_form.cleaned_data['id'] = c.decision_maker.id
            address_form.cleaned_data['id'] = c.address.id
            #return HttpResponse("%s" % customer_form)
            ''' Create a customer object and save it '''
            customer = customer_form.save()
            address = address_form.save()
            contact = contact_form.save()
            decision = decision_form.save()
#            customer = Customer.objects.filter(name=form.cleaned_data['name'])
            # next = request.META.get('HTTP_REFERER', None) or '/'
            #return  HttpResponseRedirect(next)
            #return HttpResponseRedirect(urlresolvers.reverse('add_customer_weight_rate')
            #customer_id= customer.id
            save_form = True
    else:
        ''' User in not submitting form , reset the form '''
        customer_form    = AddCustomerForm(instance=c)
        address_form    = Address2Form(instance=c.address)
        contact_form    = ContactForm(prefix="contact", instance=c.contact_person)
        decision_form    = ContactForm(prefix="decision", instance=c.decision_maker)

    return render_to_response('customer/add_customer.html',{'customer_form':customer_form,
                                                                'address_form':address_form,
                                                                'contact_form':contact_form,
                                                                'decision_form':decision_form,
                                                                'save_form':save_form,
                                                                'edit_form':edit_form,
                                                                'c': c,
                                                                },context_instance=RequestContext(request))

def delete_customer(request,c_id):
    ''' To delete a specific customer '''
   # Customer.objects.filter(pk=c_id).delete()
    return HttpResponseRedirect('/customer/')

def subcustomers_upload_form(request):

    if not request.is_ajax():
        raise Http404

    form = SubCustomerUploadForm()
    c_id = request.GET.get('c_id')
    html = render_to_string('customer/sub_customer_upload_form.html',
                            {'form':form, 'c_id':c_id},
                            context_instance=RequestContext(request))
    data = {'html': html}
    return HttpResponse(simplejson.dumps(data), mimetype='application/json')

def update_subcustomers(request):
    """This view is used to show a sub customers contacts upload form
    in a jquery ui overlay, and then on form submission update the
    sub customers details in database.
    """

    # if it is a post request, then validate the form.
    errors = {}
    if request.method == 'POST':
        # if form is valid, then read the excel file and
        # save the sub customers list to database. Then return the updated
        # sub customers list.
        form = SubCustomerUploadForm(request.POST, request.FILES)
        c_id = int(request.POST.get('customer-id'))

        if form.is_valid():
            file_to_read = request.FILES['filepath']
            file_contents = file_to_read.read()
            if file_contents:
                errors = update_subcustomers_list(file_contents, c_id)
        else:
            # TODO: if form validation fails return the bound form with errors
                errors['file_error'] = 'Invalid file'

        c = Customer.objects.get(id=c_id)
        sub_customers = Shipper.objects.filter(customer=c)
        cities = City.objects.all()
        shipper_form = ShipperForm()
        address_form    = Address2Form()

        return render_to_response('customer/sub_customer.html',
                                  {'cities':cities,
                                   'shipper_form':shipper_form,
                                   'address_form':address_form,
                                   'sub_customers':sub_customers,
                                   'c': c,
                                   'errors':errors},
                                  context_instance=RequestContext(request))

def sub_customer(request, c_id):
    cities  = City.objects.all()
    c = Customer.objects.get(id=c_id)
    sub_customers = Shipper.objects.filter(customer=c)
    save_form = False
    edit_form = True
    if request.method == 'POST':
        shipper_form = ShipperForm(request.POST)
        address_form = AddressForm(request.POST)
        if shipper_form.is_valid() and address_form.is_valid():
            address = address_form.save()
            shipper = shipper_form.save(c,address)
            save_form = True
            shipper_form = ShipperForm()
            address_form    = AddressForm()
    else:
        ''' User in not submitting form , reset the form '''
        shipper_form = ShipperForm()
        address_form    = AddressForm()

    return render_to_response('customer/sub_customer.html',
                                {
                                 'cities':cities,
                                 'shipper_form':shipper_form,
                                 'address_form':address_form,
                                 'sub_customers':sub_customers,
                                 'c': c,
                                 },context_instance=RequestContext(request))


def backup_sub_customer(request, c_id):
#    if request.is_ajax:
    ''' User submitted the form '''
    cities  = City.objects.all()
    c = Customer.objects.get(id=c_id)
    sub_customers = Shipper.objects.filter(customer=c)
    save_form = False
    edit_form = True
    if request.method == 'POST':
        shipper_form = ShipperForm(request.POST)
        address_form = Address2Form(request.POST)
        city = request.POST['city']
        state = request.POST['state']
        if shipper_form.is_valid() and address_form.is_valid():
            shipper = shipper_form.save(commit=False)
            address = address_form.save(commit=False)
            ''' Create a customer object and save it '''
            address.city = city
            address.state = state
            address = address.save()
            shipper.customer= c
            shipper.address = address
            shipper.save()
            save_form = True
    else:
        ''' User in not submitting form , reset the form '''
        shipper_form = ShipperForm()
        address_form    = Address2Form()

    return render_to_response('customer/sub_customer.html',{
                                                                'cities':cities,
                                                                'shipper_form':shipper_form,
                                                                'address_form':address_form,
                                                                'sub_customers':sub_customers,
                                                                'c': c,
                                                                },context_instance=RequestContext(request))
def cod_customer(request, c_id):
#    if request.is_ajax:
    ''' User submitted the form '''
    c = Customer.objects.get(id=c_id)
    cod_customers = CashOnDelivery.objects.filter(customer=c).order_by("-effective_date", "start_range")
#    return HttpResponse("%s" % cod_customers[0])
    return render_to_response('customer/cod_customer.html',{
                                                                'cod_customers':cod_customers,
                                                                'c': c,
                                                                },context_instance=RequestContext(request))

def fs_customer(request,c_id):
    c = Customer.objects.get(id=c_id)
    fs=FuelSurcharge.objects.filter(customer=c)
    return render_to_response('customer/fs_customer.html',{ 'fs_customers':fs,'c':c},context_instance=RequestContext(request))


def branding_customer(request, c_id):
#    if request.is_ajax:
    ''' User submitted the form '''
    c = Customer.objects.get(id=c_id)
    branded_fleet = BrandedFleetCustomer.objects.filter(customer=c)
    branded_employees = BrandedFullTimeEmployeeCustomer.objects.filter(customer=c)
#    return HttpResponse("%s" % cod_customers[0])
    return render_to_response('customer/branding_customer.html',{
                                                                'branded_fleet':branded_fleet,
                                                                'branded_employees':branded_employees,
                                                                'c': c,
                                                                },context_instance=RequestContext(request))

def delete_sub_customer(request,c_id):
    ''' To delete a specific customer '''
    Customer.objects.filter(pk=c_id).delete()
    return HttpResponseRedirect('/customer/')


def price_customer(request, c_id):
#    if request.is_ajax:
    ''' User submitted the form '''
    c = Customer.objects.get(id=c_id)
    save_form = False
    edit_form = True
    if request.method == 'POST':
        fsf = FuelSurchargeForm(request.POST)
        price_form    = AddPriceForm(request.POST, instance=c)

        if price_form.is_valid() and fsf.is_valid():
            #return HttpResponse("%s" % price_form)
            price_form.cleaned_data['id'] = c.id
            customer = price_form.save()
            fs_list = FuelSurcharge.objects.filter(customer=c)
            fsf.cleaned_data['customer'] = c.id
#            return HttpResponse("%d" % len(fs_list))
            if fs_list:
                fs = fs_list[0]
                fs.fuelsurcharge_min_rate      = fsf.cleaned_data['fuelsurcharge_min_rate']
                fs.fuelsurcharge_min_fuel_rate = fsf.cleaned_data['fuelsurcharge_min_fuel_rate']
                fs.flat_fuel_surcharge = fsf.cleaned_data['flat_fuel_surcharge']
                fs.max_fuel_surcharge  = fsf.cleaned_data['max_fuel_surcharge']
                fs.save()
            else:
                fuelsurcharge = fsf.save()
            save_form = True
        #return HttpResponse("%s" % price_form)
    else:
        ''' User in not submitting form , reset the form '''
        price_form    = AddPriceForm(instance=c)
        try:
            fs = FuelSurcharge.objects.get(customer=c)
            fsf = FuelSurchargeForm(instance = fs)
        except FuelSurcharge.DoesNotExist:
            fsf = FuelSurchargeForm()

    return render_to_response('customer/price_customer.html',{
                                                                'price_form': price_form,
                                                                'fsf': fsf,
                                                                'c': c,
                                                                'save_form':save_form,
                                                                },context_instance=RequestContext(request))

def pricematrix_customer(request, c_id):
#    if request.is_ajax:
    ''' User submitted the form '''
    c = Customer.objects.get(id=c_id)
    zones = Zone.objects.all()
    freight_slabs = FreightSlab.objects.filter(customer=c)
    save_form = False
    if request.method == 'POST':
        customer_form = AddCustomerForm(request.POST, instance=c)
        if customer_form.is_valid() :
#            return HttpResponse("%s" % customer_form)
            customer_form.cleaned_data['id'] = c.id
            #return HttpResponse("%s" % customer_form)
            ''' Create a customer object and save it '''
            customer = customer_form.save()
            save_form = True
    else:
        ''' User in not submitting form , reset the form '''

    return render_to_response('customer/pricematrix_customer.html',{
                                                                'c': c,
                                                                'zones': zones,
                                                                'freight_slabs': freight_slabs,
                                                                },context_instance=RequestContext(request))

def add_zone(request, fs_id):
    fs = FreightSlab.objects.get(id=fs_id)
    fsz_form = AddFreightSlabZoneForm()
    return render_to_response('customer/add_zone.html',{
                                                        'fs': fs,
                                                        'fsz_form': fsz_form,
                                                        },context_instance=RequestContext(request))


# To manipulate customer weight rate

def customer_weight_rate_home(request):
    ''' View to display home page'''
    customer_weight_rates = CustomerWeightRate.objects.all()
    return render_to_response('customer/customer_weight_rate_home.html',{'object_list':customer_weight_rates},context_instance=RequestContext(request))







#second page wieghtrate
def customer_rate_details(request,customer_id):
    customer = Customer.objects.get(pk=customer_id)

    ''' User submitted the form '''
    if request.method == 'POST':
        formset = WeightrateFormset(request.POST)
        #weight_rate_form    = CustomerWeightRateForm(request.POST,prefix="weight_form")
        brentrate_form       = BrentrateForm(request.POST)
        value_added_surcharge = ValueCargoHandlingChargeForm(request.POST)

        for form in (brentrate_form,formset,value_added_surcharge):
            if form.is_valid():
                form.save(commit=False)
            else:
                print "not valid"
                myform = render_to_string('customer/add_customer_weight_rate.html', {'formset':formset,
                                                                            'brentrate_form':brentrate_form,
                                                                            'value_added_surcharge':value_added_surcharge,
                                                                            'customer_id':customer_id,
                                                                            }, context_instance=RequestContext(request))
                return HttpResponse("%s" % myform)

        for form in formset:
            form.save(commit=False)
            form.customer = customer

        formset.save()

#        CustomerWeightRate.objects.get_or_create(         weight_rate = weight_rate_form.cleaned_data['weight_rate'],
#                                                          slab=weight_rate_form.cleaned_data['slab'],
#                                                          weight_min = weight_rate_form.cleaned_data['weight_min'],
#                                                          weight_max = weight_rate_form.cleaned_data['weight_max'],
#                                                          customer= customer,
#                                                          )

        FuelSurcharge.objects.get_or_create(        min_brent_rate = brentrate_form.cleaned_data['min_brent_rate'],
                                                            min_fuel_surcharge = brentrate_form.cleaned_data['min_fuel_surcharge'],
                                                            flat_fuel_surcharge = brentrate_form.cleaned_data['flat_fuel_surcharge'],
                                                            max_fuel_surcharge = brentrate_form.cleaned_data['max_fuel_surcharge'],
                                                            customer= customer,
                                                    )

        ValueCargoHandlingCharge.objects.get_or_create(min_ratio = value_added_surcharge.cleaned_data['min_ratio'],
                                                        min_charge = value_added_surcharge.cleaned_data['min_charge'],
                                                        flat_charge = value_added_surcharge.cleaned_data['flat_charge'],
                                                        max_charge = value_added_surcharge.cleaned_data['max_charge'],
                                                        customer= customer,
                                                        )


        return HttpResponseRedirect('/customer/otherdetails/'+str(customer_id)+ '/add/')

    else:
        ''' User in not submitting form , reset the form '''
        formset = WeightrateFormset(queryset=CustomerWeightRate.objects.none(),initial=[{'customer':customer}])
        brentrate_form       = BrentrateForm()
        value_added_surcharge = ValueCargoHandlingChargeForm()

        return render_to_response('customer/add_customer_weight_rate.html',{'formset':formset,
                                                                            'brentrate_form':brentrate_form,
                                                                            'value_added_surcharge':value_added_surcharge,
                                                                            'customer_id':customer_id,
                                                                            },context_instance=RequestContext(request))


def edit_customer_rate_details(request,customer_id):
    customer = Customer.objects.get(pk=customer_id)
    ''' User submitted the form '''
    if request.method == 'POST':
        brentrate = FuelSurcharge.objects.get(customer=customer)
        fs_rate = ValueCargoHandlingCharge.objects.get(customer=customer)

        formset = WeightrateFormset(request.POST,queryset=CustomerWeightRate.objects.filter(customer=customer),initial=[{'customer':customer}])
        brentrate_form       = BrentrateForm(request.POST,instance=brentrate)
        value_added_surcharge = ValueCargoHandlingChargeForm(request.POST,instance=fs_rate)

        for form in ( formset,brentrate_form,value_added_surcharge):
            if form.is_valid():
                form.save(commit=False)
            else:
                print formset.errors
                myform = render_to_string('customer/edit_customer_details.html', {'formset':formset,
                                                                            'brentrate_form':brentrate_form,
                                                                            'value_added_surcharge':value_added_surcharge,
                                                                            'customer_id':customer_id,
                                                                            }, context_instance=RequestContext(request))
                return HttpResponse("%s" % myform)

        for form in formset:
            form.save(commit=False)
            form.customer = customer

        formset.save()
        brentrate_form.save()
        value_added_surcharge.save()

        ''' Forms submitted successfully now go to add other details'''
        return HttpResponseRedirect('/customer/otherdetails/'+str(customer_id)+ '/edit/')
        return HttpResponseRedirect('/customer/otherdetailsrate/'+str(customer_id)+ '/edit/')

    else:
        ''' User in not submitting form , reset the form '''
        brentrate = FuelSurcharge.objects.get(customer=customer)
        formset = WeightrateFormset(queryset=CustomerWeightRate.objects.filter(customer=customer),initial=[{'customer':customer_id}])
        fs_rate = ValueCargoHandlingCharge.objects.get(customer=customer)

        # weight_rate_form    = CustomerWeightRateForm(instance=wt_rate)
        brentrate_form       = BrentrateForm(instance=brentrate)
        value_added_surcharge = ValueCargoHandlingChargeForm(instance=fs_rate)

        return render_to_response('customer/edit_customer_details.html',{'formset':formset,
                                                                            'brentrate_form':brentrate_form,
                                                                            'value_added_surcharge':value_added_surcharge,
                                                                            'customer_id':customer_id,
                                                                            },context_instance=RequestContext(request))

def edit_customer_weight_rate(request,c_id):
    ''' User submitted the form '''
    customer_weight_rate = CustomerWeightRate.objects.get(customer__pk=c_id)
    if request.method == 'POST':
        form = CustomerWeightRateForm(request.POST,instance=customer_weight_rate)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/customer/weightrate/')
        else:
            return render_to_response('customer/add_customer_weight_rate.html', {'form':form}, context_instance=RequestContext(request))

    else:
        ''' User in not submitting form , set object to the form '''
        form    = CustomerWeightRateForm(instance=customer_weight_rate)
        return render_to_response('customer/add_customer_weight_rate.html',{'form':form},context_instance=RequestContext(request))






def add_customer_other_details(request,customer_id):
    ''' User submitted the form '''
    if request.method == 'POST':
        branded_staff_rate_form    = BrandedStaffRateForm(request.POST)
        branded_vehicle_rate_form       = BrandedVehicleRateForm(request.POST)
        standard_operating_procedure_form = StandardOperatingProcedureForm(request.POST)

        for form in ( branded_staff_rate_form,branded_vehicle_rate_form,standard_operating_procedure_form):
            if form.is_valid():
                form.save(commit=False)
            else:
                myform = render_to_string('customer/add_customer_other_details.html', {'branded_staff_rate_form':branded_staff_rate_form,
                                                                            'branded_vehicle_rate_form':branded_vehicle_rate_form,
                                                                            'standard_operating_procedure_form':standard_operating_procedure_form,
                                                                            'customer_id':customer_id,
                                                                            }, context_instance=RequestContext(request))
                return HttpResponse("%s" % myform)

        customer = Customer.objects.get(pk=customer_id)

        BrandedStaffRate.objects.get_or_create(         staff_type=branded_staff_rate_form.cleaned_data['staff_type'],
                                                         staff_rate = branded_staff_rate_form.cleaned_data['staff_rate'],
                                                         customer = customer,
                                                          )

        BrandedVehicleRate.objects.get_or_create(   vehicle_type = branded_vehicle_rate_form.cleaned_data['vehicle_type'],
                                                    vehicle_rate = branded_vehicle_rate_form.cleaned_data['vehicle_rate'],
                                                    customer = customer,
                                                    )

        #standard_operating_procedure_form.save()
        StandardOperatingProcedure.objects.get_or_create( customer =customer,
                                                          attempts = standard_operating_procedure_form.cleaned_data['attempts'],
                                                          wait = standard_operating_procedure_form.cleaned_data['wait'],
                                                          return_to_origin = standard_operating_procedure_form.cleaned_data['return_to_origin'],
                                                         )

        return HttpResponseRedirect('/customer/otherdetailsrate/'+str(customer_id)+ '/add/')

    else:
        ''' User in not submitting form , reset the form '''
        branded_staff_rate_form    = BrandedStaffRateForm(initial={'customer':customer_id})
        branded_vehicle_rate_form       = BrandedVehicleRateForm(initial={'customer':customer_id})
        standard_operating_procedure_form = StandardOperatingProcedureForm(initial={'customer':customer_id})

        return render_to_response('customer/add_customer_other_details.html',{'branded_staff_rate_form':branded_staff_rate_form,
                                                                            'branded_vehicle_rate_form':branded_vehicle_rate_form,
                                                                            'standard_operating_procedure_form':standard_operating_procedure_form,
                                                                            'customer_id':customer_id,
                                                                            },context_instance=RequestContext(request))


#third page staff  and types and all
def edit_customer_other_details(request,customer_id):
    ''' User submitted the form '''
    if request.method == 'POST':
        customer  = Customer.objects.get(pk=customer_id)
        b_staff = BrandedStaffRate.objects.get(customer=customer)
        b_vehicle   = BrandedVehicleRate.objects.get(customer=customer)
        sop   = StandardOperatingProcedure.objects.get(customer=customer)

        branded_staff_rate_form     = BrandedStaffRateForm(request.POST,instance=b_staff)
        branded_vehicle_rate_form   = BrandedVehicleRateForm(request.POST,instance=b_vehicle)
        standard_operating_procedure_form = StandardOperatingProcedureForm(request.POST,instance=sop)

        for form in (branded_staff_rate_form,branded_vehicle_rate_form,standard_operating_procedure_form):
            if form.is_valid():
                form.save(commit=False)
            else:
                myform = render_to_string('customer/edit_customer_other_details.html', {'branded_staff_rate_form':branded_staff_rate_form,
                                                                            'branded_vehicle_rate_form':branded_vehicle_rate_form,
                                                                            'standard_operating_procedure_form':standard_operating_procedure_form,
                                                                            'customer_id':customer_id,
                                                                            }, context_instance=RequestContext(request))
                return HttpResponse("%s" % myform)

        branded_staff_rate_form.save()
        branded_vehicle_rate_form.save()
        standard_operating_procedure_form.save()

        return HttpResponseRedirect('/customer/otherdetailsrate/'+str(customer_id)+ '/edit/')
        return HttpResponse("1")

    else:
        ''' User in not submitting form , reset the form '''
        customer = Customer.objects.get(pk=customer_id)
        brandedstaff = BrandedStaffRate.objects.get(customer=customer)
        b_vehicle = BrandedVehicleRate.objects.get(customer=customer)
        sop = StandardOperatingProcedure.objects.get(customer=customer)

        branded_staff_rate_form    = BrandedStaffRateForm(instance=brandedstaff)
        branded_vehicle_rate_form       = BrandedVehicleRateForm(instance=b_vehicle)
        standard_operating_procedure_form = StandardOperatingProcedureForm(instance=sop)

        return render_to_response('customer/edit_customer_other_details.html',{'branded_staff_rate_form':branded_staff_rate_form,
                                                                            'branded_vehicle_rate_form':branded_vehicle_rate_form,
                                                                            'standard_operating_procedure_form':standard_operating_procedure_form,
                                                                            'customer_id':customer_id,
                                                                            },context_instance=RequestContext(request))







def add_customer_otherdetails_rate(request,customer_id):
    ''' User submitted the form '''
    if request.method == 'POST':
        numberof_branded_staff_form = NumberOfBrandedStaffForm(request.POST)
        numberof_vehicle_form       = NumberOfVehicleForm(request.POST)
        remmitance_cycle_COD_Form   = RemmitanceCycleForCODForm(request.POST)

        for form in ( numberof_branded_staff_form,numberof_vehicle_form,remmitance_cycle_COD_Form):
            if form.is_valid():
                form.save(commit=False)
            else:
                myform = render_to_string('customer/add_customer_otherdetails_rate.html', {'numberof_branded_staff_form':numberof_branded_staff_form,
                                                                            'numberof_vehicle_form':numberof_vehicle_form,
                                                                            'remmitance_cycle_COD_Form':remmitance_cycle_COD_Form,
                                                                            'customer_id':customer_id,
                                                                            }, context_instance=RequestContext(request))
                return HttpResponse("%s" % myform)

        customer = Customer.objects.get(pk=customer_id)
        numberof_branded_staff_form.customer = customer
        numberof_vehicle_form.customer = customer
        remmitance_cycle_COD_Form.customer = customer

        NumberOfBrandedStaff.objects.get_or_create( staff_type=numberof_branded_staff_form.cleaned_data['staff_type'],
                                                         number_of_banded_staff = numberof_branded_staff_form.cleaned_data['number_of_banded_staff'],
                                                         customer= customer,

                                                          )

        NumberOfVehicle.objects.get_or_create(vehicle_type = numberof_vehicle_form.cleaned_data['vehicle_type'],
                                                    number_of_vehicles = numberof_vehicle_form.cleaned_data['number_of_vehicles'],
                                                    customer= customer,

                                                    )

        RemmitanceCycleForCOD.objects.get_or_create(number_fo_days = remmitance_cycle_COD_Form.cleaned_data['number_fo_days'],
                                                        frequency = remmitance_cycle_COD_Form.cleaned_data['frequency'],
                                                    customer= customer,


                                                        )

        return HttpResponse("1")

    else:
        ''' User in not submitting form , reset the form '''
        numberof_branded_staff_form    = NumberOfBrandedStaffForm()
        numberof_vehicle_form       = NumberOfVehicleForm()
        remmitance_cycle_COD_Form = RemmitanceCycleForCODForm()

        return render_to_response('customer/add_customer_otherdetails_rate.html',{'numberof_branded_staff_form':numberof_branded_staff_form,
                                                                            'numberof_vehicle_form':numberof_vehicle_form,
                                                                            'remmitance_cycle_COD_Form':remmitance_cycle_COD_Form,
                                                                            'customer_id':customer_id,
                                                                            },context_instance=RequestContext(request))






def edit_customer_otherdetails_rate(request,customer_id):
    ''' User submitted the form '''
    if request.method == 'POST':
        customers = Customer.objects.filter(pk=customer_id)
        for cust in customers:
            customer = cust
        brentrate = NumberOfBrandedStaff.objects.get(customer=customer)
        wt_rate  = NumberOfVehicle.objects.get(customer=customer)
        fs_rate  = RemmitanceCycleForCOD.objects.get(customer=customer)

        numberof_branded_staff_form    = NumberOfBrandedStaffForm(request.POST,instance=wt_rate)
        numberof_vehicle_form       = NumberOfVehicleForm(request.POST,instance=brentrate)
        remmitance_cycle_COD_Form = RemmitanceCycleForCODForm(request.POST,instance=fs_rate)

        for form in ( numberof_branded_staff_form,numberof_vehicle_form,remmitance_cycle_COD_Form):
            if form.is_valid():
                form.save(commit=False)
            else:
                myform = render_to_string('customer/edit_customer_otherdetails_rate.html', {'numberof_branded_staff_form':numberof_branded_staff_form,
                                                                            'numberof_vehicle_form':numberof_vehicle_form,
                                                                            'remmitance_cycle_COD_Form':remmitance_cycle_COD_Form,
                                                                            'customer_id':customer_id,
                                                                            }, context_instance=RequestContext(request))
                return HttpResponse("%s" % myform)

        numberof_branded_staff_form.save()
        numberof_vehicle_form.save()
        remmitance_cycle_COD_Form.save()

        return HttpResponse("1")

    else:
        ''' User in not submitting form , reset the form '''
        customer = Customer.objects.get(pk=customer_id)
        bs_rate = NumberOfBrandedStaff.objects.get(customer=customer)
        bv_rate = NumberOfVehicle.objects.get(customer=customer)
        rcod = RemmitanceCycleForCOD.objects.get(customer=customer)

        numberof_branded_staff_form    = NumberOfBrandedStaffForm(instance=bs_rate)
        numberof_vehicle_form       = NumberOfVehicleForm(instance=bv_rate)
        remmitance_cycle_COD_Form = RemmitanceCycleForCODForm(instance=rcod)

        return render_to_response('customer/edit_customer_otherdetails_rate.html',{'numberof_branded_staff_form':numberof_branded_staff_form,
                                                                            'numberof_vehicle_form':numberof_vehicle_form,
                                                                            'remmitance_cycle_COD_Form':remmitance_cycle_COD_Form,
                                                                            'customer_id':customer_id,
                                                                            },context_instance=RequestContext(request))





def activate_customer(request, c_id):
    c = Customer.objects.get(id=c_id)
    c.activation_status = True
    c.activation_date = date.today()
    c.activation_by = request.user
    c.save()
    return HttpResponseRedirect("/customer/")

def deactivate_customer(request, c_id):
    c = Customer.objects.get(id=c_id)
    c.activation_status = False
    c.activation_date = date.today()
    c.activation_by = request.user
    c.save()
    return HttpResponseRedirect("/customer/")

@csrf_exempt
def subcustomer_info(request):
    subcust_code = request.POST['subcust_code']
    subcustomer = Shipper.objects.get(id=int(subcust_code))
    subcustomer_info = {}
    address = Address.objects.get(id=subcustomer.address.id)
    pincode = Pincode.objects.get(pincode=address.pincode)
    if ShipperMapping.objects.filter(shipper=subcustomer):
            pinc = ShipperMapping.objects.get(shipper=subcustomer)
            pincode = Pincode.objects.get(pincode = pinc.forward_pincode)

    for k, v in subcustomer.get_fields():
        subcustomer_info[k]=v
    for k, v in address.get_fields():
        subcustomer_info[k]=v
    subcustomer_info['sc_id']=pincode.service_center.id
    subcustomer_info['sc_val']=str(pincode.service_center)
    subcustomer_json = json.dumps(subcustomer_info)
    return HttpResponse(subcustomer_json)

@csrf_exempt
def customer_subcustomer(request, cid):
    subcust = Shipper.objects.using('local_ecomm').filter(customer_id=cid).only('id','name').order_by('name')
    return render_to_response("customer/cust_subcustomer.html", {'subcust':subcust}, context_instance=RequestContext(request))





def customer_rates(request, c_id):
#    if request.is_ajax:
    ''' User submitted the form '''
    c = Customer.objects.get(id=c_id)
    now = datetime.now()
    #return HttpResponse("---###- %s" % now)
    if request.method == 'POST':
        upload_file = request.FILES['upload_file']
        file_contents = upload_file.read()
        rate_version = c.rateversion_set.all().order_by("-effective_date")
        if rate_version :
            rate_version = rate_version[0]
            if rate_version.active:
                rate_version = RateVersion.objects.create(customer=c, effective_date =  now)
        else:
                rate_version = RateVersion.objects.create(customer=c, effective_date =  now)
   
        if file_contents:
            import_wb = xlrd.open_workbook(file_contents=file_contents)
            import_sheet = import_wb.sheet_by_index(0)
            zones = Zone.objects.filter(id__gte=13)
            rate_master=[]
            row = 4
            end_col = 19
            for org_zone in zones:
                start_col = 3
                for dest_zone in zones :
                  if row < 38: 
                    first_500gm = import_sheet.cell_value(rowx=row, colx=start_col)
                    add_500gm = import_sheet.cell_value(rowx=row+1, colx=start_col)

                    if dest_zone.code in ['CB','CH', 'CC'] and org_zone.code in  ['CB','CH', 'CC']:
                        if dest_zone.code <> org_zone.code:
                            first_500gm = import_sheet.cell_value(rowx=row, colx=11)
                            add_500gm = import_sheet.cell_value(rowx=row+1, colx=11)

                    rate_master.append("%s, %s, %s, %s<br>" % (org_zone, dest_zone, first_500gm, add_500gm))
                    if not first_500gm:
                        first_500gm = 0
                    if not add_500gm:
                        add_500gm = 0
                    ff_rate_500gm = ForwardFreightRate.objects.get_or_create(version = rate_version, slab=500, range_from = 0, range_to=500, org_zone = org_zone, dest_zone=dest_zone, mode_id = 1)
                    ff_rate_500gm = ff_rate_500gm[0]
                    ff_rate_500gm.rate_per_slab = first_500gm
                    ff_rate_add500gm = ForwardFreightRate.objects.get_or_create(version = rate_version, slab=500, range_from = 501, range_to=9999999, org_zone = org_zone, dest_zone=dest_zone, mode_id = 1)
                    ff_rate_add500gm = ff_rate_add500gm[0]
                    ff_rate_add500gm.rate_per_slab = add_500gm

                    ff_rate_500gm.save()
                    ff_rate_add500gm.save()
                  
                    if dest_zone.code not in ['CB','CH']:
                        start_col +=1 
                if org_zone.code not in ['CB','CH']:
                    row += 2
                    rate_master.append("=============%s, %s, %s, %s<br>" % (org_zone, dest_zone, row, start_col))
            return HttpResponse("Zones Updated Successfully" )
            # Rate updates
            #return HttpResponse("---###- %d" % import_sheet.nrows)

    return render_to_response('customer/customer_rates.html',{ 'rates': c.rateversion_set.all().order_by("-effective_date"),
                                                                'c': c,
                                                                },context_instance=RequestContext(request))




def customer_rates_v2(request, c_id):
#    if request.is_ajax:
    ''' User submitted the form '''
    c = Customer.objects.get(id=c_id)
    now = datetime.now()
    #return HttpResponse("---###- %s" % now)
    if request.method == 'POST':
        upload_file = request.FILES['upload_file']
        file_contents = upload_file.read()
        rate_version = c.rateversion_set.all().order_by("-effective_date")
        if rate_version :
            rate_version = rate_version[0]
            if rate_version.active:
                rate_version = RateVersion.objects.create(customer=c, effective_date =  now)
        else:
                rate_version = RateVersion.objects.create(customer=c, effective_date =  now)
   
        if file_contents:
            import_wb = xlrd.open_workbook(file_contents=file_contents)
            import_sheet = import_wb.sheet_by_index(0)
            zones = Zone.objects.filter(id__gte=13)
            rate_master=[]
            row = 3
            end_col = 19
            for org_zone in zones:
                start_col = 3
                for dest_zone in zones :
                  if row < 53: 
                    first_250gm = import_sheet.cell_value(rowx=row, colx=start_col)
                    first_500gm = import_sheet.cell_value(rowx=row+1, colx=start_col) - first_250gm
                    add_500gm = import_sheet.cell_value(rowx=row+2, colx=start_col)
                    #return HttpResponse("%s, %s, %s" % (first_250gm, first_500gm, add_500gm))
                    if dest_zone.code in ['CB','CH', 'CC'] and org_zone.code in  ['CB','CH', 'CC']:
                        if dest_zone.code <> org_zone.code:
                            first_250gm = import_sheet.cell_value(rowx=row, colx=11)
                            first_500gm = import_sheet.cell_value(rowx=row+1, colx=11) - first_250gm
                            add_500gm = import_sheet.cell_value(rowx=row+2, colx=11)

                    rate_master.append("%s, %s, %s, %s<br>" % (org_zone, dest_zone, first_500gm, add_500gm))
                    if not first_500gm:
                        first_500gm = 0
                    if not add_500gm:
                        add_500gm = 0
                    ff_rate_250gm = ForwardFreightRate.objects.get_or_create(version = rate_version, slab=250, range_from = 0, range_to=250, org_zone = org_zone, dest_zone=dest_zone, mode_id = 1)
                    ff_rate_500gm = ForwardFreightRate.objects.get_or_create(version = rate_version, slab=250, range_from = 251, range_to=500, org_zone = org_zone, dest_zone=dest_zone, mode_id = 1)
                    ff_rate_250gm = ff_rate_250gm[0]
                    ff_rate_500gm = ff_rate_500gm[0]
                    ff_rate_250gm.rate_per_slab = first_250gm
                    ff_rate_500gm.rate_per_slab = first_500gm
                    ff_rate_add500gm = ForwardFreightRate.objects.get_or_create(version = rate_version, slab=500, range_from = 501, range_to=9999999, org_zone = org_zone, dest_zone=dest_zone, mode_id = 1)
                    ff_rate_add500gm = ff_rate_add500gm[0]
                    ff_rate_add500gm.rate_per_slab = add_500gm

                    ff_rate_250gm.save()
                    ff_rate_500gm.save()
                    ff_rate_add500gm.save()
                  
                    if dest_zone.code not in ['CB','CH']:
                        start_col +=1 
                if org_zone.code not in ['CB','CH']:
                    row += 3
                    rate_master.append("=============%s, %s, %s, %s<br>" % (org_zone, dest_zone, row, start_col))
            return HttpResponse("Zones Updated Successfully" )
            # Rate updates
            #return HttpResponse("---###- %d" % import_sheet.nrows)

    return render_to_response('customer/customer_rates.html',{
                                                                'rates': c.rateversion_set.all().order_by("-effective_date"),
                                                                'c': c,
                                                                },context_instance=RequestContext(request))


def customer_rates_v4(request, c_id):
#    if request.is_ajax:
    ''' User submitted the form '''
    c = Customer.objects.get(id=c_id)
    now = datetime.now()
    #return HttpResponse("---###- %s" % now)
    if request.method == 'POST':
        upload_file = request.FILES['upload_file']
        file_contents = upload_file.read()
        rate_version = c.rateversion_set.all().order_by("-effective_date")
        if rate_version :
            rate_version = rate_version[0]
            if rate_version.active:
                rate_version = RateVersion.objects.create(customer=c, effective_date =  now)
        else:
                rate_version = RateVersion.objects.create(customer=c, effective_date =  now)
   
        if file_contents:
            import_wb = xlrd.open_workbook(file_contents=file_contents)
            import_sheet = import_wb.sheet_by_index(0)
            zones = Zone.objects.filter(id__gte=13)
            rate_master=[]
            row = 3
            end_col = 19
            for org_zone in zones:
                start_col = 15
                for dest_zone in zones :
                    if row == 39: 
                        row += 3
                    if row < 56: 
                        first_250gm = import_sheet.cell_value(rowx=row, colx=start_col)
                        first_500gm = import_sheet.cell_value(rowx=row+1, colx=start_col) - first_250gm
                        add_500gm = import_sheet.cell_value(rowx=row+2, colx=start_col)
                        #return HttpResponse("%s, %s, %s" % (first_250gm, first_500gm, add_500gm))
                        rate_master.append("%s, %s, %s, %s<br>" % (org_zone, dest_zone, first_500gm, add_500gm))
                        if not first_500gm:
                            first_500gm = 0
                        if not add_500gm:
                            add_500gm = 0
                        ff_rate_250gm = FreightSlabOriginZone.objects.get_or_create(customer = rate_version.customer, slab=250, range_from = 0, range_to=250, org_zone = org_zone, city_dest_id=21, mode_id = 1)
                        ff_rate_500gm = FreightSlabOriginZone.objects.get_or_create(customer = rate_version.customer, slab=250, range_from = 251, range_to=500, org_zone = org_zone, city_dest_id=21, mode_id = 1)
                        ff_rate_250gm = ff_rate_250gm[0]
                        ff_rate_500gm = ff_rate_500gm[0]
                        ff_rate_250gm.rate_per_slab = first_250gm
                        ff_rate_500gm.rate_per_slab = first_500gm
                        ff_rate_add500gm = FreightSlabOriginZone.objects.get_or_create(customer = rate_version.customer, slab=500, range_from = 501, range_to=9999999, org_zone = org_zone, city_dest_id=21, mode_id = 1)
                        ff_rate_add500gm = ff_rate_add500gm[0]
                        ff_rate_add500gm.rate_per_slab = add_500gm
                       
                        ff_rate_250gm.save()
                        ff_rate_500gm.save()
                        ff_rate_add500gm.save()
                    
                      #if dest_zone.code not in ['CB','CH']:
                          #start_col +=1 
                if org_zone.code not in ['CB','CH']:
                    row += 3
                    rate_master.append("=============%s, %s, %s, %s<br>" % (org_zone, dest_zone, row, start_col))

            start_col = 3

            for dest_zone in zones:
                #for dest_zone in zones :
                  row = 39
                  if start_col == 15:
                      start_col += 1
                  first_250gm = import_sheet.cell_value(rowx=row, colx=start_col)
                  first_500gm = import_sheet.cell_value(rowx=row+1, colx=start_col) - first_250gm
                  add_500gm = import_sheet.cell_value(rowx=row+2, colx=start_col)
                  #return HttpResponse("%s, %s, %s" % (first_250gm, first_500gm, add_500gm))
                  rate_master.append("%s, %s, %s, %s<br>" % (org_zone, dest_zone, first_500gm, add_500gm))
                  if not first_500gm:
                      first_500gm = 0
                  if not add_500gm:
                      add_500gm = 0
                  ff_rate_250gm = FreightSlabDestZone.objects.get_or_create(customer = rate_version.customer, slab=250, range_from = 0, range_to=250, dest_zone = dest_zone, city_org_id=21, mode_id = 1)
                  ff_rate_500gm = FreightSlabDestZone.objects.get_or_create(customer = rate_version.customer, slab=250, range_from = 251, range_to=500, dest_zone = dest_zone, city_org_id=21, mode_id = 1)
                  ff_rate_250gm = ff_rate_250gm[0]
                  ff_rate_500gm = ff_rate_500gm[0]
                  ff_rate_250gm.rate_per_slab = first_250gm
                  ff_rate_500gm.rate_per_slab = first_500gm
                  ff_rate_add500gm = FreightSlabDestZone.objects.get_or_create(customer = rate_version.customer, slab=500, range_from = 501, range_to=9999999, dest_zone = dest_zone, city_org_id=21, mode_id = 1)
                  ff_rate_add500gm = ff_rate_add500gm[0]
                  ff_rate_add500gm.rate_per_slab = add_500gm
                  
                  ff_rate_250gm.save()
                  ff_rate_500gm.save()
                  ff_rate_add500gm.save()
                  
                  if dest_zone.code not in ['CB','CH']:
                        start_col +=1 

            row = 39
            start_col = 15
            first_250gm = import_sheet.cell_value(rowx=row, colx=start_col)
            first_500gm = import_sheet.cell_value(rowx=row+1, colx=start_col) - first_250gm
            add_500gm = import_sheet.cell_value(rowx=row+2, colx=start_col)
            #return HttpResponse("%s, %s, %s" % (first_250gm, first_500gm, add_500gm))
            rate_master.append("%s, %s, %s, %s<br>" % (org_zone, dest_zone, first_500gm, add_500gm))
            if not first_500gm:
                first_500gm = 0
            if not add_500gm:
                add_500gm = 0
            ff_rate_250gm = FreightSlabCity.objects.get_or_create(customer = rate_version.customer, slab=250, range_from = 0, range_to=250, city_dest_id = 21, city_org_id=21, mode_id = 1)
            ff_rate_500gm = FreightSlabCity.objects.get_or_create(customer = rate_version.customer, slab=250, range_from = 251, range_to=500, city_dest_id = 21, city_org_id=21, mode_id = 1)
            ff_rate_250gm = ff_rate_250gm[0]
            ff_rate_500gm = ff_rate_500gm[0]
            ff_rate_250gm.rate_per_slab = first_250gm
            ff_rate_500gm.rate_per_slab = first_500gm
            ff_rate_add500gm = FreightSlabCity.objects.get_or_create(customer = rate_version.customer, slab=500, range_from = 501, range_to=9999999, city_dest_id = 21, city_org_id=21, mode_id = 1)
            ff_rate_add500gm = ff_rate_add500gm[0]
            ff_rate_add500gm.rate_per_slab = add_500gm
            
            ff_rate_250gm.save()
            ff_rate_500gm.save()
            ff_rate_add500gm.save()
            
            return HttpResponse("Zones Updated Successfully" )
            # Rate updates
            #return HttpResponse("---###- %d" % import_sheet.nrows)

    return render_to_response('customer/customer_rates.html',{
                                                                'rates': c.rateversion_set.all().order_by("-effective_date"),
                                                                'c': c,
                                                                },context_instance=RequestContext(request))



def customer_rates_v3(request, c_id):
#    if request.is_ajax:
    ''' User submitted the form '''
    c = Customer.objects.get(id=c_id)
    now = datetime.now()
    #return HttpResponse("---###- %s" % now)
    if request.method == 'POST':
        upload_file = request.FILES['upload_file']
        file_contents = upload_file.read()
        rate_version = c.rateversion_set.all().order_by("-effective_date")
        if rate_version :
            rate_version = rate_version[0]
            if rate_version.active:
                rate_version = RateVersion.objects.create(customer=c, effective_date =  now)
        else:
                rate_version = RateVersion.objects.create(customer=c, effective_date =  now)
   
        if file_contents:
            import_wb = xlrd.open_workbook(file_contents=file_contents)
            import_sheet = import_wb.sheet_by_index(0)
            zones = Zone.objects.filter(id__gte=13)
            rate_master=[]
            row = 3
            end_col = 19
            for org_zone in zones:
                start_col = 3
                for dest_zone in zones :
                  if row < 53: 
                    first_750gm = import_sheet.cell_value(rowx=row, colx=start_col)
                    first_500gm = import_sheet.cell_value(rowx=row+1, colx=start_col) - first_750gm
                    add_500gm = import_sheet.cell_value(rowx=row+2, colx=start_col)
                    #return HttpResponse("%s, %s, %s" % (first_250gm, first_500gm, add_500gm))
                    if dest_zone.code in ['CB','CH', 'CC'] and org_zone.code in  ['CB','CH', 'CC']:
                        if dest_zone.code <> org_zone.code:
                            first_750gm = import_sheet.cell_value(rowx=row, colx=11)
                            first_500gm = import_sheet.cell_value(rowx=row+1, colx=11) - first_750gm
                            add_500gm = import_sheet.cell_value(rowx=row+2, colx=11)

                    rate_master.append("%s, %s, %s, %s<br>" % (org_zone, dest_zone, first_500gm, add_500gm))
                    if not first_500gm:
                        first_500gm = 0
                    if not add_500gm:
                        add_500gm = 0
                    ff_rate_750gm = ForwardFreightRate.objects.get_or_create(version = rate_version, slab=750, range_from = 0, range_to=750, org_zone = org_zone, dest_zone=dest_zone, mode_id = 1)
                    ff_rate_500gm = ForwardFreightRate.objects.get_or_create(version = rate_version, slab=750, range_from = 251, range_to=1000, org_zone = org_zone, dest_zone=dest_zone, mode_id = 1)
                    ff_rate_750gm = ff_rate_750gm[0]
                    ff_rate_500gm = ff_rate_500gm[0]
                    ff_rate_750gm.rate_per_slab = first_750gm
                    ff_rate_500gm.rate_per_slab = first_500gm
                    ff_rate_add500gm = ForwardFreightRate.objects.get_or_create(version = rate_version, slab=500, range_from = 501, range_to=9999999, org_zone = org_zone, dest_zone=dest_zone, mode_id = 1)
                    ff_rate_add500gm = ff_rate_add500gm[0]
                    ff_rate_add500gm.rate_per_slab = add_500gm

                    ff_rate_750gm.save()
                    ff_rate_500gm.save()
                    ff_rate_add500gm.save()
                  
                    if dest_zone.code not in ['CB','CH']:
                        start_col +=1 
                if org_zone.code not in ['CB','CH']:
                    row += 3
                    rate_master.append("=============%s, %s, %s, %s<br>" % (org_zone, dest_zone, row, start_col))
            return HttpResponse("Zones Updated Successfully" )
            # Rate updates
            #return HttpResponse("---###- %d" % import_sheet.nrows)

    return render_to_response('customer/customer_rates.html',{
                                                                'rates': c.rateversion_set.all().order_by("-effective_date"),
                                                                'c': c,
                                                                },context_instance=RequestContext(request))

@csrf_exempt
def download_rates(request):
    if request.POST['id']:
       tmp=request.POST['id']
       rate_version=RateVersion.objects.get(id=tmp)
       data=[]
       ffw=ForwardFreightRate.objects.filter(version=rate_version)      
       header=("From Zone","To Zone","range_from","range_to","slab","Rate per slab","customer","activation status","activation date") 
       customer=rate_version.customer
       status=rate_version.active
       eff_date=rate_version.effective_date.strftime("%d-%m-%Y")
       for f in ffw:
          u=(f.org_zone,f.dest_zone,f.range_from,f.range_to,f.slab,f.rate_per_slab,customer,status,eff_date)
          data.append(u)
       report=ReportGenerator('customer_rates_{0}.xlsx'.format(tmp))
       report.write_header(header) 
       path=report.write_body(data)
       file_link = settings.ROOT_URL + 'static/uploads/reports/' +path
       return HttpResponse(file_link)



@csrf_exempt
def update_customer(request):
     if request.POST['id']:
           tmp=request.POST['id']
           rate_version=RateVersion.objects.get(id=tmp)
           val = rate_version.active
           RateVersion.objects.filter(customer=rate_version.customer).update(active=False)
           val = not val
           RateVersion.objects.filter(id=tmp).update(active=val)
           return HttpResponse(tmp)
     return HttpResponse("coming here")



@csrf_exempt
def update_rate_dates(request):
   if request.POST['id']:
      tmp=request.POST['id']
      rate_version=RateVersion.objects.get(id=tmp)
      val = rate_version.active
      date=request.POST['date']
      rates= RateVersion.objects.filter(customer=rate_version.customer,effective_date=date)
      if not rates:
             RateVersion.objects.filter(id=tmp).update(effective_date=date)
             return HttpResponse("Updated")


def update_hike_ui(request,c_id):
    #rate_version = c.rateversion_set.all().order_by("-effective_date")
    if request.POST['percent_hike']:
        percent_hike=request.POST['percent_hike']
        update_hike(c_id,percent_hike)
    return HttpResponse("Updated")


def update_hike(customer_id, percent_hike):
    #rate_version = c.rateversion_set.all().order_by("-effective_date")
    c = Customer.objects.get(id=customer_id)
    rate_version = RateVersion.objects.get_or_create(customer=c, active=0)
    rate_version = rate_version[0]
    #rate_version.effective_date = effective_date
    rate_version.effective_date = datetime.now()
    rate_version.save()
    current_rate_version = RateVersion.objects.filter(customer_id=customer_id, active=1).latest("effective_date")
    for ff in current_rate_version.forwardfreightrate_set.all():
        newff = ForwardFreightRate.objects.get_or_create(version = rate_version, mode=ff.mode, slab = ff.slab, range_from =ff.range_from, range_to = ff.range_to, org_zone = ff.org_zone, dest_zone = ff.dest_zone)
        if newff:
            newff = newff[0]
        else:
            return HttpResponse("error")
        newff.rate_per_slab = float(ff.rate_per_slab) * (1+(float(percent_hike)/ 100)) 
        newff.save()
    return HttpResponse("Updated")

