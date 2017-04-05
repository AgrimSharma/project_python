# Create your views here.
from service_centre.models import *
from wb_entry_tax.models  import *
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt   
from django.template.loader import render_to_string
from wb_entry_tax.wb_tax_reports import get_invoice_summary, get_octroi_excel_report, get_octroi_pdf_report
from custom_entry_tax.models import *

@csrf_exempt
def wb_entry_tax(request):
   if request.is_ajax():
     # total_ship = request.POST['total_ship']
     # oct_slip_no = request.POST['oct_slip_no']
      date = request.POST.get('oct_date')
      date = datetime.date.today() if not date else date
      #ship = WestBengalAirportConfirmation.objects.filter(status=0)
      ship=CustomEntryTaxConfirmation.objects.filter(status=0,custom_entrytax__tax_name__service_center=request.user.employeemaster.service_centre)
      if not ship:
         return HttpResponse("No shipments for EntryTax")
      tax = CustomTaxBilling.objects.create(date = date, origin=request.user.employeemaster.service_centre)
      for a in ship:
                CustomTaxShipments.objects.create(wb_tax=tax, shipment=a.shipment, shipper=a.shipment.shipper, origin=a.origin)
                CustomEntryTaxConfirmation.objects.filter(id=a.id,custom_entrytax__tax_name__service_center=request.user.employeemaster.service_centre).update(status=1,updated_on=now)
                #WestBengalAirportConfirmation.objects.filter(id=a.id).update(status=1, updated_on=now)
      return render_to_response("wb_entry_tax/tax_data.html",
                        {"a":tax},)
    #  return HttpResponse("Success")
   else:
      if request.user.employeemaster.employee_code in ['124']:
         tax = WBTax.objects.filter().order_by('-id')
      else:
          tax = WBTax.objects.filter(origin=request.user.employeemaster.service_centre).order_by('-id')
      shipper = Customer.objects.all()

   return render_to_response("wb_entry_tax/wb_entry_tax.html",
                                  {"octroi":tax,
                                   'shipper':shipper},
                                  # 'origin_sc':request.user.employeemaster.service_centre},
                                  context_instance=RequestContext(request))


@csrf_exempt
def mycustomer(request, cid):
   customer = Customer.objects.get(id=cid)
   #octroi_form = OctroiBillingForm(initial={"customer":customer.pk})
   octroi_billings=CustomTaxBilling.objects.filter(customer=customer).order_by('-id')[:10]
   unbilled_ship_count = CustomTaxShipments.objects.filter(shipper=customer, status=1).exclude(receipt_number="").only('id').count()

   return render_to_response("wb_entry_tax/customer.html",
                    {'customer':customer,
                     'unbilled_ship_count':unbilled_ship_count,
                     #'octroi_form':octroi_form,
                     'octroi_billings':octroi_billings},
                    context_instance=RequestContext(request))
   return HttpRequest('coming here ')

@csrf_exempt
def entry_tax(request):
   if request.is_ajax():
     # total_ship = request.POST['total_ship']
     # oct_slip_no = request.POST['oct_slip_no']
      date = request.POST.get('oct_date')
      date = datetime.date.today() if not date else date
      ship=CustomEntryTaxConfirmation.objects.filter(status=0,custom_entrytax__tax_name__service_center=request.user.employeemaster.service_centre)
      #ship = WestBengalAirportConfirmation.objects.filter(status=0)
      if not ship:
         return HttpResponse("No shipments for Entry Tax")
      # tax = WBTax.objects.create(date = date, origin=request.user.employeemaster.service_centre)
      tax=CustomTax.objects.create(date=date,origin=request.user.employeemaster.service_centre)
      for a in ship:
                CustomTaxShipments.objects.create(custom_entrytax=tax,shipment=a.shipment,shipper=a.shipment,origin=a.origin)
                #WBTaxShipments.objects.create(wb_tax=tax, shipment=a.shipment, shipper=a.shipment.shipper, origin=a.origin)
                CustomEntryTaxConfirmation.objects.filter(status=0,id=a.id,updated_on=now)
      return render_to_response("wb_entry_tax/tax_data.html",
                        {"a":oct},)
    #  return HttpResponse("Success")
   else:
      if request.user.employeemaster.service_centre.city.state.id == 13:# in ['10500','10612','11662']:
         tax =CustomTax.objects.filter().order_by('-id')
      else:
          tax = CustomTax.objects.filter(origin=request.user.employeemaster.service_centre).order_by('-id')
      shipper = Customer.objects.all()
      customer=Customer.objects.using('local_ecomm').all()
      return render_to_response("reports/west-bengal.html",
                                {                                 'customer':customer}     ,                           context_instance=RequestContext(request))
   #return render_to_response("wb_entry_tax/wb_entry_tax.html",
   #                               {"octroi":tax,
   #                                'shipper':shipper},
                                  # 'origin_sc':request.user.employeemaster.service_centre},
    #                              context_instance=RequestContext(request))

@csrf_exempt
def wbetax_billing_details(request):
#def wbetax_billing_details(request, updated):
    tax_ships = CustomTaxShipments.objects.filter(status=1, wbtaxbilling=None).exclude(receipt_number="")\
            .values('shipper').annotate(Count('shipper'))

    unbilled_customers_id = [int(d.get('shipper')) for d in tax_ships]
    all_customers = list(Customer.objects.values_list('id', flat=True))
    billed_customers_id = list(set(all_customers) - set(unbilled_customers_id))

    billed_customers = Customer.objects.filter(id__in=billed_customers_id)
    unbilled_customers = Customer.objects.filter(id__in=unbilled_customers_id)
    cust=Customer.objects.all()
    return render_to_response("wb_entry_tax/wnentrytax_billingdetails.html",
                              {'billed_customers':billed_customers,'cust':cust,
                               'unbilled_customers':unbilled_customers},
                              context_instance=RequestContext(request))

@csrf_exempt
def tax_manifest(request,oid):
    tax=WBTax.objects.get(id=oid)
    shipments=WBTaxShipments.objects.filter(wb_tax=tax)
    weight = shipments.aggregate(Sum('shipment__chargeable_weight'))
    weight = weight['shipment__chargeable_weight__sum']
    dec_value = shipments.aggregate(Sum('shipment__declared_value'))
    dec_value = dec_value['shipment__declared_value__sum']
   # bags = shipments.aggregate(Count('shipment__bags'))
   # bags = bags['shipment__bags__count']
    ls = []
    for a in shipments:
        if a.shipment.bags_set.filter(destination__city__state__id=13):
        #if a.shipment.bags_set.filter(origin__center_shortcode__in=['bmr','boc','bok','bog','bow','bot','bov','bod']):
            ls.append(a.shipment.bags_set.filter()[0])
    bags = len(set(ls))
    text = render_to_string("wb_entry_tax/manifest_txt.html",
                                  {'bags':bags,
                                   'dec_value':dec_value,
                                   'weight':weight,
                                   'shipments':shipments},
                                   context_instance=RequestContext(request))
    response =  HttpResponse("%s"%text, content_type="text/plain", mimetype='text/plain')
    #response['Content-Disposition'] = 'attachment; filename=octroi_manifest.txt'
    return response

@csrf_exempt
def wbtax_manifest(request, oid, stat):
    if stat == '1':
       tax=WBTax.objects.get(id=oid)
       shipments = WBTaxShipments.objects.filter(wb_tax=tax,destination__city__state__id=13).order_by('shipper','origin')
       ship = defaultdict(list)
       for a in shipments:
         ship[(a.shipper, a.origin)].append(a.shipment)
       file_name = "/wbtax_manifest_%s.xlsx"%(oid)  
       path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
       workbook = Workbook(path_to_save)
       c = 0
       for k in ship:
          c = c +1
          sheet = workbook.add_worksheet()
          sheet.set_column('A:H', 16)
          sheet.set_row(0, 30)
          sheet.set_row(1, 20)
          sheet.set_row(2, 20)
          #sheet.set_row(6, 30)
          #worksheet.set_row(7, 30)
          #sheet.set_column(0, 3, 12)

          sheet.set_column(4, 5, 45)
         # sheet.set_column(5, 9, 12)
          nformat = workbook.add_format()
          nformat.set_border(style=2)
          bformat = workbook.add_format({
              'bold': 1,
                    })
          bformat.set_border(style=2)
          merge_format = workbook.add_format({
              #'bold': 1,
              'align': 'center',
              'valign': 'vcenter',
              'border':'border',
                         })
          merge_format.set_border(style=2)
          sheet.merge_range('A1:D1', 'From Ecom Express Pvt Ltd %s'%(k[1]), merge_format)
          sheet.merge_range('E1:G1', "To Ecom Express Pvt Ltd, Kolkatta", merge_format)
          sheet.merge_range('A2:B2', "Manifest Number", bformat)
          sheet.merge_range('A3:B3', "Manifest Date", bformat)
          sheet.write(1, 2, str(oid)+str(c), nformat)
          sheet.write(2, 2, str(now.date()), nformat)
          sheet.write(1, 3, "Shipper Name", bformat)
          sheet.write(2, 3, "Origin Hub", bformat)
          sheet.write(1, 4, str(k[0].name), nformat)
          sheet.write(2, 4, str(k[1].center_name), nformat)
          sheet.write(1, 5, "Slip No.", bformat)
           #sheet.write(1, 6, "Amount", bformat)
          sheet.merge_range('F3:G3', "Date", bformat)
          sheet.write(3, 0, "Sr No.", bformat)
          sheet.write(3, 1, "Air Waybill No.", bformat)
          sheet.write(3, 2, "Order No.", bformat)
          sheet.write(3, 3, "Consignee Name", bformat)
          #sheet.write(3, 4, "Consignee Address", bformat)
          sheet.write(3, 4, "Product Description", bformat)
          sheet.write(3, 5, "Value", bformat)
          sheet.write(3, 6, "Bag Number", bformat)
          counter =1
          coll_val = 0
          for b in ship[k]:
                 coll_val = coll_val + b.declared_value
             # for b in v:
                 sheet.write(counter+3, 0, counter, nformat)
                 sheet.write(counter+3, 1, b.airwaybill_number, nformat)
                 sheet.write(counter+3, 2, b.order_number, nformat)
                 sheet.write(counter+3, 3, b.consignee, nformat)
#                 sheet.write(counter+3, 4, u'%s, %s, %s'%(b.consignee_address1, b.consignee_address2, b.consignee_address3), nformat)
                 sheet.write(counter+3, 4, b.item_description[0:10], nformat)
                 sheet.write(counter+3, 5, b.declared_value, nformat)
                 if b.shipment_data.all():
                     sheet.write(counter+3, 6, b.shipment_data.all()[0].bag_number, nformat)
                 counter = counter+1
          sheet.write(1, 6, "Amount: %s"%(coll_val), bformat)
     # sheet.write(0, 1, spid[0].pickedup_by.employee_code)
       workbook.close()
       return HttpResponseRedirect("/static/uploads/%s"%(file_name))




@csrf_exempt
#def wb_entry_tax_billing_details(request, updated):
def wb_entry_tax_billing_details(request):
    tax_ships = WBTaxShipments.objects.filter(status=1, wbtaxbilling=None).exclude(receipt_number="")\
            .values('shipper').annotate(Count('shipper'))

    unbilled_customers_id = [int(d.get('shipper')) for d in tax_ships]
    all_customers = list(Customer.objects.values_list('id', flat=True))
    billed_customers_id = list(set(all_customers) - set(unbilled_customers_id))

    billed_customers = Customer.objects.filter(id__in=billed_customers_id)
    unbilled_customers = Customer.objects.filter(id__in=unbilled_customers_id)
    cust=Customer.objects.all()
    return render_to_response("wb_entry_tax/wnentrytax_billingdetails.html",
                              {'billed_customers':billed_customers,'cust':cust,
                               'unbilled_customers':unbilled_customers},
                              context_instance=RequestContext(request))

@csrf_exempt
def add_billing(request):
    if request.method == 'POST':
        form = OctroiBillingForm(request.POST)
        if form.is_valid():
            octroi_billing = form.save()
            if octroi_billing == None:
                return HttpResponse('There are no wb shipments in the given date range')
            return HttpResponseRedirect(reverse('wb-entry-tax-customer', kwargs={'cid':octroi_billing.customer.id}))
        else:
            return HttpResponseRedirect(reverse('wb_entry_tax'))
    else:
        return HttpResponseRedirect(reverse('wb_entry_tax'))


def invoice_summary(request, bid):
    file_name = 'wb_invoice_summary_{0}.pdf'.format(bid)
    fp = '/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/billing/{0}'.format(file_name)
    if not os.path.exists(fp):
        file_path = get_invoice_summary(bid, file_name)
    else:
        file_path = '/static/uploads/billing/{0}'.format(file_name)
    return HttpResponseRedirect(file_path)


def invoice_summary_without_header(request, bid):
    file_name = 'wb_invoice_summary_headless_{0}.pdf'.format(bid)
    fp = '/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/billing/{0}'.format(file_name)
    if not os.path.exists(fp):
        file_path = get_invoice_summary(bid, file_name, with_header=False)
    else:
        file_path = '/static/uploads/billing/{0}'.format(file_name)
    return HttpResponseRedirect(file_path)

def awb_pdf(request, bid):
    file_name = 'wb_awb_pdf_{0}.pdf'.format(bid)
    fp = '/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/billing/{0}'.format(file_name)
    if not os.path.exists(fp):
        file_path = get_octroi_pdf_report(bid)
    else:
        file_path = '/static/uploads/billing/{0}'.format(file_name)
    return HttpResponseRedirect(file_path)

def awb_excel(request, bid):
    file_name = 'wb_awb_excel_{0}.xlsx'.format(bid)
    fp = '/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/billing/{0}'.format(file_name)
    if not os.path.exists(fp):
        file_path = get_octroi_excel_report(bid)
    else:
        file_path = '/static/uploads/billing/{0}'.format(file_name)
    return HttpResponseRedirect(file_path)


def custom_billing(request):
    if request.method == 'POST':
        cid=request.POST['cid']
        oct_file = request.FILES['oct_file']
        octroi_value = request.POST['octroi_value']
        if not octroi_value == '':
            octroi_value = octroi_value
        else:
            octroi_value = 5.5

        content = oct_file.read()
        c = CustomBilling(cid, content, octroi_value)
        generate_result = c.generate_bill()
        if generate_result[0]:
            error_list = []
            error_awbs = []
        else:
            error_list = generate_result[1]['error_list']
            error_awbs = generate_result[1]['error_awbs']
        customer = Customer.objects.get(id=cid)
        octroi_form = OctroiBillingForm(initial={"customer":customer.pk})
        octroi_billings = OctroiBilling.objects.filter(customer=customer)[:10]
        unbilled_ship_count = OctroiShipments.objects.filter(shipper__id=cid, octroi_billing=None, status=1).exclude(receipt_number="").count()

        return render_to_response("octroi/customer.html",
                    {'customer':customer,
                     'unbilled_ship_count':unbilled_ship_count,
                     'octroi_form':octroi_form,
                     'octroi_billings':octroi_billings,
                     'error_list':error_list,
                     'error_awbs':error_awbs},
                    context_instance=RequestContext(request))




@csrf_exempt
def process_reports(request):
   download_list = []
   if request.method == 'POST':
        date_from=request.POST['date_from']
        date_to=request.POST['date_to']
        cust=request.POST['cust']
        report_type=request.POST['report_type']
        t = datetime.datetime.strptime(date_from, "%Y%m%d")
        date_from=t.strftime("%Y-%m-%d")
        t = datetime.datetime.strptime(date_to, "%Y%m%d")
        date_to=t.strftime("%Y-%m-%d")
        if cust=="All":
            oct_bills=OctroiBilling.objects.all()
        else:
           cust_code=cust.split("-")
           cust=Customer.objects.get(code=int(cust_code[1]))
           oct_bills=OctroiBilling.objects.filter(customer=cust)
        return HttpResponse(str(date_from))


