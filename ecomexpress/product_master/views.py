# Create your views here.

from privateviews.decorators import login_not_required

from customer.models import Customer
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from xlsxwriter.workbook import Workbook
import xlrd

from datetime import datetime

import traceback
import sys
from customer.models import Customer

    
@login_not_required
def pim_add_update(request):
    '''Creates view for pim_add_update page.'''
    from customer.models import Customer
    customers = Customer.objects.all()
    return render_to_response("product_master/pim_add_update.html",
                              {'customers':customers},
                              context_instance=RequestContext(request))

@login_not_required
def pim_update(request):
    ''' This method takes an excel file in a specific name and updates the ProductItemMaster.'''
    ''' if squ_id exists, we have to update based on squ_id.'''
    ''' if squ_id is null: then update based on product description and client.'''
    customers = Customer.objects.all()
    pim_file = None
    if request.method == 'POST':
        try:
            pim_file = request.FILES['pim_file']
        except:
            print traceback.print_exc

        if pim_file:
            content = pim_file.read()
            wb = xlrd.open_workbook(file_contents=content)
            sheetnames = wb.sheet_names()
            sh = wb.sheet_by_name(sheetnames[0])
            product_description = sh.col_values(0)[4:]
            weight= sh.col_values(1)[4:]
            height= sh.col_values(2)[4:]
            breadth= sh.col_values(3)[4:]
            length= sh.col_values(4)[4:]
            squ_id= sh.col_values(5)[4:]
            customer_code= sh.col_values(6)[4:]    
            pim_list = zip(product_description, weight, height, breadth, length, squ_id, customer_code)
            pim_not_found = []
            count = 0
            for each_pim in pim_list:
                squ = each_pim[5]
                custom_code = int(each_pim[6])
                customer = Customer.objects.get(code=custom_code)        
                updated_pim_flag = False
                if squ:
                    pim_found = ProductItemMaster.objects.filter(squ_id=each_pim[5])
                    if pim_found:
                        #print "NOT NONE"
                        p = pim_found.update(product_description=each_pim[0], product_weight=each_pim[1], \
                                            product_height=each_pim[2], product_breadth=each_pim[3], product_length=each_pim[4], \
                                            customer=customer)
                        updated_pim_flag = True #pim updated
                
                if not squ:
                    #create squ_id?
                    from random import randint
                    from string import lowercase
                    squ_seed = randint(1, 25)
                    _squ_id = lowercase[squ_seed]+str(squ_seed)
                    try:
                        s = ProductItemMaster.objects.filter(product_description=each_pim[0], customer=customer).update( \
                                                                product_weight = each_pim[1], \
                                                                product_height = each_pim[2], product_breadth = each_pim[3], \
                                                                product_length = each_pim[4], squ_id = _squ_id)
                    except:
                        continue
                
                #if s:
                #    count += 1
                ##            update_pim(squ_id)
                #else:
                #    pim_not_found.append(squ_id)
            customers = Customer.objects.all()
            return render_to_response("product_master/pim_add_update.html",{'warnings':pim_not_found,'count':count, 'customers':customers},
                                           context_instance=RequestContext(request))
        #return render_to_response("product_master/pim_add_update.html",
                                           #context_instance=RequestContext(request))
        
        else:
            product_description = request.POST['product_description']
            weight= float(request.POST['product_weight'])
            height= float(request.POST['product_height'])
            breadth= float(request.POST['product_breadth'])
            length= float(request.POST['product_length'])
            squ_id= request.POST['squ_id']
            customer_code= request.POST['customer']
            customer = Customer.objects.get(code=customer_code)
            updated_pim_flag = False
            if squ_id:
                pim_found = ProductItemMaster.objects.filter(squ_id=squ_id)
                if pim_found:
                    s = pim_found.update(product_description=product_description, \
                    product_weight=weight, product_height=height, product_breadth=breadth, product_length=length, \
                    customer=customer)
                    updated_pim_flag = True
            
            if not squ_id or not pim_found:
                s = ProductItemMaster.objects.filter(product_description=product_description, customer=customer).update( \
                                                            product_weight = weight, \
                                                            product_height = height, product_breadth = breadth, \
                                                            product_length = length, squ_id = squ_id)
            if not updated_pim_flag:
                # create new squ_id
                from random import randint
                from string import lowercase
                squ_seed = randint(1, 25)
                _squ_id = lowercase[squ_seed]+str(squ_seed)
                # check if squ_id already in models, else create a new one.
                #new_pim, created = ProductItemMaster.objects.get_or_create(product_description=product_description, product_weight = weight, \
                                                               #product_height = height, product_breadth = breadth, \
                                                               #product_length = length, squ_id = _squ_id, customer = customer)
                new_pim, created = ProductItemMaster.objects.get_or_create(squ_id=_squ_id, defaults={'product_description':product_description, \
                                                                                               'product_weight':weight, \
                                                                                               'product_height':height, \
                                                                                               'product_breadth':breadth, \
                                                                                               'product_length':length, 'customer':customer})

                #return HttpResponse(new_pim)
            #return HttpResponse("done")
            return render_to_response("product_master/pim_add_update.html",
                              {'customers':customers},
                              context_instance=RequestContext(request))
        # write method for updating existing pim.

@login_not_required
def show_download_pim(request):
    #return render_to_response("product_master/show_download_pim.html")
    return render_to_response("product_master/show_download_pim.html", context_instance=RequestContext(request))

@login_not_required
def return_PIM(request):
    '''This method returns all ProductItemMaster items as an excel sheet.
    '''
    
    p = ProductItemMaster.objects.all()
    error_flag = False
    err_status = []
    PIM_list = []
    report_datetime = datetime.now().strftime("%d%m%Y%H%M%S%s")
    filename = '/product_item_master_report%s.xlsx' %(report_datetime)

    path_to_save = settings.FILE_UPLOAD_TEMP_DIR + filename
    workbook = Workbook(path_to_save, {'strings_to_numbers':  True})
    sheet = workbook.add_worksheet()

    sheet.write(0,2, "Product Item Master Report")

    sheet.write(3, 0, "Product Description")
    sheet.write(3, 1, "Weight")
    sheet.write(3, 2, "Height ")
    sheet.write(3, 3, "Breadth")
    sheet.write(3, 4, "length")
    sheet.write(3, 5, "squ_id")
    sheet.write(3, 6, "Customer code")
    sheet.write(3, 7, "Customer name")

    for record in p:
        item = record
        i = int(item.customer_id)
        each = ()
        try:
            this_customer = Customer.objects.get(id=i)
        except:
            err_status.append(traceback.print_exc)
            continue
        product_description = str(item.product_description)
        product_weight = item.product_weight
        product_height = item.product_height
        product_breadth = item.product_breadth
        product_length = item.product_length
        squ_id = item.squ_id
        this_customer_code = (this_customer.code)
        this_customer = str(this_customer.name)
        each = (product_description, product_weight, product_height, product_breadth, product_length, squ_id, this_customer_code, \
                this_customer)
        PIM_list.append(each)
    print err_status

    for row, each in enumerate(PIM_list, start=4):
        #print type(each)
        for column, value in enumerate(each):
            #print row, column, type(value)
            sheet.write(row, column, value)

    workbook.close()
    workbook = "file downloaded to /static/uploads :)"
    response = HttpResponse(workbook)
#    response = HttpResponse(mimetype='application/vnd.ms-excel')
#    response['Content-Disposition'] = 'attachment; filename=product_item_master_report%s.xlsx' % report_datetime
#    book.save(response)   
    return response

@login_not_required 
def show_single_pim(request):
    '''This method returns a single PIM record if the squ_id is given.'''
    if request.method == 'GET':
      s_id = request.GET.get('squ_id')
      #return HttpResponse(s_id)
    try:
        data = ProductItemMaster.objects.get(squ_id=str(s_id))
        #from django.core import serializers
        #data = serializers.serialize( "python", this_pim)
        #return HttpResponse(data)
        from django.forms.models import model_to_dict
        this_pim = model_to_dict(data)
        return render_to_response("product_master/show_single_PIM.html",
                            {'this_pim':this_pim},
                           context_instance=RequestContext(request))
    except:
        #log error
        err = traceback.print_exc
        return HttpResponse(err)
      
@login_not_required
def show_all_pims(request):
    pim_list = ProductItemMaster.objects.all()
    from django.forms.models import model_to_dict
    pim_list_dicts = [model_to_dict(item) for item in pim_list]
    return render_to_response('product_master/show_download_PIM.html',
                              {'this_pim':pim_list_dicts},
                              context_instance=RequestContext(request))
    # pagination needed.


from django.views.generic import ListView
from .models import ProductItemMaster

class ListPI(ListView):

    model = ProductItemMaster
    template_name = 'show_PIM.html'
    
    def get_context_data(self, **kwargs):
        kwargs['object_list'] = ProductItemMaster.objects.order_by('id')
        return super(ListPI, self).get_context_data(**kwargs)
