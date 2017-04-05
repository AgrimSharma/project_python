
#===============================================================================
# Copyright, 2012, All Rights Reserved. 
# File Name:views.py
# Project Name:ecomm
# To create views for location module
# Revision: 1
# Developer: Vish Gite
#===============================================================================


from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from location.models import Region, Zone, State, ServiceCenter, City, AreaMaster,\
    Branch, PinRoutes, Pincode
from itertools import chain
from location.forms import RegionForm, ZoneForm, StateForm, CityForm, BranchForm,\
    AreaMasterForm, ServiceCenterForm, PinRoutesForm, PincodeForm
from django.template.loader import render_to_string

from django.views.decorators.csrf import csrf_exempt                                          




def get_class_object(model_name):
    classes = [Region, Zone, State, ServiceCenter, City, AreaMaster, Branch, PinRoutes, Pincode]
    for class_name in classes:
        if class_name.__name__ == model_name:
            return class_name

#to display all location
def location(request):
    regions = Region.objects.all()
    zones   = Zone.objects.all()
    states  = State.objects.all()
    cities  = City.objects.all()
    branches= Branch.objects.all()
    areas   = AreaMaster.objects.all()
    centers = ServiceCenter.objects.all()
    pinroutes=PinRoutes.objects.all()
    pincodes= Pincode.objects.all()
    #result_list  = chain(regions,zones)
    #from django.db.models import get_model

#    classes = [Region, Zone, State, ServiceCenter, City, AreaMaster, Branch, PinRoutes, Pincode]
#    def find_class(model_name):
#        for clls in classes:
#            print clls.__name__
#            if clls.__name__ == model_name:
#                return clls
#
#    
#    model_name = 'City'
#    ClassName = find_class(model_name)
#    
#    cities =  ClassName.objects.all()
    

    return render_to_response('location/locations.html',{'branches':branches,'areas':areas,
                                                         'cities':cities,'regions':regions,
                                                         'zones':zones,'states':states,
                                                         'centers':centers,'pinroutes':pinroutes,
                                                         'pincodes':pincodes},context_instance=RequestContext(request))



@csrf_exempt
def update_table_field(request):
    ''' To update a specific field '''
    if request.method == 'POST':
        model_name = request.POST['model_name']
        row_id     = int(request.POST['row_id'])
        field_name = request.POST['field_name']
        value       = request.POST['value']  
        
        ModelName = get_class_object(model_name)
        this_model=ModelName.objects.get(pk=row_id) 
        
        #print getattr(this_model, field_name)
        this_model.__setattr__(field_name,value)
        this_model.save()
    return HttpResponseRedirect('/location/')
        



def add_location_details(request):
    ''' User submitted the form '''
    if request.method == 'POST':
        region_form = RegionForm(request.POST)
        if region_form.is_valid():
            pass
                # next = request.META.get('HTTP_REFERER', None) or '/'
                #return  HttpResponseRedirect(next)
                #return HttpResponseRedirect(urlresolvers.reverse('add_customer_weight_rate')
            return HttpResponse('1')
        else:    
                myform = render_to_string('location/add_location_details.html', {'form':region_form}, context_instance=RequestContext(request))     
                return HttpResponse("%s" % myform)
        region_form.save()
    else:
        ''' User in not submitting form , reset the form '''
        form    = RegionForm()
        return render_to_response('location/add_location_details.html',{'form':form},context_instance=RequestContext(request))



def add_zone_details(request):
    if request.method == 'POST':
        zone_form = ZoneForm(request.POST)
        if zone_form.is_valid():
            zone_form.save()
            return HttpResponse('1')
        else:    
            myform = render_to_string('location/add_zone.html', {'zone_form':zone_form}, context_instance=RequestContext(request))     
            return HttpResponse("%s" % myform)
    else:
        zone_form= ZoneForm()
        return render_to_response('location/add_zone.html',{'zone_form':zone_form},context_instance=RequestContext(request))
    


def add_state_details(request):
    if request.method == 'POST':
        state_form = StateForm(request.POST)
        if state_form.is_valid():
            state_form.save()
            return HttpResponse('1')

        else:
            myform =render_to_string('location/add_state.html', {'state_form':state_form}, context_instance=RequestContext(request))
            return HttpResponse("%s" % myform)
    else:
        state_form = StateForm()
        return render_to_response('location/add_state.html',{'state_form':state_form},context_instance=RequestContext(request))
        

def add_city_details(request):
    if request.method == 'POST':
        city_form = CityForm(request.POST)
        if city_form.is_valid():
            city_form.save()
            return HttpResponse('1')

        else:
            myform =render_to_string('location/add_city.html', {'city_form':city_form,'name':'city'}, context_instance=RequestContext(request))
            return HttpResponse("%s" % myform)
    else:
        city_form = CityForm()
        return render_to_response('location/add_city.html',{'city_form':city_form,'name':'city'},context_instance=RequestContext(request))
        

def add_branch_details(request):
    if request.method == 'POST':
        city_form = BranchForm(request.POST)
        if city_form.is_valid():
            city_form.save()
            return HttpResponse('1')

        else:
            myform =render_to_string('location/add_city.html', {'city_form':city_form,'name':'branch'}, context_instance=RequestContext(request))
            return HttpResponse("%s" % myform)
    else:
        city_form = BranchForm()
        return render_to_response('location/add_city.html',{'city_form':city_form,'name':'branch'},context_instance=RequestContext(request))



def add_area_details(request):
    if request.method == 'POST':
        form = AreaMasterForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse('1')

        else:
            myform =render_to_string('location/add_city.html', {'city_form':form,'name':'area'}, context_instance=RequestContext(request))
            return HttpResponse("%s" % myform)
    else:
        form = AreaMasterForm()
        return render_to_response('location/add_city.html',{'city_form':form,'name':'area'},context_instance=RequestContext(request))
  
      

def add_center_details(request):
    if request.method == 'POST':
        form = ServiceCenterForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse('1')

        else:
            myform =render_to_string('location/add_city.html', {'city_form':form,'name':'center'}, context_instance=RequestContext(request))
            return HttpResponse("%s" % myform)
    else:
        form = ServiceCenterForm()
        return render_to_response('location/add_city.html',{'city_form':form,'name':'center'},context_instance=RequestContext(request))
  

            
def add_pinroutes_details(request):
    if request.method == 'POST':
        form = PinRoutesForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse('1')

        else:
            myform =render_to_string('location/add_city.html', {'city_form':form,'name':'pinroute'}, context_instance=RequestContext(request))
            return HttpResponse("%s" % myform)
    else:
        form = PinRoutesForm()
        return render_to_response('location/add_city.html',{'city_form':form,'name':'pinroute'},context_instance=RequestContext(request))
  


def add_pincode_details(request):
    if request.method == 'POST':
        form = PincodeForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse('1')
        else:
            myform =render_to_string('location/add_city.html', {'city_form':form,'name':'pincode'}, context_instance=RequestContext(request))
            return HttpResponse("%s" % myform)
    else:
        form = PincodeForm()
        return render_to_response('location/add_city.html',{'city_form':form,'name':'pincode'},context_instance=RequestContext(request))
  

            

def delete_location_details(request,location_id):
    ''' user requested a delete record '''
    #model_name = get_modle_name(request)
    model_name = 'City'
    print get_class_object(model_name)
    #model_name.__class__.__name__.objects.delete(pk=location)
