# Create your views here.
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from models import *
import sys, traceback
from django.template import RequestContext
from django.db.models import *
import string, random
import xlwt
from django.db.models import Q
import csv
from xlsxwriter.workbook import Workbook

def airwaybill_search(request):

    if request.POST:
      awb_number = request.POST['awb_number']
      try:
       awb = AirwaybillNumbers.objects.get(airwaybill_number=awb_number)
      except:
       awb = ""
      return render_to_response('airwaybill/airwaybill_search.html',
                                {"awb":awb
                                 },context_instance=RequestContext(request))
    else:
      awbc = AirwaybillCustomer.objects.filter().order_by("-created_on")
      return render_to_response('airwaybill/airwaybill_search.html',
                                {"awbc":awbc},context_instance=RequestContext(request))

def generate_airwaybills(request):
    if request.POST:
        customer_id = request.POST['customer']
        ship_type = request.POST['type']
        quantity = request.POST['quantity']
        awbc = AirwaybillCustomer.objects.create(customer_id=customer_id, type=ship_type, quantity=int(quantity))
        #return HttpRespose(ship_type)
        if int(ship_type) == 1:
            pid = PPD.objects.latest('id').id + 1
            ppds = [PPD(id=i) for i in range(pid, int(pid) + int(quantity))]
            ppd_objs = PPD.objects.bulk_create(ppds)
            ppd_ids = [p.id for p in ppd_objs]
            airs = [AirwaybillNumbers(airwaybill_number=a) for a in ppd_ids]
        elif int(ship_type) == 2:
            cid = COD.objects.latest('id').id + 1
            cods = [COD(id=i) for i in range(cid, int(cid) + int(quantity))]
            cod_objs = COD.objects.bulk_create(cods)
            cod_ids = [p.id for p in cod_objs]
            airs = [AirwaybillNumbers(airwaybill_number=a) for a in cod_ids]
        elif int(ship_type) == 3:
            cid = ReversePickup.objects.latest('id').id + 1
            cods = [ReversePickup(id=i) for i in range(cid, int(cid) + int(quantity))]
            cod_objs = ReversePickup.objects.bulk_create(cods)
            cod_ids = [p.id for p in cod_objs]
            airs = [AirwaybillNumbers(airwaybill_number=a) for a in cod_ids]
        elif int(ship_type) == 4:
            cid = PPDZero.objects.latest('id').id + 1
            cods = [PPDZero(id=i) for i in range(cid, int(cid) + int(quantity))]
            cod_objs = PPDZero.objects.bulk_create(cods)
            cod_ids = [p.id for p in cod_objs]
            airs = [AirwaybillNumbers(airwaybill_number=a) for a in cod_ids]
        elif int(ship_type) == 5:
            cid = CODZero.objects.latest('id').id + 1
            cods = [CODZero(id=i) for i in range(cid, int(cid) + int(quantity))]
            cod_objs = CODZero.objects.bulk_create(cods)
            cod_ids = [p.id for p in cod_objs]
            airs = [AirwaybillNumbers(airwaybill_number=a) for a in cod_ids]

        awbs = AirwaybillNumbers.objects.bulk_create(airs)
        awb_nums = [a.airwaybill_number for a in awbs]
        awb_objs = AirwaybillNumbers.objects.filter(airwaybill_number__in=awb_nums)
        awbc.airwaybill_number = awb_objs
        awbc.save()
        return HttpResponseRedirect("/airwaybill/airwaybill_search/")
    else:
        customer = Customer.objects.filter(activation_status=True)
        return render_to_response('airwaybill/airwaybill_generate.html',
                              {'awb_type':AWB_TYPES, 'customer':customer},
                              context_instance=RequestContext(request))

def airwaybill_download(request, aid, tid):
     awbc = AirwaybillCustomer.objects.get(id=int(aid))
     distinct_list = list(awbc.airwaybill_number.filter().values_list())
     awb_type = ""
     if awbc.type == "1":
         awb_type = "ppd"
     if awbc.type == "2":
         awb_type = "cod"

     if tid == "1":
         response = HttpResponse(mimetype='text/plain')
         response['Content-Disposition'] = 'attachment; filename="awb_prn_%s.prn"' % awb_type
         writer = csv.writer(response)
         text = 'SIZE 101.6 mm, 50.8 mm\nDIRECTION 0,0\nREFERENCE 0,0\nOFFSET 0 mm\nSET PEEL OFF\nSET CUTTER OFF\nSET TEAR ON\nCLS\nCODEPAGE 1252\nTEXT 778,199,\"ROMAN.TTF\",180,1,10,\"ORG: ______  DST: ________\"\nTEXT 372,199,\"ROMAN.TTF\",180,1,10,\"ORG: ______  DST: ________\"\nTEXT 777,47,\"0\",180,11,10,\"DATE: _______________\"\nTEXT 371,47,\"0\",180,11,10,\"DATE: _______________\"\nTEXT 777,85,\"0\",180,10,10,\"VALUE: _________________\"\nTEXT 371,85,\"0\",180,10,10,\"VALUE: _________________\"\nTEXT 777,123,\"ROMAN.TTF\",180,1,10,\"CONSIGNEE: _____________\"\nTEXT 371,123,\"ROMAN.TTF\",180,1,10,\"CONSIGNEE: _____________\"\nTEXT 778,161,\"ROMAN.TTF\",180,1,10,\"SENDER: ________________\"\nTEXT 372,161,\"ROMAN.TTF\",180,1,10,\"SENDER: ________________\"\nTEXT 709,395,\"ROMAN.TTF\",180,1,8,\"Ecom Express Pvt Ltd\"\nTEXT 303,395,\"ROMAN.TTF\",180,1,8,\"Ecom Express Pvt Ltd\"'
         text_header=render_to_string('airwaybill/prn_file_header.html',{},context_instance=RequestContext(request))
         text = ""
         book = xlwt.Workbook(encoding='utf8')
         sheet = book.add_sheet('AirwayBill')
         prn_list = []
         prn_list = distinct_list
         for a in xrange(0,len(prn_list),2):
            #awb1 = 'BARCODE 766,300,"39",53,0,180,2,5,"%s"\n'%(prn_list[a][1])
            #awb11 = 'TEXT 737,329,"ROMAN.TTF",180,1,9,"%s"\n'%(prn_list[a][1])
            #awb2 = 'BARCODE 360,300,"39",53,0,180,2,5,"%s"\n'%(prn_list[a+1][1])
            #awb22 = 'TEXT 331,329,"ROMAN.TTF",180,1,9,"%s"\n'%(prn_list[a+1][1])
             awb1 = 'BARCODE 766,300,"39",53,0,180,2,5,"%s"'%(prn_list[a][1])
             awb11 = 'TEXT 737,329,"ROMAN.TTF",180,1,9,"%s"'%(prn_list[a][1])
             awb2 = 'BARCODE 360,300,"39",53,0,180,2,5,"%s"'%(prn_list[a+1][1])
             awb22 = 'TEXT 331,329,"ROMAN.TTF",180,1,9,"%s"'%(prn_list[a+1][1])
             text_barcode=render_to_string('airwaybill/prn_file_barcode.html',{'b1':prn_list[a][1], 'b2':prn_list[a+1][1]},context_instance=RequestContext(request))

             p = "PRINT 1,1\n"
             writer.writerow([text_header])
             text = text+text_header
             text = text+text_barcode
             writer.writerow([awb1])
             writer.writerow([awb11])
             writer.writerow([awb2])
             writer.writerow([awb22])
             writer.writerow([p])
         #return response
         response.write(text)
         #return HttpResponse("%s"%text, content_type="text/plain", mimetype='text/plain')
         response_prn =  HttpResponse("%s"%text, content_type="text/plain", mimetype='text/plain')
         response_prn['Content-Disposition'] = 'attachment; filename=airwaybill_%s.prn' % awb_type
         return response_prn
     elif tid == "2":
          file_name = "/awb_%s_%s.xlsx"%( awb_type, datetime.datetime.now().strftime("%d%m%Y%H%M%S%s") )
          path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
          workbook = Workbook(path_to_save)

          header_format = workbook.add_format({
                     'bold': 1,
                     'align': 'center',
                     'valign': 'vcenter',
                     'fg_color': 'green'})

          plain_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter'})
          sheet = workbook.add_worksheet()

          sheet.set_column(0, 4, 12) # set c
          sheet.write(2, 1, "Air waybill", header_format)
          sheet.write(2, 2, "Status", header_format)
          for row, rowdata in enumerate(distinct_list, start=4):
                    for col, val in enumerate(rowdata, start=0):
                        if col <> 0:
                             if col==2:
                                 if val==True:
                                     val="Used"
                                 elif val == False:
                                     val = "Unused"
                                 sheet.write(row, col, str(val), plain_format)
                             else:
                                     sheet.write(row, col, str(val), plain_format)
          workbook.close()
          return HttpResponseRedirect('/static/uploads/%s'%(file_name))
