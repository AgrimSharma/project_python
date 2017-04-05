import datetime
import sys
import xlrd
import pdb

from django.db.models import Sum, Count
from django.conf import settings

from octroi.models import OctroiBilling, CustomerOctroiCharges
from customer.models import Customer
from service_centre.models import OctroiShipments, Shipment


class CustomBilling(object):

    def __init__(self, cid, data, octroi_value=5.5):
        self.customer_id = cid
        self.data = data
        try:
            customer_oct  = CustomerOctroiCharges.objects.get(customer__id=cid)
            self.octroi_value = round(customer_oct.octroi_rate/100, 4)
            self.ecomm_charge = round(customer_oct.octroi_charge/100, 4)
        except CustomerOctroiCharges.DoesNotExist:
            self.octroi_value = round(float(octroi_value)/100, 4)
            self.ecomm_charge = 0.05

    def read_excel_file(self):
        book = xlrd.open_workbook(file_contents=self.data)
        ws = book.sheet_by_index(0)
        awbs = ws.col_values(0)[1:]
        cv = ws.col_values(1)[1:]
        receipt = ws.col_values(2)[1:]
        sheet_data = zip(awbs, cv, receipt)
        return sheet_data

    def generate_bill(self):
        customer = Customer.objects.get(id=self.customer_id)
        sheet_data = self.read_excel_file()
        awbs = [x[0] for x in sheet_data]
        values_list = [x[1] for x in sheet_data]

        oct_ships = OctroiShipments.objects.filter(shipment__airwaybill_number__in=awbs, octroi_billing=None)
        cust_id = oct_ships.values_list('shipper__id', flat=True).distinct()
        error_dict = {}
        error_list = []
        error_awbs = []

        if len(cust_id) == 0:
            error_list.append('No valid Airwayblls found for billing.')

        if len(cust_id) > 1:
            error_list.append('Airwaybill from multiple customers')

        if cust_id and int(cust_id[0]) != int(self.customer_id):
            error_list.append('Airwaybills found from different customers')

        if len(awbs) != oct_ships.only('id').count():
            error_list.append('Incorrect airwaybill numbers found')
            b = oct_ships.values_list('shipment__airwaybill_number', flat=True)
            corrupt_awbs = list(set(awbs) - set(b))
            error_awbs = [int(x) for x in corrupt_awbs]

        if error_list or error_awbs:
            error_dict['error_list'] = error_list
            error_dict['error_awbs'] = error_awbs
            return (False, error_dict)

        # update octroi shipments values
        for a, c, r in sheet_data:
            ship = Shipment.objects.get(airwaybill_number=a)
            oct_charge = c * self.octroi_value
            ecomm_charge = oct_charge * self.ecomm_charge
            OctroiShipments.objects.filter(shipment=ship).update(octroi_charge=oct_charge,
                    octroi_ecom_charge=ecomm_charge, status=1, receipt_number=str(int(float(r))))

        total_collectable_value = sum(values_list)
        tcv = total_collectable_value if total_collectable_value else 0
        octroi_charge = tcv * self.octroi_value
        octroi_ecom_charge = octroi_charge * self.ecomm_charge

        total_charge_pretax = octroi_charge + octroi_ecom_charge
        service_tax = octroi_ecom_charge * 0.12
        education_secondary_tax =  service_tax * 0.02
        cess_higher_secondary_tax =  service_tax * 0.01
        total_payable_charge = total_charge_pretax + service_tax + education_secondary_tax + cess_higher_secondary_tax

        billingdate = datetime.datetime.now()
        oct_billing = OctroiBilling.objects.create(customer=customer,
                octroi_charge=octroi_charge,
                octroi_ecom_charge=octroi_ecom_charge,
                education_secondary_tax=education_secondary_tax,
                cess_higher_secondary_tax=cess_higher_secondary_tax,
                service_tax=service_tax,
                total_charge_pretax=total_charge_pretax,
                total_payable_charge=total_payable_charge,
                bill_generation_date=billingdate)

        octroi_ships = OctroiShipments.objects.filter(shipment__airwaybill_number__in=awbs, octroi_billing=None, status=1)
        cust_id = oct_ships.values_list('shipper__id', flat=True).distinct()
        oct_billing.shipments = octroi_ships
        oct_billing.bill_id = 'OC' + str(oct_billing.id)
        oct_billing.save()
        octroi_ships.update(octroi_billing=oct_billing)
        return (True, oct_billing)

def revert_ecomm_charge(bill_id):
    """ This function is used to updated the ecomm_charge of a billing object to zero.
        This function will update the related fields values also.
    """
    b=OctroiBilling.objects.get(id=bill_id)
    octroi_charge = b.octroi_charge
    ships = b.shipments.all()
    ships.update(octroi_ecom_charge=0)
    OctroiBilling.objects.filter(id=bill_id).update(
        octroi_ecom_charge=0,
        education_secondary_tax=0,
        cess_higher_secondary_tax=0,
        service_tax=0,
        total_charge_pretax=octroi_charge,
        total_payable_charge=octroi_charge)

    return True

def update_ecomm_charge(bill_id, ecomm_charge):
    """ This function is used to updated the ecomm_charge of a billing object to 5%.
        This function will update the related fields values also.
    """
    b=OctroiBilling.objects.get(id=bill_id)
    octroi_charge = b.octroi_charge
    ships = b.shipments.all()
    for s in ships:
        s.octroi_ecom_charge = s.octroi_charge * (ecomm_charge / 100)
        s.save()

    octroi_ecom_charge = octroi_charge * (ecomm_charge / 100)
    total_charge_pretax = octroi_charge + octroi_ecom_charge
    service_tax = octroi_ecom_charge * 0.12
    education_secondary_tax =  service_tax * 0.02
    cess_higher_secondary_tax =  service_tax * 0.01
    total_payable_charge = total_charge_pretax + service_tax + education_secondary_tax + cess_higher_secondary_tax

    OctroiBilling.objects.filter(id=bill_id).update(
        octroi_ecom_charge =octroi_ecom_charge,
        total_charge_pretax = total_charge_pretax,
        service_tax = service_tax,
        education_secondary_tax =education_secondary_tax ,
        cess_higher_secondary_tax =cess_higher_secondary_tax ,
        total_payable_charge =total_payable_charge )

    return True

def update_ecomm_octroi_charge(bill_id, oct_charge=0, ecomm_charge=0):
    b = OctroiBilling.objects.get(id=bill_id)
    shipments = b.shipments.all()
    for ship in shipments:
        coll_value = ship.shipment.collectable_value
        oct_val = coll_value * (oct_charge / 100)
        ecom_val = oct_val * (ecomm_charge / 100)
        ship.octroi_ecom_charge=ecom_val
        ship.octroi_charge = oct_val
        ship.save()

    ships = b.shipments.all()

    octroi_charge = ships.aggregate(tot=Sum('octroi_charge'))['tot']
    octroi_ecom_charge = ships.aggregate(tot=Sum('octroi_ecom_charge'))['tot']

    total_charge_pretax = octroi_charge + octroi_ecom_charge
    service_tax = octroi_ecom_charge * 0.12
    education_secondary_tax =  service_tax * 0.02
    cess_higher_secondary_tax =  service_tax * 0.01
    total_payable_charge = total_charge_pretax + service_tax + education_secondary_tax + cess_higher_secondary_tax

    OctroiBilling.objects.filter(id=bill_id).update(
            octroi_charge=octroi_charge,
            octroi_ecom_charge=octroi_ecom_charge,
            education_secondary_tax=education_secondary_tax,
            cess_higher_secondary_tax=cess_higher_secondary_tax,
            service_tax=service_tax,
            total_charge_pretax=total_charge_pretax,
            total_payable_charge=total_payable_charge)

    return True


