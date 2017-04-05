import xml.etree.cElementTree as ET
from xml.etree import *
from django.conf import settings

from service_centre.models import Shipment, StatusUpdate
from reports.report_api import ReportGenerator
from reports.cash_tally_customer_names import cash_tally_customer_name
from customer.models import *
from billing.models import *
from decimal import *
import datetime
import xml
TW = Decimal(10) ** -2

class InvoiceXmlReport(object):

    def __init__(self, year, month, *args, **kwargs):
        self.year = year
        self.month = month
        self.xml_file = 'invoice_xml_{0}_{1}.xml'.format(year, month)
        self.xml_file_path = '/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/reports/' + self.xml_file
        self.xml_file_web = settings.ROOT_URL + '/static/uploads/reports/'+str(self.xml_file)

    def create_invoice_xml_for_customers(self,bill_ids):
        root = ET.Element("ENVELOPE")
        for bill_id in bill_ids:
            bill_objs =  Billing.objects.get(id =bill_id )
            if bill_objs:
                path = self.create_invoice_xml(bill_objs.customer,bill_objs,root)
        tree = ET.ElementTree(root)
        tree.write(self.xml_file_path)
        return self.xml_file_web

    def create_invoice_xml(self,customer,bill_obj,root):
#        bill_objs =  Billing.objects.get(customer_id = customer.id,billing_date__year = self.year,billing_date__month = self.month)        
#        XHTML_NAMESPACE = "http://www.w3.org/1999/xhtml"
#        XHTML = "{%s}" % XHTML_NAMESPACE
#        NSMAP = {None : XHTML_NAMESPACE}
#        root = ET.Element("ENVELOPE")

#        root =ET.Element("{http://www.w3.org/1999/xhtml}html")
# 	body = ET.SubElement(root, "{http://ww/xhtml}body")

        header = ET.SubElement(root, "HEADER")
        tallyrequest = ET.SubElement(header, "TALLYREQUEST")
        body = ET.SubElement(root, "BODY")
        importdata = ET.SubElement(body, "IMPORTDATA")
        requestdesc = ET.SubElement(importdata, "REQUESTDESC")
        reportname = ET.SubElement(requestdesc, "REPORTNAME")
        reportname.text = "Vouchers"
        staticvariables = ET.SubElement(requestdesc, "STATICVARIABLES")
        svcurrentcompany = ET.SubElement(staticvariables, "SVCURRENTCOMPANY")
        svcurrentcompany.text = "Ecom Express Private Limited"

        requestdata = ET.SubElement(importdata, "REQUESTDATA")
        tallymessage1 = ET.SubElement(requestdata, "TALLYMESSAGE")

        #tallymessage1.set('xmlns',"TallyUDF")
#        tallymessage1.set('UDF',"TallyUDF")
        voucher = ET.SubElement(tallymessage1, "VOUCHER")

        voucher.set('REMOTEID', '')
        voucher.set('VCHKEY',"91f0e35f-6726-452f-bf2d-bc668305a729-0000a31f:000002a8")
        voucher.set('VCHTYPE',"Journal")
        voucher.set('ACTION',"Create")
        voucher.set('OBJVIEW',"Accounting Voucher View")

        oldauditentryids = ET.SubElement(voucher, "OLDAUDITENTRYIDS.LIST")
        oldauditentryids.set('TYPE', "Number")
        oldauditentry = ET.SubElement(oldauditentryids, "OLDAUDITENTRYIDS")
        oldauditentry.text = "-1"

        date = ET.SubElement(voucher, "DATE")
        indate = bill_obj.billing_date
        indate = indate + datetime.timedelta(days=1)
#        date.text = str(indate.year)+"-"+str(indate.month)+"-"+str(indate.day)
#        date.text = str(indate.year)+str('{:02d}'.format(indate.month))+str('{:02d}'.format(indate.day))
#        date.text = 'Dated-' + str('{:02d}'.format(indate.day))+'-'+str('{:02d}'.format(indate.month))+'-'+str(indate.year)
        date.text = indate.strftime("%Y") + indate.strftime("%m") + indate.strftime("%d")
        guid = ET.SubElement(voucher, "GUID")
        guid.text = "91f0e35f-6726-452f-bf2d-bc668305a729-00005204"

        narration = ET.SubElement(voucher, "NARRATION")
#        narration.text = str(bill_obj.customer.name)+'/'+str(bill_obj.id)+' DATED '+str(indate.year)+'-'+str(indate.month+'-'+str(indate.day)+' AGAINST SALE FOR THE M/O '+bill_obj.billing_date.strftime("%B")
        try:
            cu_obj = CustomerReportNames.objects.get(customer=bill_obj.customer)
            customer_name = cu_obj.invoice_name
        except CustomerReportNames.DoesNotExist:
            customer_name = bill_obj.customer.name


        narration.text = str(customer_name)+'/BN-'+str(bill_obj.id)+' Dated:'+str('{:02d}'.format(indate.day))+'-'+str('{:02d}'.format(indate.month))+'-'+str(indate.year)+' AGAINST SALE FOR THE M/O '+bill_obj.billing_date.strftime("%B")+str(indate.year)
        vouchertypename = ET.SubElement(voucher, "VOUCHERTYPENAME")
        vouchertypename.text = "Journal"
        vouchernumber = ET.SubElement(voucher, "VOUCHERNUMBER")
        vouchernumber.text = "1124"
        partyledgername = ET.SubElement(voucher, "PARTYLEDGERNAME")
        partyledgername.text = customer_name
        cstformissuetype = ET.SubElement(voucher, "CSTFORMISSUETYPE")
        cstformrecvtype = ET.SubElement(voucher, "CSTFORMRECVTYPE")
        fbtpaymenttype = ET.SubElement(voucher, "FBTPAYMENTTYPE")
        fbtpaymenttype.text = "Default"
        persistedview = ET.SubElement(voucher, "PERSISTEDVIEW")
        persistedview.text = "Accounting Voucher View"
        vchgstclass = ET.SubElement(voucher, "VCHGSTCLASS")
        enteredby = ET.SubElement(voucher, "ENTEREDBY")
        enteredby.text = "murari"
        diffactualqty = ET.SubElement(voucher, "DIFFACTUALQTY")
        diffactualqty.text = "No"
        audited = ET.SubElement(voucher, "AUDITED")
        audited.text = "No"
        forjobcosting = ET.SubElement(voucher, "FORJOBCOSTING")
        forjobcosting.text = "No"
        isoptional = ET.SubElement(voucher, "ISOPTIONAL")
        isoptional.text = "No"
        effectivedate = ET.SubElement(voucher, "EFFECTIVEDATE")
        #effectivedate.text = str(bill_obj.billing_date_from.year)+"-"+str(bill_obj.billing_date_from.month)+"-"+str(bill_obj.billing_date_from.day)
#        effectivedate.text = str(bill_obj.billing_date_from.year)+str('{:02d}'.format(bill_obj.billing_date_from.month))+str('{:02d}'.format(bill_obj.billing_date_from.day))
        #effectivedate.text = 'Dated-' + str('{:02d}'.format(indate.day))+'-'+str('{:02d}'.format(indate.month))+'-'+str(indate.year)
        effectivedate.text = str(indate.year) + str(indate.month) + str(indate.day)
        isforjobworkin = ET.SubElement(voucher, "ISFORJOBWORKIN")
        isforjobworkin.text = "No"
        allowconsumption = ET.SubElement(voucher, "ALLOWCONSUMPTION")
        allowconsumption.text = "No"
        useforinterest = ET.SubElement(voucher, "USEFORINTEREST")
        useforinterest.text = "No"
        useforgainloss = ET.SubElement(voucher, "USEFORGAINLOSS")
        useforgainloss.text = "No"
        useforgodowntransfer = ET.SubElement(voucher, "USEFORGODOWNTRANSFER")
        useforgodowntransfer.text = "No"
        useforcompound = ET.SubElement(voucher, "USEFORCOMPOUND")
        useforcompound.text = "No"
        alterid = ET.SubElement(voucher, "ALTERID ")
        alterid.text = "71970"
        exciseopening = ET.SubElement(voucher, "EXCISEOPENING")
        exciseopening.text = "No"
        useforfinalproduction = ET.SubElement(voucher, "USEFORFINALPRODUCTION")
        useforfinalproduction.text = "No"
        iscancelled = ET.SubElement(voucher, "ISCANCELLED")
        iscancelled.text = "No"
        hascashflow = ET.SubElement(voucher, "HASCASHFLOW")
        hascashflow.text = "No"
        ispostdated = ET.SubElement(voucher, "ISPOSTDATED")
        ispostdated.text = "No"
        usetrackingnumber = ET.SubElement(voucher, "USETRACKINGNUMBER")
        usetrackingnumber.text = "No"
        isinvoice = ET.SubElement(voucher, "ISINVOICE")
        isinvoice.text = "No"
        mfgjournal = ET.SubElement(voucher, "MFGJOURNAL")
        mfgjournal.text = "No"
        hasdiscounts = ET.SubElement(voucher, "HASDISCOUNTS")
        hasdiscounts.text = "No"
        aspayslip = ET.SubElement(voucher, "ASPAYSLIP")
        aspayslip.text = "No"
        iscostcentre = ET.SubElement(voucher, "ISCOSTCENTRE")
        iscostcentre.text = "No"
        isstxnonrealizedvch = ET.SubElement(voucher, "ISSTXNONREALIZEDVCH")
        isstxnonrealizedvch.text = "No"
        isexcisemanufactureron = ET.SubElement(voucher, "ISEXCISEMANUFACTURERON")
        isexcisemanufactureron.text = "No"
        isblankcheque = ET.SubElement(voucher, "ISBLANKCHEQUE")
        isblankcheque.text =  "No"
        isdeleted = ET.SubElement(voucher, "ISDELETED")
        isdeleted.text =  "No"
        asoriginal = ET.SubElement(voucher, "ASORIGINAL")
        asoriginal.text =  "No"
        vchisfromsync = ET.SubElement(voucher, "VCHISFROMSYNC")
        vchisfromsync.text =  "No"
        masterid  = ET.SubElement(voucher, "MASTERID ")
        masterid .text =  "37380"
        voucherkey = ET.SubElement(voucher, "VOUCHERKEY")
        voucherkey.text =  "179353539314344"
        
        oldauditentries = ET.SubElement(voucher, "OLDAUDITENTRIES.LIST")
        accountauditentries = ET.SubElement(voucher, "ACCOUNTAUDITENTRIES.LIST")
        auditentries = ET.SubElement(voucher, "AUDITENTRIES.LIST")
        invoicedelnotes = ET.SubElement(voucher, "INVOICEDELNOTES.LIST")
        invoiceorderlist = ET.SubElement(voucher, "INVOICEORDERLIST.LIST")
        invoiceindentlist = ET.SubElement(voucher, "INVOICEINDENTLIST.LIST")
        attendenceentries = ET.SubElement(voucher, "ATTENDANCEENTRIES.LIST")
        originvoicedetails = ET.SubElement(voucher, "ORIGINVOICEDETAILS.LIST")
        invoiceexportlist = ET.SubElement(voucher, "INVOICEEXPORTLIST.LIST")
        allledgerentries = ET.SubElement(voucher, "ALLLEDGERENTRIES.LIST")

        oldauditentryidslist = ET.SubElement(allledgerentries,'OLDAUDITENTRYIDS.LIST')
        oldauditentryidslist.set('TYPE',"Number")
        
        oldauditentryids = ET.SubElement(oldauditentryidslist,'OLDAUDITENTRYIDS')
        oldauditentryids.text = "-1"
        
        ledgername = ET.SubElement(allledgerentries,'LEDGERNAME')
        ledgername.text = customer_name
        gstclass = ET.SubElement(allledgerentries,'GSTCLASS')
        isdeemedpositive = ET.SubElement(allledgerentries,'ISDEEMEDPOSITIVE')
        isdeemedpositive.text ="Yes"
        ledgerformitem = ET.SubElement(allledgerentries,'LEDGERFROMITEM')
        ledgerformitem.text = "NO"
        removezeroentries = ET.SubElement(allledgerentries,'REMOVEZEROENTRIES')
        removezeroentries.text = "NO"
        ispartyledger = ET.SubElement(allledgerentries,'ISPARTYLEDGER')
        ispartyledger.text ="Yes"
        islastdeemedpositive = ET.SubElement(allledgerentries,'ISLASTDEEMEDPOSITIVE')
        islastdeemedpositive.text = "Yes"
        
        amount = ET.SubElement(allledgerentries,'AMOUNT')
        amount.text = '-'+str(int(round(Decimal(bill_obj.total_payable_charge).quantize(TW))))
        total = int(round(Decimal(bill_obj.total_payable_charge).quantize(TW)))

   #amount value
        categoryallocations = ET.SubElement(allledgerentries,'CATEGORYALLOCATIONS.LIST')
        category = ET.SubElement(categoryallocations, 'CATEGORY')
        isdeemedpositive = ET.SubElement(categoryallocations, 'ISDEEMEDPOSITIVE')
        isdeemedpositive.text = "Yes"
        costcentreallocationlist = ET.SubElement(categoryallocations, 'COSTCENTREALLOCATIONS.LIST')
        name = ET.SubElement(costcentreallocationlist, 'NAME')
        name.text = "DHQ - Head Office"
        amount = ET.SubElement(costcentreallocationlist,'AMOUNT')    
        amount.text = '-'+str(int(round(Decimal(bill_obj.total_payable_charge).quantize(TW))))
   #amount value
        
        banklocationslist = ET.SubElement(allledgerentries,'BANKALLOCATIONS.LIST')
        billallocationslist = ET.SubElement(allledgerentries,'BILLALLOCATIONS.LIST')
        
        name = ET.SubElement(billallocationslist,'NAME')
        name.text = 'BN-' + str(bill_obj.id)
        billtype = ET.SubElement(billallocationslist,'BILLTYPE')
        billtype = "New Ref"
        tdseducteeisspecialrate = ET.SubElement(billallocationslist,'TDSDEDUCTEEISSPECIALRATE')
        tdseducteeisspecialrate.text = "NO"
        amount = ET.SubElement(billallocationslist,'AMOUNT')
        amount.text = '-'+str(int(round(Decimal(bill_obj.total_payable_charge).quantize(TW))))
  #amount value
        interestcollectionlist =  ET.SubElement(billallocationslist,'INTERESTCOLLECTION.LIST')
       
        interestcollectionlist =  ET.SubElement(allledgerentries,'INTERESTCOLLECTION.LIST')
        oldauditentrieslist = ET.SubElement(allledgerentries,'OLDAUDITENTRIES.LIST')
        accountauditentries = ET.SubElement(allledgerentries,'ACCOUNTAUDITENTRIES.LIST')
        auditentrieslist = ET.SubElement(allledgerentries,'AUDITENTRIES.LIST')
        taxbillocations = ET.SubElement(allledgerentries,'TAXBILLALLOCATIONS.LIST')
        taxobjectallocations = ET.SubElement(allledgerentries,'TAXOBJECTALLOCATIONS.LIST')
        tdsexpenselocations = ET.SubElement(allledgerentries,'TDSEXPENSEALLOCATIONS.LIST')
        vatstatutorydetails = ET.SubElement(allledgerentries,'VATSTATUTORYDETAILS.LIST')
        costtrackallocations = ET.SubElement(allledgerentries,'COSTTRACKALLOCATIONS.LIST')

#2nd ALLLEDGERENTRIES.LIST
        allledgerentries = ET.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
        oldauditentryidslist = ET.SubElement(allledgerentries, "OLDAUDITENTRYIDS.LIST")
        oldauditentryids = ET.SubElement(oldauditentryidslist, "OLDAUDITENTRYIDS")
        oldauditentryids.text = "-1"
        oldauditentryidslist.set('TYPE',"Number")
       
        ledgername= ET.SubElement(allledgerentries,"LEDGERNAME")
        ledgername.text = "Service Tax on Billing"
        gstclass = ET.SubElement(allledgerentries,"GSTCLASS")
        isdeemedpositive = ET.SubElement(allledgerentries,"ISDEEMEDPOSITIVE")
        isdeemedpositive.text ="No"
        ledgerfromitem = ET.SubElement(allledgerentries,"LEDGERFROMITEM")
        ledgerfromitem.text ="No"
        removezeroentries = ET.SubElement(allledgerentries,"REMOVEZEROENTRIES")
        removezeroentries.text ="No"
        ispartyledger = ET.SubElement(allledgerentries,"ISPARTYLEDGER")
        ispartyledger.text ="No"
        islastdeemedpositive = ET.SubElement(allledgerentries,"ISLASTDEEMEDPOSITIVE")
        islastdeemedpositive.text ="No"
        amount = ET.SubElement(allledgerentries,"AMOUNT")
        s_val = bill_obj.service_tax+bill_obj.cess_higher_secondary_tax+bill_obj.education_secondary_tax
        amount.text = str(Decimal(s_val).quantize(TW))
        tax = Decimal(s_val).quantize(TW)
#amount value
        bankallocationslist = ET.SubElement(allledgerentries,"BANKALLOCATIONS.LIST")
        billallocationslist = ET.SubElement(allledgerentries,"BILLALLOCATIONS.LIST")
        intercollectionlist = ET.SubElement(allledgerentries,"INTERESTCOLLECTION.LIST")
        oldauditentrieslist = ET.SubElement(allledgerentries,"OLDAUDITENTRIES.LIST")
        accountaudientrieslist = ET.SubElement(allledgerentries,"ACCOUNTAUDITENTRIES.LIST")
        auditentrieslist = ET.SubElement(allledgerentries,"AUDITENTRIES.LIST")
        taxbillallocationslist = ET.SubElement(allledgerentries,"TAXBILLALLOCATIONS.LIST")
        taxobjectallocationslist = ET.SubElement(allledgerentries,"TAXOBJECTALLOCATIONS.LIST")
        tdsexpenseallocationslist = ET.SubElement(allledgerentries,"TDSEXPENSEALLOCATIONS.LIST")
        vatstatdetails = ET.SubElement(allledgerentries,"VATSTATUTORYDETAILS.LIST")
        costtrackallocationslist = ET.SubElement(allledgerentries,"COSTTRACKALLOCATIONS.LIST")

#3rd ALLLEDGERENTRIES.LIST
        ppd_obj = ProductBilling.objects.filter(billing=bill_obj, product__product_name='ppd')
        ppd_amount = 0
        ppd_total = 0
        if ppd_obj:
            ppd = ppd_obj[0]
            ppd_amount = ppd.total_charge_pretax
            ppd_total = Decimal(ppd_amount).quantize(TW)
        allledgerentries = ET.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
        oldauditentryidslist = ET.SubElement(allledgerentries, "OLDAUDITENTRYIDS.LIST")
        oldauditentryidslist.set('TYPE',"Number")
        oldauditentryids = ET.SubElement(oldauditentryidslist, "OLDAUDITENTRYIDS")
        oldauditentryids.text = "-1"
        ledgername= ET.SubElement(allledgerentries,"LEDGERNAME")
        ledgername.text = "Sales - Prepaid (PPD)"
        gstclass = ET.SubElement(allledgerentries,"GSTCLASS")
        isdeemedpositive = ET.SubElement(allledgerentries,"ISDEEMEDPOSITIVE")
        isdeemedpositive.text ="No"
        ledgerfromitem = ET.SubElement(allledgerentries,"LEDGERFROMITEM")
        ledgerfromitem.text ="No"
        removezeroentries = ET.SubElement(allledgerentries,"REMOVEZEROENTRIES")
        removezeroentries.text ="No"
        ispartyledger = ET.SubElement(allledgerentries,"ISPARTYLEDGER")
        ispartyledger.text ="No"
        islastdeemedpositive = ET.SubElement(allledgerentries,"ISLASTDEEMEDPOSITIVE")
        islastdeemedpositive.text ="No"
        amount = ET.SubElement(allledgerentries,"AMOUNT")
        amount.text = str(Decimal(ppd_amount).quantize(TW))
#amount value
        categoryallocattions = ET.SubElement(allledgerentries,"CATEGORYALLOCATIONS.LIST")
        category = ET.SubElement(categoryallocattions, "CATEGORY")
        category.text = "Primary Cost Category"
        isdeemedpositive = ET.SubElement(categoryallocattions, "ISDEEMEDPOSITIVE")
        isdeemedpositive.text = "No"
        costcenterallocationslist = ET.SubElement(categoryallocattions, "COSTCENTREALLOCATIONS.LIST")
        name = ET.SubElement(costcenterallocationslist, 'NAME')
        name.text = "DHQ - Head Office"
        amount = ET.SubElement(costcenterallocationslist,"AMOUNT") 
        amount.text = str(Decimal(ppd_amount).quantize(TW))
#amount value
 
        bankallocationslist = ET.SubElement(allledgerentries,"BANKALLOCATIONS.LIST")
        billallocationslist = ET.SubElement(allledgerentries,"BILLALLOCATIONS.LIST")
        intercollectionlist = ET.SubElement(allledgerentries,"INTERESTCOLLECTION.LIST")
        oldauditentrieslist = ET.SubElement(allledgerentries,"OLDAUDITENTRIES.LIST")
        accountaudientrieslist = ET.SubElement(allledgerentries,"ACCOUNTAUDITENTRIES.LIST")
        auditentrieslist = ET.SubElement(allledgerentries,"AUDITENTRIES.LIST")
        taxbillallocationslist = ET.SubElement(allledgerentries,"TAXBILLALLOCATIONS.LIST")
        taxobjectallocationslist = ET.SubElement(allledgerentries,"TAXOBJECTALLOCATIONS.LIST")
        tdsexpenseallocationslist = ET.SubElement(allledgerentries,"TDSEXPENSEALLOCATIONS.LIST")
        vatstatdetails = ET.SubElement(allledgerentries,"VATSTATUTORYDETAILS.LIST")
        costtrackallocationslist = ET.SubElement(allledgerentries,"COSTTRACKALLOCATIONS.LIST")

#4th ALLLEDGERENTRIES.LIST
        cod_obj = ProductBilling.objects.filter(billing=bill_obj, product__product_name='cod')
        cod_amount = 0
        cod_total = 0
        if cod_obj:
            cod = cod_obj[0]
            cod_amount = cod.total_charge_pretax
            cod_total = Decimal(cod_amount).quantize(TW)
        allledgerentries = ET.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
        oldauditentryidslist = ET.SubElement(allledgerentries, "OLDAUDITENTRYIDS.LIST")
        oldauditentryidslist.set('TYPE',"Number")
        oldauditentryids = ET.SubElement(oldauditentryidslist, "OLDAUDITENTRYIDS")
        oldauditentryids.text = "-1"
        ledgername= ET.SubElement(allledgerentries,"LEDGERNAME")
        ledgername.text = "Sales - Cash on Delivery (COD)"
        gstclass = ET.SubElement(allledgerentries,"GSTCLASS")
        isdeemedpositive = ET.SubElement(allledgerentries,"ISDEEMEDPOSITIVE")
        isdeemedpositive.text ="No"
        ledgerfromitem = ET.SubElement(allledgerentries,"LEDGERFROMITEM")
        ledgerfromitem.text ="No"
        removezeroentries = ET.SubElement(allledgerentries,"REMOVEZEROENTRIES")
        removezeroentries.text ="No"
        ispartyledger = ET.SubElement(allledgerentries,"ISPARTYLEDGER")
        ispartyledger.text ="No"
        islastdeemedpositive = ET.SubElement(allledgerentries,"ISLASTDEEMEDPOSITIVE")
        islastdeemedpositive.text ="No"
        amount = ET.SubElement(allledgerentries,"AMOUNT")
        amount.text = str(Decimal(cod_amount).quantize(TW))
   
#amount value
        categoryallocattions = ET.SubElement(allledgerentries,"CATEGORYALLOCATIONS.LIST")
        category = ET.SubElement(categoryallocattions, "CATEGORY")
        category.text = "Primary Cost Category"
        isdeemedpositive = ET.SubElement(categoryallocattions, "ISDEEMEDPOSITIVE")
        isdeemedpositive.text = "No"
        costcenterallocationslist = ET.SubElement(categoryallocattions, "COSTCENTREALLOCATIONS.LIST")
        name = ET.SubElement(costcenterallocationslist, 'NAME')
        name.text = "DHQ - Head Office"
        amount = ET.SubElement(costcenterallocationslist,"AMOUNT")
        amount.text = str(Decimal(cod_amount).quantize(TW))
#amount value

        bankallocationslist = ET.SubElement(allledgerentries,"BANKALLOCATIONS.LIST")
        billallocationslist = ET.SubElement(allledgerentries,"BILLALLOCATIONS.LIST")
        intercollectionlist = ET.SubElement(allledgerentries,"INTERESTCOLLECTION.LIST")
        oldauditentrieslist = ET.SubElement(allledgerentries,"OLDAUDITENTRIES.LIST")
        accountaudientrieslist = ET.SubElement(allledgerentries,"ACCOUNTAUDITENTRIES.LIST")
        auditentrieslist = ET.SubElement(allledgerentries,"AUDITENTRIES.LIST")
        taxbillallocationslist = ET.SubElement(allledgerentries,"TAXBILLALLOCATIONS.LIST")
        taxobjectallocationslist = ET.SubElement(allledgerentries,"TAXOBJECTALLOCATIONS.LIST")
        tdsexpenseallocationslist = ET.SubElement(allledgerentries,"TDSEXPENSEALLOCATIONS.LIST")
        vatstatdetails = ET.SubElement(allledgerentries,"VATSTATUTORYDETAILS.LIST")
        costtrackallocationslist = ET.SubElement(allledgerentries,"COSTTRACKALLOCATIONS.LIST")

#5th ALLLEDGERENTRIES.LIST
        ebsppd_obj = ProductBilling.objects.filter(billing=bill_obj, product__product_name='ebsppd')
        ebsppd_amount = 0
        ebsppd_total  = 0
        if ebsppd_obj:
            ebsppd = ebsppd_obj[0]
            ebsppd_amount = ebsppd.total_charge_pretax
            ebsppd_total = Decimal(ebsppd_amount).quantize(TW)
        ebsppd_amount = Decimal(ebsppd_amount).quantize(TW)
        allledgerentries = ET.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
        oldauditentryidslist = ET.SubElement(allledgerentries, "OLDAUDITENTRYIDS.LIST")
        oldauditentryidslist.set('TYPE',"Number")
        oldauditentryids = ET.SubElement(oldauditentryidslist, "OLDAUDITENTRYIDS")
        oldauditentryids.text = "-1"
        ledgername= ET.SubElement(allledgerentries,"LEDGERNAME")
        ledgername.text = "Sales - EBS Prepaid (EBS PPD)"
        gstclass = ET.SubElement(allledgerentries,"GSTCLASS")
        isdeemedpositive = ET.SubElement(allledgerentries,"ISDEEMEDPOSITIVE")
        isdeemedpositive.text ="No"
        ledgerfromitem = ET.SubElement(allledgerentries,"LEDGERFROMITEM")
        ledgerfromitem.text ="No"
        removezeroentries = ET.SubElement(allledgerentries,"REMOVEZEROENTRIES")
        removezeroentries.text ="No"
        ispartyledger = ET.SubElement(allledgerentries,"ISPARTYLEDGER")
        ispartyledger.text ="No"
        islastdeemedpositive = ET.SubElement(allledgerentries,"ISLASTDEEMEDPOSITIVE")
        islastdeemedpositive.text ="No"
        amount = ET.SubElement(allledgerentries,"AMOUNT")
        amount.text = str(ebsppd_amount)
#amount value
        categoryallocattions = ET.SubElement(allledgerentries,"CATEGORYALLOCATIONS.LIST")
        category = ET.SubElement(categoryallocattions, "CATEGORY")
        category.text = "Primary Cost Category"
        isdeemedpositive = ET.SubElement(categoryallocattions, "ISDEEMEDPOSITIVE")
        isdeemedpositive.text = "No"
        costcenterallocationslist = ET.SubElement(categoryallocattions, "COSTCENTREALLOCATIONS.LIST")
        name = ET.SubElement(costcenterallocationslist, 'NAME')
        name.text = "DHQ - Head Office"
        amount = ET.SubElement(costcenterallocationslist,"AMOUNT")
        amount.text = str(ebsppd_amount)
#amount value
  
        bankallocationslist = ET.SubElement(allledgerentries,"BANKALLOCATIONS.LIST")
        billallocationslist = ET.SubElement(allledgerentries,"BILLALLOCATIONS.LIST")
        intercollectionlist = ET.SubElement(allledgerentries,"INTERESTCOLLECTION.LIST")
        oldauditentrieslist = ET.SubElement(allledgerentries,"OLDAUDITENTRIES.LIST")
        accountaudientrieslist = ET.SubElement(allledgerentries,"ACCOUNTAUDITENTRIES.LIST")
        auditentrieslist = ET.SubElement(allledgerentries,"AUDITENTRIES.LIST")
        taxbillallocationslist = ET.SubElement(allledgerentries,"TAXBILLALLOCATIONS.LIST")
        taxobjectallocationslist = ET.SubElement(allledgerentries,"TAXOBJECTALLOCATIONS.LIST")
        tdsexpenseallocationslist = ET.SubElement(allledgerentries,"TDSEXPENSEALLOCATIONS.LIST")
        vatstatdetails = ET.SubElement(allledgerentries,"VATSTATUTORYDETAILS.LIST")
        costtrackallocationslist = ET.SubElement(allledgerentries,"COSTTRACKALLOCATIONS.LIST")

#6th ALLLEDGERENTRIES.LIST
        ebscod_obj = ProductBilling.objects.filter(billing=bill_obj, product__product_name='ebscod')
        ebscod_amount = 0
        ebscod_total = 0
        if ebscod_obj:
            ebscod = ebscod_obj[0]
            ebscod_amount = ebscod.total_charge_pretax
            ebscod_total = ebscod_amount
        ebscod_amount = Decimal(ebscod_amount).quantize(TW)
        ebscod_total = ebscod_amount
        allledgerentries = ET.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
        oldauditentryidslist = ET.SubElement(allledgerentries, "OLDAUDITENTRYIDS.LIST")
        oldauditentryidslist.set('TYPE',"Number")
        oldauditentryids = ET.SubElement(oldauditentryidslist, "OLDAUDITENTRYIDS")
        oldauditentryids.text = "-1"
        ledgername= ET.SubElement(allledgerentries,"LEDGERNAME")
        ledgername.text = "Sales - EBS Cash on Delivery (EBS COD)"
        gstclass = ET.SubElement(allledgerentries,"GSTCLASS")
        isdeemedpositive = ET.SubElement(allledgerentries,"ISDEEMEDPOSITIVE")
        isdeemedpositive.text ="No"
        ledgerfromitem = ET.SubElement(allledgerentries,"LEDGERFROMITEM")
        ledgerfromitem.text ="No"
        removezeroentries = ET.SubElement(allledgerentries,"REMOVEZEROENTRIES")
        removezeroentries.text ="No"
        ispartyledger = ET.SubElement(allledgerentries,"ISPARTYLEDGER")
        ispartyledger.text ="No"
        islastdeemedpositive = ET.SubElement(allledgerentries,"ISLASTDEEMEDPOSITIVE")
        islastdeemedpositive.text ="No"
        amount = ET.SubElement(allledgerentries,"AMOUNT")
        amount.text = str(ebscod_amount)
#amount value
        categoryallocattions = ET.SubElement(allledgerentries,"CATEGORYALLOCATIONS.LIST")
        category = ET.SubElement(categoryallocattions, "CATEGORY")
        category.text = "Primary Cost Category"
        isdeemedpositive = ET.SubElement(categoryallocattions, "ISDEEMEDPOSITIVE")
        isdeemedpositive.text = "No"
        costcenterallocationslist = ET.SubElement(categoryallocattions, "COSTCENTREALLOCATIONS.LIST")
        name = ET.SubElement(costcenterallocationslist, 'NAME')
        name.text = "DHQ - Head Office"
        amount = ET.SubElement(costcenterallocationslist,"AMOUNT")
        amount.text = str(ebscod_amount)
#amount value

        bankallocationslist = ET.SubElement(allledgerentries,"BANKALLOCATIONS.LIST")
        billallocationslist = ET.SubElement(allledgerentries,"BILLALLOCATIONS.LIST")
        intercollectionlist = ET.SubElement(allledgerentries,"INTERESTCOLLECTION.LIST")
        oldauditentrieslist = ET.SubElement(allledgerentries,"OLDAUDITENTRIES.LIST")
        accountaudientrieslist = ET.SubElement(allledgerentries,"ACCOUNTAUDITENTRIES.LIST")
        auditentrieslist = ET.SubElement(allledgerentries,"AUDITENTRIES.LIST")
        taxbillallocationslist = ET.SubElement(allledgerentries,"TAXBILLALLOCATIONS.LIST")
        taxobjectallocationslist = ET.SubElement(allledgerentries,"TAXOBJECTALLOCATIONS.LIST")
        tdsexpenseallocationslist = ET.SubElement(allledgerentries,"TDSEXPENSEALLOCATIONS.LIST")
        vatstatdetails = ET.SubElement(allledgerentries,"VATSTATUTORYDETAILS.LIST")
        costtrackallocationslist = ET.SubElement(allledgerentries,"COSTTRACKALLOCATIONS.LIST")
#7th ALLLEDGERENTRIES.LIST
        rev_obj = ProductBilling.objects.filter(billing=bill_obj, product__product_name='rev')
        rev_amount = 0
        new_rev_amount = 0
        if rev_obj:
            rev = rev_obj[0]
            rev_amount = rev.total_charge_pretax
            new_rev_amount = rev.reverse_charge
        rev_amount = Decimal(rev_amount).quantize(TW)
        total_diff = total - (tax+ppd_total+cod_total+ebsppd_total+ebsppd_total+rev_amount)
        rev_amount = rev_amount + total_diff
        allledgerentries = ET.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
        oldauditentryidslist = ET.SubElement(allledgerentries, "OLDAUDITENTRYIDS.LIST")
        oldauditentryidslist.set('TYPE',"Number")
        oldauditentryids = ET.SubElement(oldauditentryidslist, "OLDAUDITENTRYIDS")
        oldauditentryids.text = "-1"
        ledgername= ET.SubElement(allledgerentries,"LEDGERNAME")
        ledgername.text = "Sales - Reverse Pickup ( RVP)"
        gstclass = ET.SubElement(allledgerentries,"GSTCLASS")
        isdeemedpositive = ET.SubElement(allledgerentries,"ISDEEMEDPOSITIVE")
        isdeemedpositive.text ="No"
        ledgerfromitem = ET.SubElement(allledgerentries,"LEDGERFROMITEM")
        ledgerfromitem.text ="No"
        removezeroentries = ET.SubElement(allledgerentries,"REMOVEZEROENTRIES")
        removezeroentries.text ="No"
        ispartyledger = ET.SubElement(allledgerentries,"ISPARTYLEDGER")
        ispartyledger.text ="No"
        islastdeemedpositive = ET.SubElement(allledgerentries,"ISLASTDEEMEDPOSITIVE")
        islastdeemedpositive.text ="No"
        amount = ET.SubElement(allledgerentries,"AMOUNT")
        amount.text = str(new_rev_amount)
#amount value
        categoryallocattions = ET.SubElement(allledgerentries,"CATEGORYALLOCATIONS.LIST")
        category = ET.SubElement(categoryallocattions, "CATEGORY")
        category.text = "Primary Cost Category"
        isdeemedpositive = ET.SubElement(categoryallocattions, "ISDEEMEDPOSITIVE")
        isdeemedpositive.text = "No"
        costcenterallocationslist = ET.SubElement(categoryallocattions, "COSTCENTREALLOCATIONS.LIST")
        name = ET.SubElement(costcenterallocationslist, 'NAME')
        name.text = "DHQ - Head Office"
        amount = ET.SubElement(costcenterallocationslist,"AMOUNT")
        amount.text = str(rev_amount)
#amount value

        bankallocationslist = ET.SubElement(allledgerentries,"BANKALLOCATIONS.LIST")
        billallocationslist = ET.SubElement(allledgerentries,"BILLALLOCATIONS.LIST")
        intercollectionlist = ET.SubElement(allledgerentries,"INTERESTCOLLECTION.LIST")
        oldauditentrieslist = ET.SubElement(allledgerentries,"OLDAUDITENTRIES.LIST")
        accountaudientrieslist = ET.SubElement(allledgerentries,"ACCOUNTAUDITENTRIES.LIST")
        auditentrieslist = ET.SubElement(allledgerentries,"AUDITENTRIES.LIST")
        taxbillallocationslist = ET.SubElement(allledgerentries,"TAXBILLALLOCATIONS.LIST")
        taxobjectallocationslist = ET.SubElement(allledgerentries,"TAXOBJECTALLOCATIONS.LIST")
        tdsexpenseallocationslist = ET.SubElement(allledgerentries,"TDSEXPENSEALLOCATIONS.LIST")
        vatstatdetails = ET.SubElement(allledgerentries,"VATSTATUTORYDETAILS.LIST")
        costtrackallocationslist = ET.SubElement(allledgerentries,"COSTTRACKALLOCATIONS.LIST")
 
        tallymessage2 = ET.SubElement(requestdata, "TALLYMESSAGE")
        company = ET.SubElement(tallymessage2,"COMPANY")
        remotecompanyinfolist = ET.SubElement(company,"REMOTECMPINFO.LIST")
        remotecompanyinfolist.set('MERGE',"Yes")
        name =  ET.SubElement(remotecompanyinfolist,"NAME")
        name.text = "91f0e35f-6726-452f-bf2d-bc668305a729"
        remotecmpname = ET.SubElement(remotecompanyinfolist,"REMOTECMPNAME")
        remotecmpname.text = "Ecom Express Private Limited"
        remotecmpstate = ET.SubElement(remotecompanyinfolist,"REMOTECMPSTATE")
        remotecmpstate.text = "Delhi"

        tallymessage3 = ET.SubElement(requestdata, "TALLYMESSAGE")
        company = ET.SubElement(tallymessage3,"COMPANY")
        remotecompanyinfolist = ET.SubElement(company,"REMOTECMPINFO.LIST")
        remotecompanyinfolist.set('MERGE',"Yes")
        name =  ET.SubElement(remotecompanyinfolist,"NAME")
        name.text = "91f0e35f-6726-452f-bf2d-bc668305a729"
        remotecmpname = ET.SubElement(remotecompanyinfolist,"REMOTECMPNAME")
        remotecmpname.text = "Ecom Express Private Limited"
        remotecmpstate = ET.SubElement(remotecompanyinfolist,"REMOTECMPSTATE")
        remotecmpstate.text = "Delhi"
       
      #  tree = ET.ElementTree(root)
      #  tree.write(xml_file_path)
      #  return xml_file_web
