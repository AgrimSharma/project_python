import datetime
import xml.etree.cElementTree as ET
from decimal import Decimal

from django.db.models import Q, Sum
from django.conf import settings

from service_centre.models import Shipment, StatusUpdate, CODDeposits
from reports.report_api import ReportGenerator
from reports.cash_tally_customer_names import cash_tally_customer_name
from location.models import ServiceCenter
from delivery.models import CreditPaymentAwbDetails
from mongoadmin.models import get_ledger_name


#import logging
#logging.basicConfig(
    #format='%(message)s',
    #filename='/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/reports.log',
    #level=logging.DEBUG, datefmt='%I:%M:%S %p') #filemode='w', 

class CodCollectionPodReport(object):

    def __init__(self, date_from_str, date_to_str, customer=None, sc=None, *args, **kwargs):
        self.customer = int(customer) if customer else None
        self.sc = int(sc) if sc else None

        date_from1 = datetime.datetime.strptime(date_from_str, "%Y-%m-%d")
        date_to1 = datetime.datetime.strptime(date_to_str, "%Y-%m-%d")

        self.date_from = date_from1.strftime("%Y-%m-%d 00:00:00")
        self.date_to = date_to1.strftime("%Y-%m-%d 23:59:59")
        self.xml_date_to = date_to1.strftime("%Y%m%d")
        self.str_date_to = date_to1.strftime("%d%B%Y")

        self.report = ReportGenerator('cod_pod_report_{0}.xlsx'.format(date_to_str))
        col_heads = ('Serial Number',
                'AWB Number',
                'Pickup Date',
                'Origin',
                'Shipper',
                'Consignee',
                'COD Due',
                'COD Collected',
                'Cr. Card Payment Received',
                'COD Balance',
                'Delivery Employee Code',
                'Delivery Employee Name',
                'Dest Centre',
                'Reason',
                'Updated on',
                'Delivery Date',
                'Amount Deposited')
        self.report.write_header(col_heads)
        self.xml_file = 'cod_collection_pod_{0}.xml'.format(date_to_str)
        self.xml_file_path = settings.FILE_UPLOAD_TEMP_DIR + '/reports/' + self.xml_file

    def get_query(self):
        q = Q()
        if self.customer:
            q = q & Q(shipper_id=self.customer)
        if self.date_from and self.date_to:
            q = q & Q(statusupdate__added_on__range=(self.date_from, self.date_to), statusupdate__status=2, reason_code=1)
        else:
            q = q & Q(statusupdate__added_on__range=self.report.current_month_range(), statusupdate__status=2, reason_code=1)

        if self.sc:
            q = q & Q(service_centre_id=self.sc)

        q = q & Q(product_type="cod")
     #   q = q & Q(airwaybill_number__startswith=4)
        return q

    def get_data(self):
        #logging.info('inside get data')
        q = self.get_query()
        #logging.info('query is : {0}'.format(q))
        all_data = Shipment.objects.using('local_ecomm').filter(q).exclude(rts_status=1).values_list(
                'id', 'airwaybill_number', 'added_on',
                'pickup__service_centre__center_name', 'shipper__code',
                'consignee', 'collectable_value', 'codcharge__status',
                'rto_status', 'rts_status', 'service_centre__center_name').distinct()
        
        ind = 0
        #logging.info('starting to write data')
        output = []
        for data in all_data:
            ind += 1
            #amount_collected = "return" if data[8] or data[9] else data[6]
            #logging.info(ind)
            amt = "Yes" if data[7] else "No"

            stu = StatusUpdate.objects.using('local_ecomm').filter(shipment__id=data[0], status=2).latest('added_on')
            if stu:
                reason_code = stu.reason_code
                added_on = stu.added_on
                dt = str(stu.date) + " "+ str(stu.time)
                emp_code = stu.delivery_emp_code.employee_code
                emp_firstname = stu.delivery_emp_code.firstname
            else:
                reason_code = ""
                added_on = ""
                dt = ""
                emp_code = ""
                emp_firstname = ""
            credit_payment = CreditPaymentAwbDetails.objects.filter(
                shipment__airwaybill_number=data[1]
            ).aggregate(total=Sum('credit_card_payment_received'))['total']
            credit_payment = credit_payment if credit_payment else ' '
            output.append(
                 (ind, data[1], data[2], data[3], data[4],
                 data[5], data[6], data[6], credit_payment, data[6],
                 emp_code, emp_firstname, data[10], reason_code, 
                 added_on, dt, amt))
        return output

    def daily_cash_tally_report(self, from_date, to_date, sc=0):
        #logging.info('inside daily cash tally report')
        start_date = datetime.datetime.strptime(from_date, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(to_date, '%Y-%m-%d').date()
        if int(sc):
            sc_list = ServiceCenter.objects.filter(id=sc)
        else:
            sc_list = ServiceCenter.objects.all()
        #logging.info(' start date : {0}  end date : {1}'.format(start_date, end_date))
        delta = end_date - start_date
        days = [start_date + datetime.timedelta(days=d) for d in range(delta.days + 1)]

        col_heads = [
            'COD Delivered date', 'DC Name', 'COD Delivered Due Amount',
            'Cash Deposited', 'Cash Deposited Date', 'CODID No',
            'Manual Slip No', 'Short/Excess', 'Cash Closed Status']
        now = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        report = ReportGenerator('scwise_daily_cash_tally_report_{0}.xlsx'.format(now))
        report.write_row(col_heads)

        for day in days:
            for sc in sc_list:
                row_count = 0
                #logging.info('day : {0} sc : {1} '.format(day, sc))
                q = Q()
                q = q & Q(
                    statusupdate__date=day, statusupdate__status=2,
                    reason_code=1, product_type='cod', statusupdate__origin=sc)
                ships = Shipment.objects.filter(q).exclude(rts_status=1)
                #logging.info('ship count :'.format(ships.count()))
                if ships.count() == 0:
                    continue
                #modification
                #Query Optimization needed
                cods = []
                cnt = 0
                for s in ships:
                    for cod_obj in CODDeposits.objects.filter(cod_shipments=s, date__gte=start_date):
                        if cod_obj not in cods:
                            cods.append(cod_obj)
                            cnt += 1
                            #logging.info(cnt)
                    
                #cod_deposits = CODDeposits.objects.filter(cod_shipments__in=ships, date__gte=start_date)
                #cods = list(set(cod_deposits))
                cod_codes = ', '.join([str(cod.codd_code) for cod in cods])
                deposited_dates = ', '.join([str((cod.deposited_on).date()) for cod in cods])
                slip_numbers = ', '.join([str(cod.slip_number) for cod in cods])      
                ############
                total_amount = ships.aggregate(total=Sum('collectable_value'))['total']
                deposit_amount = ships.filter(shipext__cash_deposit_status=1)\
                    .aggregate(total=Sum('shipext__collected_amount'))['total']
                total_amount = total_amount if total_amount else 0
                deposit_amount = deposit_amount if deposit_amount else 0
                short = total_amount - deposit_amount
                cash_status = 'no' if abs(short) > 20  else 'yes'
                cod_del_date = day.strftime('%Y-%m-%d')
                row_data = [
                    cod_del_date, sc.center_name, total_amount, deposit_amount,
                    deposited_dates, cod_codes, slip_numbers, short,
                    cash_status]
                report.write_row(row_data)
                #logging.info('row count :{0}'.format(row_count))
        return report.file_name

    def generate_report(self):
        #logging.info('inside generate report')
        data_gen = self.get_data()
        #logging.info('got data.. writing to excel')
        self.report.write_body(data_gen)
        #logging.info('path is .. {0}'.format(path))
        file_name = self.report.manual_sheet_close()
        return file_name

    def get_xml_data(self):
        q = self.get_query()
        #distinct_ship_ids = Shipment.objects.using('local_ecomm').filter(q).exclude(rts_status=1).distinct().values_list('id', flat=True)
        #data = Shipment.objects.using('local_ecomm').filter(id__in=distinct_ship_ids).values('shipper__id', 'shipper__name', 'shipper__code').\
                #annotate(collect_sum=Sum('collectable_value'))
        data = Shipment.objects.using('local_ecomm').filter(q).exclude(
            rts_status=1).distinct().values(
            'shipper__id', 'shipper__name', 'shipper__code'
            ).annotate(collect_sum=Sum('collectable_value'))
        return data

    def create_xml_report(self):
        xml_data = self.get_xml_data()
        customer_cs = sum([float(d.get('collect_sum')) for d in xml_data if d.get('collect_sum')])
        TW = Decimal(10) ** -2
        customer_collect_sum = Decimal(customer_cs).quantize(TW)
        root = ET.Element("ENVELOPE")

        header = ET.SubElement(root, "HEADER")
        tallyrequest = ET.SubElement(header, "TALLYREQUEST")
        tallyrequest.text = "Import Data"

        body = ET.SubElement(root, "BODY")

        importdata = ET.SubElement(body, "IMPORTDATA")
        # body IMPORTDATA-REQUESTDESC section
        requestdesc = ET.SubElement(importdata, "REQUESTDESC")
        requestdata = ET.SubElement(importdata, "REQUESTDATA")

        reportname = ET.SubElement(requestdesc, "REPORTNAME")
        reportname.text = "Vouchers"
        staticvariables = ET.SubElement(requestdesc, "STATICVARIABLES")
        svcurrentcompany = ET.SubElement(staticvariables, "SVCURRENTCOMPANY")
        svcurrentcompany.text = "Ecom Express Private Limited"

        # starts BODY-REQUESTDATA section
        tallymessage1 = ET.SubElement(requestdata, "TALLYMESSAGE")
        tallymessage1.set('xmlns:UDF', 'TallyUDF')
        tallymessage2 = ET.SubElement(requestdata, "TALLYMESSAGE")
        tallymessage2.set('xmlns:UDF', 'TallyUDF')
        tallymessage3 = ET.SubElement(requestdata, "TALLYMESSAGE")
        tallymessage3.set('xmlns:UDF', 'TallyUDF')

        # starts BODY-REQUESTDATA-TALLYMESSAGE1-VOUCHER section
        voucher = ET.SubElement(tallymessage1, "VOUCHER")
        voucher.set('REMOTEID', '')
        voucher.set('VCHKEY',"91f0e35f-6726-452f-bf2d-bc668305a729-0000a291:000003a4")
        voucher.set('VCHTYPE',"Journal")
        voucher.set('ACTION',"Create")
        voucher.set('OBJVIEW',"Accounting Voucher View")

        # Voucher sub tree
        oldauditentryids = ET.SubElement(voucher, "OLDAUDITENTRYIDS.LIST")
        oldauditentryids.set('TYPE', "Number")
        oldauditentry = ET.SubElement(oldauditentryids, "OLDAUDITENTRYIDS")
        oldauditentry.text = "-1"

        date = ET.SubElement(voucher, "DATE")
        date.text = self.xml_date_to

        guid = ET.SubElement(voucher, "GUID")
        guid.text = "91f0e35f-6726-452f-bf2d-bc668305a729-00005204"

        narration = ET.SubElement(voucher, "NARRATION")
        narration.text = "Being COD Amount Dues for AWB Delivered for Dated:- {0}".format(self.str_date_to)

        vouchertypename = ET.SubElement(voucher, "VOUCHERTYPENAME")
        vouchertypename.text = "Journal"

        vouchernumber = ET.SubElement(voucher, "VOUCHERNUMBER")
        vouchernumber.text = "8950"

        cstformissuetype = ET.SubElement(voucher, "CSTFORMISSUETYPE")
        cstformrecvtype = ET.SubElement(voucher, "CSTFORMRECVTYPE")

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
        effectivedate.text = self.xml_date_to
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
        alterid.text = "43456"
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
        masterid .text =  "20996"
        voucherkey = ET.SubElement(voucher, "VOUCHERKEY")
        voucherkey.text =  "178743653958564"

        oldauditentries = ET.SubElement(voucher, "OLDAUDITENTRIES.LIST")
        oldauditentries.text = ' '
        accountauditentries = ET.SubElement(voucher, "ACCOUNTAUDITENTRIES.LIST")
        accountauditentries.text = ' '
        auditentries = ET.SubElement(voucher, "AUDITENTRIES.LIST")
        auditentries.text = ' '
        invoicedelnotes = ET.SubElement(voucher, "INVOICEDELNOTES.LIST")
        invoicedelnotes.text = ' '
        invoiceorderlist = ET.SubElement(voucher, "INVOICEORDERLIST.LIST")
        invoiceorderlist.text = ' '
        invoiceindentlist = ET.SubElement(voucher, "INVOICEINDENTLIST.LIST")
        invoiceindentlist.text = ' '
        attendanceentries = ET.SubElement(voucher, "ATTENDANCEENTRIES.LIST")
        attendanceentries.text = ' '
        originvoicedetails = ET.SubElement(voucher, "ORIGINVOICEDETAILS.LIST")
        originvoicedetails.text = ' '
        invoiceexportlist = ET.SubElement(voucher, "INVOICEEXPORTLIST.LIST")
        invoiceexportlist.text = ' '

        allledgerentriesp = ET.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
        ledgernamep  = ET.SubElement(allledgerentriesp, "LEDGERNAME")

        ledgernamep.text = "Collection From Customers"
        oldauditentryidslist =  ET.SubElement(allledgerentriesp, "OLDAUDITENTRYIDS.LIST")
        oldauditentryidslist.set('TYPE', "Number")
        oldauditentryids = ET.SubElement(oldauditentryidslist, "OLDAUDITENTRYIDS")
        oldauditentryids.text = "-1"

        gstclass = ET.SubElement(allledgerentriesp, "GSTCLASS")
        gstclass.text = " "

        isdeemedpositive = ET.SubElement(allledgerentriesp, "ISDEEMEDPOSITIVE")
        isdeemedpositive.text = "Yes"

        ledgerfromitem = ET.SubElement(allledgerentriesp, "LEDGERFROMITEM")
        ledgerfromitem.text = "No"

        removezeroentries = ET.SubElement(allledgerentriesp, "REMOVEZEROENTRIES")
        removezeroentries.text = "No"

        ispartyledger = ET.SubElement(allledgerentriesp, "ISPARTYLEDGER")
        ispartyledger.text = "No"

        islastdeemedpositive = ET.SubElement(allledgerentriesp, "ISLASTDEEMEDPOSITIVE")
        islastdeemedpositive.text = "Yes"

        amount = ET.SubElement(allledgerentriesp, "AMOUNT")
        amount.text = '-' + str(round(customer_collect_sum))

        bankallocationslist  = ET.SubElement(allledgerentriesp, "BANKALLOCATIONS.LIST ")
        bankallocationslist.text = " "

        billallocationslist  = ET.SubElement(allledgerentriesp, "BILLALLOCATIONS.LIST ")
        billallocationslist.text = " "

        interestcollectionlist  = ET.SubElement(allledgerentriesp, "INTERESTCOLLECTION.LIST ")
        interestcollectionlist.text = " "

        oldauditentrieslist = ET.SubElement(allledgerentriesp, "OLDAUDITENTRIES.LIST")
        oldauditentrieslist.text = " "

        accountauditentrieslist  = ET.SubElement(allledgerentriesp, "ACCOUNTAUDITENTRIES.LIST ")
        accountauditentrieslist.text = " "

        auditentrieslist  = ET.SubElement(allledgerentriesp, "AUDITENTRIES.LIST ")
        auditentrieslist.text = " "

        taxbillallocationslist  = ET.SubElement(allledgerentriesp, "TAXBILLALLOCATIONS.LIST ")
        taxbillallocationslist.text = " "

        taxobjectallocationslist  = ET.SubElement(allledgerentriesp, "TAXOBJECTALLOCATIONS.LIST ")
        taxobjectallocationslist.text = " "

        tdsexpenseallocationslist  = ET.SubElement(allledgerentriesp, "TDSEXPENSEALLOCATIONS.LIST ")
        tdsexpenseallocationslist.text = " "

        vatstatutorydetailslist  = ET.SubElement(allledgerentriesp, "VATSTATUTORYDETAILS.LIST ")
        vatstatutorydetailslist.text = " "

        costtrackallocationslist  = ET.SubElement(allledgerentriesp, "COSTTRACKALLOCATIONS.LIST ")
        costtrackallocationslist.text = " "

        allledgerentrieslist  = ET.SubElement(allledgerentriesp, "ALLLEDGERENTRIES.LIST ")
        allledgerentrieslist.text = " "

        oldauditentryidslist = ET.SubElement(allledgerentriesp, "OLDAUDITENTRYIDS.LIST")
        oldauditentryidslist.set("TYPE", "Number")
        oldauditentryids = ET.SubElement(oldauditentryidslist, "OLDAUDITENTRYIDS")
        oldauditentryids.text = "-1"

        # Customer wise details section
        for data in xml_data:
            allledgerentries = ET.SubElement(voucher, "ALLLEDGERENTRIES.LIST")

            oldauditentryidslist = ET.SubElement(allledgerentries, "OLDAUDITENTRYIDS.LIST")
            oldauditentryidslist.set('TYPE', "Number")
            oldauditentryids = ET.SubElement(oldauditentryidslist, "OLDAUDITENTRYIDS")
            oldauditentryids.text = "-1"

            ledgername  = ET.SubElement(allledgerentries, "LEDGERNAME")

            # replace this line: instead read the value from mongodb database
            #customer_name = cash_tally_customer_name.get(int(data.get('shipper__code')), data.get('shipper__name'))
            customer_name = get_ledger_name(data.get('shipper__code'))
            if not customer_name:
                customer_name = data.get('shipper__name')
            ledgername.text = customer_name

            gstclass = ET.SubElement(allledgerentries, "GSTCLASS")
            isdeemedpositive = ET.SubElement(allledgerentries, "ISDEEMEDPOSITIVE")
            isdeemedpositive.text = "No"
            ledgerfromitem = ET.SubElement(allledgerentries, "LEDGERFROMITEM")
            ledgerfromitem.text = "No"
            removezeroentries = ET.SubElement(allledgerentries, "REMOVEZEROENTRIES")
            removezeroentries.text = "No"
            ispartyledger = ET.SubElement(allledgerentries, "ISPARTYLEDGER")
            ispartyledger.text = "No"
            islastdeemedpositive = ET.SubElement(allledgerentries, "ISLASTDEEMEDPOSITIVE")
            islastdeemedpositive.text = "No"
            amount = ET.SubElement(allledgerentries, "AMOUNT")
            amount.text = str(round(data['collect_sum']))

            bankallocations = ET.SubElement(allledgerentries, "BANKALLOCATIONS.LIST")
            bankallocations.text = ' '
            billallocations = ET.SubElement(allledgerentries, "BILLALLOCATIONS.LIST")
            billallocations.text = ' '
            interestcollection = ET.SubElement(allledgerentries, "INTERESTCOLLECTION.LIST")
            interestcollection.text = ' '
            oldauditentries = ET.SubElement(allledgerentries, "OLDAUDITENTRIES.LIST")
            oldauditentries.text = ' '
            accountauditentries = ET.SubElement(allledgerentries, "ACCOUNTAUDITENTRIES.LIST")
            accountauditentries.text = ' '
            auditentries = ET.SubElement(allledgerentries, "AUDITENTRIES.LIST")
            auditentries.text = ' '
            taxbillallocations = ET.SubElement(allledgerentries, "TAXBILLALLOCATIONS.LIST")
            taxbillallocations.text = ' '
            taxobjectallocations = ET.SubElement(allledgerentries, "TAXOBJECTALLOCATIONS.LIST")
            taxobjectallocations.text = ' '
            tdsexpenseallocations = ET.SubElement(allledgerentries, "TDSEXPENSEALLOCATIONS.LIST")
            tdsexpenseallocations.text = ' '
            vatstatutorydetails = ET.SubElement(allledgerentries, "VATSTATUTORYDETAILS.LIST")
            vatstatutorydetails.text = ' '
            costtrackallocations = ET.SubElement(allledgerentries, "COSTTRACKALLOCATIONS.LIST")
            costtrackallocations.text = ' '
            attrecords = ET.SubElement(allledgerentries, "ATTRECORDS.LIST")
            attrecords.text = ' '

        # Tally message 2 part
        company = ET.SubElement(tallymessage2, "COMPANY")
        remotecmpinfolist = ET.SubElement(company, "REMOTECMPINFO.LIST")
        remotecmpinfolist.set('MERGE', 'Yes')
        name = ET.SubElement(remotecmpinfolist, "NAME")
        name.text = "91f0e35f-6726-452f-bf2d-bc668305a729"
        remotecmpname = ET.SubElement(remotecmpinfolist, "REMOTECMPNAME")
        remotecmpname.text = 'EcomExpress Private Limited'
        remotecmpstate = ET.SubElement(remotecmpinfolist, "REMOTECMPSTATE")
        remotecmpstate.text = 'Delhi'

        # Tally message 3 part
        company = ET.SubElement(tallymessage3, "COMPANY")
        remotecmpinfolist = ET.SubElement(company, "REMOTECMPINFO.LIST")
        remotecmpinfolist.set('MERGE', 'Yes')
        name = ET.SubElement(remotecmpinfolist, "NAME")
        name.text = "91f0e35f-6726-452f-bf2d-bc668305a729"
        remotecmpname = ET.SubElement(remotecmpinfolist, "REMOTECMPNAME")
        remotecmpname.text = 'Ecom Expres Private Limited'
        remotecmpstate = ET.SubElement(remotecmpinfolist, "REMOTECMPSTATE")
        remotecmpstate.text = 'Delhi'
        tree = ET.ElementTree(root)
        tree.write(self.xml_file_path)
        return self.xml_file

