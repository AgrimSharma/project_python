import xml.etree.cElementTree as ET
from service_centre.models import Shipment, StatusUpdate
from reports.report_api import ReportGenerator
from reports.cash_tally_customer_names import cash_tally_customer_name

class InvoiceXmlReport(object):

    def __init__(self, year, month, *args, **kwargs):
        self.year = year
        self.month = month
        self.xml_file = 'invoice_xml.xml'
        self.xml_file_path = settings.FILE_UPLOAD_TEMP_DIR + '/reports/' + self.xml_file

    def create_invoice_xml_for_customers():
        customers = Customer.objects.filter(activation_status=True)
        for  customer in customers:
            path = self.create_invoice_xml(customer)
            print path
            # mail the report path

    def create_invoice_xml(customer):
        bill_obj =  Billing.objects.filter(customer__id = 4,billing_date__year = 2014,billing_date__month = 2)        

        root = ET.Element("ENVELOPE")
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
        voucher = ET.SubElement(tallymessage1, "VOUCHER")

        voucher.set('REMOTEID', '91f0e35f-6726-452f-bf2d-bc668305a729-00009204')
        voucher.set('VCHKEY',"91f0e35f-6726-452f-bf2d-bc668305a729-0000a31f:000002a8")
        voucher.set('VCHTYPE',"Journal")
        voucher.set('ACTION',"Create")
        voucher.set('OBJVIEW',"Accounting Voucher View")

        oldauditentryids = ET.SubElement(voucher, "OLDAUDITENTRYIDS.LIST")
        oldauditentryids.set('TYPE', "Number")
        oldauditentry = ET.SubElement(oldauditentryids, "OLDAUDITENTRYIDS")
        oldauditentry.text = "-1"

        date = ET.SubElement(voucher, "DATE")
        date.text = bill_obj.billing_date
        guid = ET.SubElement(voucher, "GUID")
        guid.text = "91f0e35f-6726-452f-bf2d-bc668305a729-00005204"

        narration = ET.SubElement(voucher, "NARRATION")
        narration.text = bill_obj.customer.name
        vouchertypename = ET.SubElement(voucher, "VOUCHERTYPENAME")
        vouchertypename.text = "Journal"
        vouchernumber = ET.SubElement(voucher, "VOUCHERNUMBER")
        vouchernumber.text = "1124"
        partyledgername = ET.SubElement(voucher, "PARTYLEDGERNAME")
        partyledgername.text = bill_obj.customer.name
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
        effectivedate.text = bill_obj.billing_date_from
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
        ledgername.text = bill_obj.customer.name
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
   #amount value
        categoryallocations = ET.SubElement(allledgerentries,'CATEGORYALLOCATIONS.LIST')
        category = ET.SubElement(categoryallocations, 'CATEGORY')
        isdeemedpositive = ET.SubElement(categoryallocations, 'ISDEEMEDPOSITIVE')
        isdeemedpositive.text = "Yes"
        costcentreallocationlist = ET.SubElement(categoryallocations, 'COSTCENTREALLOCATIONS.LIST')
        name = ET.SubElement(costcentreallocationlist, 'NAME')
        name.text = "DHQ - Head Office"
        amount = ET.SubElement(costcentreallocationlist,'AMOUNT')    
   #amount value
        
        banklocationslist = ET.SubElement(allledgerentries,'BANKALLOCATIONS.LIST')
        billallocationslist = ET.SubElement(allledgerentries,'BILLALLOCATIONS.LIST')
        
        name = ET.SubElement(billallocationslist,'NAME')
        name.text = "875"
        billtype = ET.SubElement(billallocationslist,'BILLTYPE')
        billtype = "New Ref"
        tdseducteeisspecialrate = ET.SubElement(billallocationslist,'TDSDEDUCTEEISSPECIALRATE')
        tdseducteeisspecialrate.text = "NO"
        amount = ET.SubElement(billallocationslist,,'AMOUNT')
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
        ledgername=.text = "Service Tax on Billing"
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
        allledgerentries = ET.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
        oldauditentryidslist = ET.SubElement(allledgerentries, "OLDAUDITENTRYIDS.LIST")
        oldauditentryidslist.set('TYPE',"Number")
        oldauditentryids = ET.SubElement(oldauditentryidslist, "OLDAUDITENTRYIDS")
        oldauditentryids.text = "-1"
        ledgername= ET.SubElement(allledgerentries,"LEDGERNAME")
        ledgername=.text = "Sales - Prepaid (PPD)"
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
        allledgerentries = ET.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
        oldauditentryidslist = ET.SubElement(allledgerentries, "OLDAUDITENTRYIDS.LIST")
        oldauditentryidslist.set('TYPE',"Number")
        oldauditentryids = ET.SubElement(oldauditentryidslist, "OLDAUDITENTRYIDS")
        oldauditentryids.text = "-1"
        ledgername= ET.SubElement(allledgerentries,"LEDGERNAME")
        ledgername=.text = "Sales - Cash on Delivery (COD)"
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
        allledgerentries = ET.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
        oldauditentryidslist = ET.SubElement(allledgerentries, "OLDAUDITENTRYIDS.LIST")
        oldauditentryidslist.set('TYPE',"Number")
        oldauditentryids = ET.SubElement(oldauditentryidslist, "OLDAUDITENTRYIDS")
        oldauditentryids.text = "-1"
        ledgername= ET.SubElement(allledgerentries,"LEDGERNAME")
        ledgername=.text = "Sales - EBS Prepaid (EBS PPD)"
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
        allledgerentries = ET.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
        oldauditentryidslist = ET.SubElement(allledgerentries, "OLDAUDITENTRYIDS.LIST")
        oldauditentryidslist.set('TYPE',"Number")
        oldauditentryids = ET.SubElement(oldauditentryidslist, "OLDAUDITENTRYIDS")
        oldauditentryids.text = "-1"
        ledgername= ET.SubElement(allledgerentries,"LEDGERNAME")
        ledgername=.text = "Sales - EBS Cash on Delivery (EBS COD)"
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
        allledgerentries = ET.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
        oldauditentryidslist = ET.SubElement(allledgerentries, "OLDAUDITENTRYIDS.LIST")
        oldauditentryidslist.set('TYPE',"Number")
        oldauditentryids = ET.SubElement(oldauditentryidslist, "OLDAUDITENTRYIDS")
        oldauditentryids.text = "-1"
        ledgername= ET.SubElement(allledgerentries,"LEDGERNAME")
        ledgername=.text = "Sales - Reverse Pickup ( RVP)"
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
       
        tree = ET.ElementTree(root)
        tree.write(self.xml_file_path)
        return self.xml_file


       
       


    
      

      
