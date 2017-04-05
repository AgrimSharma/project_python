import sys
import xlrd
import datetime
from collections import defaultdict

from django.db.models import get_model, Q
from django.contrib.auth.models import User

from service_centre.models import (
    Shipment, CODDeposits,
    CODCharge, ShipmentStatusMaster, StatusUpdate, Order_price,
    ServiceCenter, ShipmentExtension, outscan_update_for_cash_tally,
    ReverseShipment, ServiceCenter, DOShipment)
from pickup.models import * #PickupRegistration, ReversePickupRegistration
from location.models import Pincode, Address
from authentication.models import EmployeeMaster
from utils import rts_pricing_rev, price_updated_rev, history_update
from billing.charge_calculations import rts_pricing, price_updated
from ecomm_admin.models import update_shipment_changelog
from customer.models import Shipper, ShipperMapping
from airwaybill.models import *
from billing.jasper_update_new import update_jasper_awb
from reports.ecomm_mail import ecomm_send_mail
from delivery.models import update_bag_history, remove_shipment_from_bag
from reports.models import ShipmentBagHistory


def update_customer(shipment, subshipper_id, user=None):
    subshipper = Shipper.objects.get(id=int(subshipper_id))
    shipper = subshipper.customer
    Shipment.objects.filter(pk=shipment.id).update(shipper=shipper)

    if subshipper_id == 2872:#to be updated to ecomm foc
        Shipment.objects.filter(pk=shipment.id).update(pickup=89887)
        return True

    address=Address.objects.get(id=subshipper.address_id)
    pincode=Pincode.objects.get(pincode=address.pincode)

    pr = PickupRegistration.objects.create(status=1,
                customer_code=shipper, subcustomer_code=subshipper,
                service_centre=pincode.service_center, mode_id=1,
                customer_name="Test", address_line1=address.address1,
                actual_weight=4.0, volume_weight=4.0, pickup_date = now,
                pieces=4)
    Shipment.objects.filter(pk=shipment.id).update(pickup=pr)#updating origin, and subshipper
    if shipment.status >= 2:
        pricing(shipment)
	return True

def update_shipment_history(shipment, *args, **kwargs):
    reason_code = kwargs.get('reason_code')
    employee_code = kwargs.get('employee_code')
    current_sc = kwargs.get('sc')
    remarks = kwargs.get('remarks')
    status = kwargs.get('status')
    updated_on = kwargs.get('updated_on')
    if not updated_on:
        updated_on = datetime.datetime.now() 

    if not shipment.added_on:
       shipment.added_on = datetime.datetime.now()

    upd_time = shipment.added_on
    monthdir = upd_time.strftime("%Y_%m")
    shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
    sh = shipment_history.objects.create(
        shipment=shipment,
        reason_code=reason_code,
        remarks=remarks,
        status=status,
        employee_code=employee_code,
        current_sc=current_sc,
        expected_dod=shipment.expected_dod)

    shipment_history.objects.filter(id=sh.id).update(updated_on=updated_on)

    ShipmentExtension.objects.filter(
        shipment=shipment
    ).update(
        status_bk=status, current_sc_bk=current_sc, remarks=remarks, 
        updated_on=datetime.datetime.now()
    )
    reason = reason_code.code if reason_code else ''
    ShipmentBagHistory.objects.update_ship_history(
        shipment.airwaybill_number, status, employee_code, reason, remarks)
    return True

def mark_shipment_undelivered(awb, user, sc=None):
    """mark_shipment_undelivered(awb) => True/False
    check whether a shipment is delivered, if true
    mark it as  undelivered and updted its related models.
    """
    try:
        shipment = Shipment.objects.get(airwaybill_number=awb)
    except Shipment.DoesNotExist:
        return False

    # proceed only if shipments status is delivered(9)
    if shipment.status == 9:
        now = datetime.datetime.now()
        # remove shipment from coddeposits
        coddeposit = CODDeposits.objects.filter(cod_shipments__in=[shipment])
        if coddeposit.exists():
            coddeposit[0].cod_shipments.remove(shipment)

        # update shipment's codcharge status to 0
        CODCharge.objects.filter(shipment=shipment).update(status=0)

        reason_code = ShipmentStatusMaster.objects.get(id=44)
        # get the latest delivery outscan object and update its values
        dos =  shipment.doshipment_set.filter(deliveryoutscan__status=1).order_by('-added_on')
        if dos:
            dos = dos[0]
            dos.status = 0
            dos.updated_on = now
            dos.save()
            dos.deliveryoutscan.collection_status = 0
            dos.deliveryoutscan.save()
            outscan_update_for_cash_tally(dos.deliveryoutscan.id)
        if not sc:
            sc = shipment.current_sc
        update_shipment_history(shipment, reason_code=reason_code, status=0, sc=sc,
                employee_code=user.employeemaster, remarks="Shipment Updated(POD reversal)")

        # update statusupdate
        StatusUpdate.objects.filter(shipment=shipment, status=2).update(reason_code=reason_code, date=now.date(), time=now.time(), status=1)

        # update shipment's status to undelivered (status 8)
        Shipment.objects.filter(airwaybill_number=awb).update(status=8,reason_code=reason_code,updated_on=now)
        update_shipment_changelog(shipment, 'status', user, 'Undelivered', 'Delivered')
        # delete delivery outscan object
        # dos.delete()
    else:
        return False

    return True

def change_pincode_service_center(pincode, sc):
    sc = ServiceCenter.objects.get(center_shortcode=sc)
    pin = Pincode.objects.get(pincode=pincode)
    Pincode.objects.filter(pincode=pincode).update(service_center=sc)
    print 'updated service cneter from {0} to {1}'.format(pin.service_center.center_shortcode,  sc)

def update_shipment_pricing(awb, revision=False):
    s = Shipment.objects.get(airwaybill_number=awb)
    if not s.shipext.product:
        update_product_type([awb])

    if s.shipper_id == 6:
        update_jasper_awb(awb)
        return True

    if revision:
        if s.rts_status == 1:
            rts_pricing_rev(s)
        else:
            price_updated_rev(s)
    else:
        if s.rts_status == 1:
            rts_pricing(s)
        else:
            price_updated(s)
    return True

def deactivate_employees(ecodes):
    EmployeeMaster.objects.filter(employee_code__in=ecodes).update(staff_status=2)
    users = EmployeeMaster.objects.filter(employee_code__in=ecodes).exclude(user=None).values_list('user__id', flat=True)
    for user in users:
        User.objects.filter(id=user).update(is_active=False)
    return EmployeeMaster.objects.filter(employee_code__in=ecodes).values_list('employee_code', 'staff_status')

def activate_employees(ecodes):
    EmployeeMaster.objects.filter(employee_code__in=ecodes).update(staff_status=0)
    users = EmployeeMaster.objects.filter(employee_code__in=ecodes).exclude(user=None).values_list('user__id', flat=True)
    for user in users:
        User.objects.filter(id=user).update(is_active=True)
    return EmployeeMaster.objects.filter(employee_code__in=ecodes).values_list('employee_code', 'staff_status')

def update_chargeable_weight(awbs, weights):
    awbs = [int(a) for a in awbs]
    weights = [float(w) for w in weights]
    awb_weight_list = zip(awbs, weights)
    unupdated_list = []
    for awb, weight in awb_weight_list:
        s = Shipment.objects.filter(airwaybill_number=awb)
        if s.exists():
            s.update(actual_weight=weight, volumetric_weight=weight)
            update_shipment_pricing(awb)
        else:
            unupdated_list.append(awb)

    return  unupdated_list

def remove_rts_status(awb, user):
    shipment = Shipment.objects.get(airwaybill_number=awb)
    if shipment.rts_status != 2:
        return False

    ref_awb = shipment.ref_airwaybill_number
    print awb, ref_awb
    Shipment.objects.filter(airwaybill_number=awb).update(
        rts_status=0, ref_airwaybill_number=None)
    ref_ship = Shipment.objects.get(airwaybill_number=ref_awb)
    print 'ref ship ', ref_ship
    update_shipment_changelog(shipment, 'rts_status', user, 0, 2)
    update_customer(ref_ship, 2872, user=user)
    return True

def remove_reverse_pickup(pickup_id):
    rev_pickup = ReversePickupRegistration.objects.get(id=pickup_id)
    rev_ships = ReverseShipment.objects.filter(reverse_pickup=rev_pickup)
    rev_ships.delete()
    rev_pickup.delete()
    return True

def airwaybill_update(awb, new_awc):
    awn =  AirwaybillNumbers.objects.get(airwaybill_number=awb)
    awc = AirwaybillCustomer.objects.get(id = awn.awbc_info.get().id)
    awc.airwaybill_number.remove(awn)
    nawc = AirwaybillCustomer.objects.get(id = new_awc)
    awc.airwaybill_number.add(awn)

def pincode_update(file):
    for a in line[1:]:
       val = a.split(',')
       sh = Shipper.objects.get(id = val[0])
       if ShipperMapping.objects.filter(shipper=sh):
         ShipperMapping.objects.filter(shipper=sh).update(forward_pincode=int(val[2]), return_pincode = int(val[1]))
       else:
            ShipperMapping.objects.create(shipper=sh, forward_pincode=int(val[2]), return_pincode = int(val[1]))
       if (counter % 500) == 0:
            print counter
       counter += 1

def multiple_pickup_creation(subcustomer_code=None, alias_code=None, 
                             num_ships=0, scheduler=0):
    """
    This function create a pickup scheduler for the given subcustomer.
    Bug: If the given sub customer has not given pincode in its address,
        this function will break.
    solution: make pincode mandatory in subcustomer address
    """ 
    if alias_code:
       subc = Shipper.objects.get(alias_code=alias_code)
    else:
       subc = Shipper.objects.get(id=subcustomer_code)
    address = Address.objects.get(id=subc.address.id)
    if ShipperMapping.objects.filter(shipper=subc):
        pincode = ShipperMapping.objects.get(shipper=subc)
        pincode_obj = Pincode.objects.get(pincode = pincode.forward_pincode)
    else:
        pincode_obj = Pincode.objects.get(pincode=subc.address.pincode)
        
    service_centre = pincode_obj.service_center

    pickup_sch = PickupScheduler.objects.create(subcustomer_code_id = subcustomer_code,
        pickup_time="14:20", schedule_uptil = "2016-06-01", 
        pieces=num_ships, service_centre=service_centre, caller_name = None)
    ps = PickupSchedulerRegistration.objects.create(pickup_scheduler = pickup_sch,
        subcustomer_code = pickup_sch.subcustomer_code, pieces = pickup_sch.pieces,
        pickup_date = datetime.datetime.now().date(), pickup_time = pickup_sch.pickup_time,
        service_centre = pickup_sch.service_centre)
    regular_pickup = 0
    if scheduler:
       for a in [1,2,3,4,5,6]:
              PickupScheduleWeekdays.objects.create(weekday=a, time="14:20", pickupscheduler = pickup_sch)
       regular_pickup = True

    pr = PickupRegistration.objects.create(customer_code=subc.customer, pickup_date = datetime.datetime.now().date(),
         customer_name=subc.name, address_line1 = address.address1, address_line2 = address.address2,
         address_line3 = address.address3, pincode=pincode_obj.pincode, regular_pickup = regular_pickup, pieces = num_ships,
         actual_weight = 4, volume_weight = 4, subcustomer_code = subc, service_centre=service_centre )
    ps.pickup = pr
    ps.save()
    return True

def mark_shipment_lost(awbs):
    """ update as lost(333) by default"""
    reason_code = ShipmentStatusMaster.objects.get(code=333)
    emp = EmployeeMaster.objects.get(employee_code=26388)
    shipments = Shipment.objects.filter(airwaybill_number__in=awbs)
    sc = ServiceCenter.objects.get(center_shortcode='BOM')

    for shipment in shipments:
        print shipment.airwaybill_number
        # if shipment is outscaned update doshipment, shipment for cash tally
        if shipment.status > 6:
            doss = shipment.doshipment_set.filter(deliveryoutscan__status=1)
            if doss:
                dos = doss.latest('id')
                DOShipment.objects.filter(id=dos.id).update(status=2, updated_on=datetime.datetime.now())
                outscan_update_for_cash_tally(dos.deliveryoutscan.id)
        # update shipment history
        update_shipment_history(shipment, reason_code=reason_code, status=8, sc=sc,
                employee_code=emp, remarks="Shipment Lost")

        Shipment.objects.filter(airwaybill_number=shipment.airwaybill_number).\
            update(status=8, reason_code=reason_code, updated_on=datetime.datetime.now())

    return True

def mark_shipment_delivered(awbs):
    '''Status Update for Shipment'''
    reason_code = ShipmentStatusMaster.objects.get(code=999)
    emp = EmployeeMaster.objects.get(employee_code=26388)
    error_dict = defaultdict(list)

    for awb in awbs:
        shipment = Shipment.objects.get(airwaybill_number=awb)
        print shipment.airwaybill_number
        if shipment.reason_code.code == 333:
            error_dict[shipment.airwaybill_number].append('Shipment is lost.')
            continue

        if shipment.rts_status == 2:
            error_dict[shipment.airwaybill_number].append('RTS Shipment') 
            continue

        #if shipment.status in [7,8,9]:
            #if not shipment.deliveryoutscan_set.latest("added_on").status:
                #error_dict[shipment.airwaybill_number].append('Need to close the outscan.')
                #continue

        #elif shipment.status < 7:
            #error_dict[shipment.airwaybill_number].append('Please outscan the shipment first.')
            #continue

        # 1. update status update table
        su = StatusUpdate.objects.get_or_create(
                shipment=shipment,
                data_entry_emp_code=emp,
                delivery_emp_code=emp,
                reason_code=reason_code,
                date=datetime.datetime.today(), time=datetime.datetime.now().time(),
                recieved_by=shipment.consignee,
                status=2,
                origin=shipment.original_dest,
                remarks='Delivered') #status update

        # 2. update doshipment and deliveryoutscan table
        doss = DOShipment.objects.filter(shipment=shipment, deliveryoutscan__status=1)
        if doss:
            dos = doss.latest('added_on')
            DOShipment.objects.filter(id=dos.id).update(status=1, updated_on=datetime.datetime.now())
            outscan_update_for_cash_tally(dos.deliveryoutscan.id)

        # 3. update shipment and shipmentextension table
        ShipmentExtension.objects.filter(shipment=shipment).update(delivered_on=datetime.datetime.now())
        Shipment.objects.filter(airwaybill_number=shipment.airwaybill_number).\
            update(status=9, reason_code=reason_code, updated_on=datetime.datetime.now())

        # 4. update shipment history
        update_shipment_history(
            shipment, reason_code=reason_code, status=9, sc=shipment.current_sc,
            employee_code=emp, remarks="Shipment Delivered")

    return error_dict

def update_shipment_undelivered(awbs):
    '''Status Update for Shipment'''
    reason_code = ShipmentStatusMaster.objects.get(code=221)
    emp = EmployeeMaster.objects.get(employee_code=26388)
    error_dict = defaultdict(list)

    for awb in awbs:
        shipment = Shipment.objects.get(airwaybill_number=awb)
        print shipment.airwaybill_number
        if shipment.reason_code.code in [111, 999, 888, 333, 310, 200, 208, 302, 311]:
            error_dict[shipment.airwaybill_number].append('Shipment is lcosed.')
            continue

        if shipment.rts_status == 2:
            error_dict[shipment.airwaybill_number].append('RTS Shipment') 
            continue

        #if shipment.status in [7,8,9]:
            #if not shipment.deliveryoutscan_set.latest("added_on").status:
                #error_dict[shipment.airwaybill_number].append('Need to close the outscan.')
                #continue

        #elif shipment.status < 7:
            #error_dict[shipment.airwaybill_number].append('Please outscan the shipment first.')
            #continue

        # 1. update status update table
        su = StatusUpdate.objects.get_or_create(
                shipment=shipment,
                data_entry_emp_code=emp,
                delivery_emp_code=emp,
                reason_code=reason_code,
                date=datetime.datetime.today(), 
                time=datetime.datetime.now().time(),
                recieved_by=shipment.consignee,
                status=1,
                origin=shipment.current_sc,
                remarks='Refused') #status update

        # 2. update doshipment and deliveryoutscan table
        doss = DOShipment.objects.filter(shipment=shipment, deliveryoutscan__status=1)
        if doss:
            dos = doss.latest('added_on')
            DOShipment.objects.filter(id=dos.id).update(status=2, updated_on=datetime.datetime.now())
            outscan_update_for_cash_tally(dos.deliveryoutscan.id)

        # 3. update shipment and shipmentextension table
        #ShipmentExtension.objects.filter(shipment=shipment).update(delivered_on=datetime.datetime.now())
        Shipment.objects.filter(airwaybill_number=shipment.airwaybill_number).\
            update(status=8, reason_code=reason_code, updated_on=datetime.datetime.now())

        # 4. update shipment history
        update_shipment_history(
            shipment, reason_code=reason_code, status=8, sc=shipment.current_sc,
            employee_code=emp, remarks="Shipment un-delivered")

    return error_dict

def update_product_type(awbs):
    cod = Product.objects.get(product_name='cod')
    ppd = Product.objects.get(product_name='ppd')
    ebscod = Product.objects.get(product_name='ebscod')
    ebsppd = Product.objects.get(product_name='ebsppd')
    rev = Product.objects.get(product_name='rev')

    for awb in awbs:
        first_digit = str(awb)[0]
        print awb
        try:
            ship = Shipment.objects.get(airwaybill_number=awb, billing=None)
            if first_digit == '3':
                ShipmentExtension.objects.filter(shipment=ship).update(product=ebsppd)
            elif first_digit == '4':
                ShipmentExtension.objects.filter(shipment=ship).update(product=ebscod)
            elif first_digit == '5':
                ShipmentExtension.objects.filter(shipment=ship).update(product=rev)
            elif ship.product_type == 'cod':
                ShipmentExtension.objects.filter(shipment=ship).update(product=cod)
            elif ship.product_type == 'ppd':
                ShipmentExtension.objects.filter(shipment=ship).update(product=ppd)
        except Shipment.DoesNotExist:
            pass 

def update_product_type_backup(awbs):
    cod = Product.objects.get(product_name='cod')
    ppd = Product.objects.get(product_name='ppd')
    ebscod = Product.objects.get(product_name='ebscod')
    ebsppd = Product.objects.get(product_name='ebsppd')
    rev = Product.objects.get(product_name='rev')

    codships = Shipment.objects.filter(airwaybill_number__in=awbs, product_type='cod', billing=None)
    cod_count = ShipmentExtension.objects.filter(shipment__in=codships).update(product=cod)

    ppdships = Shipment.objects.filter(airwaybill_number__in=awbs, product_type='ppd', billing=None)
    ppd_count = ShipmentExtension.objects.filter(shipment__in=ppdships).update(product=ppd)

    ebsppdships = Shipment.objects.filter(airwaybill_number__in=awbs, airwaybill_number__startswith=3, billing=None)
    ebsppd_count = ShipmentExtension.objects.filter(shipment__in=ebsppdships).update(product=ebsppd)

    ebscodships = Shipment.objects.filter(airwaybill_number__in=awbs, airwaybill_number__startswith=4, billing=None)
    ebscod_count = ShipmentExtension.objects.filter(shipment__in=ebscodships).update(product=ebscod)

    revships = Shipment.objects.filter(airwaybill_number__in=awbs, airwaybill_number__startswith=5, billing=None)
    rev_count = ShipmentExtension.objects.filter(shipment__in=revships).update(product=rev)

def update_ebs_prices(awbs):
    Order_price.objects.filter(
        shipment__airwaybill_number__in=awbs
        #Q(shipment__airwaybill_number__in=awbs), 
        #Q(freight_charge__gt=1), 
        #Q(shipment__airwaybill_number__startswith=3) |
        #Q(shipment__airwaybill_number__startswith=4)
    ).update(
        freight_charge=1, 
        fuel_surcharge=0, 
        valuable_cargo_handling_charge=0, 
        to_pay_charge=0, 
        rto_charge=0, 
        sdd_charge=0, 
        sdl_charge=0, 
        reverse_charge=0, 
        tab_charge=0
    )
    CODCharge.objects.filter(
        shipment__airwaybill_number__in=awbs
        #Q(shipment__airwaybill_number__in=awbs), 
        #Q(cod_charge__gt=0),
        #Q(shipment__airwaybill_number__startswith=3) |
        #Q(shipment__airwaybill_number__startswith=4)
    ).update(cod_charge=0)

def resolve_rts_failure(awb):
    ship = Shipment.objects.get(airwaybill_number=awb)
    if ship.status == 9:
        print 'Shipment Already delivered'
        return False
    if not ship.ref_airwaybill_number:
        print 'No Ref Awb. Aborting operation'
        sys.exit(1)
    print awb, ship.ref_airwaybill_number
    try:
        Shipment.objects.get(airwaybill_number=ship.ref_airwaybill_number)
        print 'Ref Shipment exists. Aborting operation'
        sys.exit(1)
    except Shipment.DoesNotExist:
        AirwaybillNumbers.objects.filter(airwaybill_number=ship.ref_airwaybill_number).update(status=False)
        Shipment.objects.filter(airwaybill_number=awb).update(rts_status=0, ref_airwaybill_number=None)
        print awb, ' updated'

def update_weight(file_path):
    wb = xlrd.open_workbook(file_path)
    sh = wb.sheet_by_index(0)
    awbn = sh.col_values(0)[1:]
    weight= sh.col_values(1)[1:]
    awb_wt = zip(awbn, weight)
    shipment_not_found = []
    count =0
    for awb, wt in awb_wt:
        s = Shipment.objects.filter(airwaybill_number=awb).update(actual_weight=wt, volumetric_weight=wt, chargeable_weight=wt)
        if s:
            update_shipment_changelog(Shipment.objects.get(airwaybill_number=awb), 'actual_weight',request.user, wt, '')
            count = count+1
            if shipment.shipment_date.month != datetime.date.today().month:
                revision = True
            else:
                revision = False

            if int(shipment.shipper.id) == 6:
                update_jasper_awb(awb)
            else:
                update_shipment_pricing(awb, revision=revision)
        else:
            shipment_not_found.append(int(awb))


def update_lbh_weight(file_path):
    wb = xlrd.open_workbook(file_path)
    sh = wb.sheet_by_index(0)
    awbn = sh.col_values(0)[1:]
    weight= sh.col_values(1)[1:]
    length = sh.col_values(2)[1:]
    breadth = sh.col_values(3)[1:]
    height = sh.col_values(4)[1:]
    awb_wt = zip(awbn, weight,length,breadth,height)
    shipment_not_found = []
    error_list = []
    count =0

    for awb, wt, le, bre, hei in awb_wt:
      s = Shipment.objects.filter(airwaybill_number=awb)\
                .update(actual_weight=wt, length=le, breadth=bre, height=hei, volumetric_weight=0)
       
      if s:
        count = count+1
        shipment = Shipment.objects.get(airwaybill_number=awb)
        shipment.set_chargeable_weight
        if shipment.shipment_date.month != datetime.date.today().month:
            revision = True
        else:
            revision = False
        try:
            if int(shipment.shipper.id) == 6:
                update_jasper_awb(awb)
            else:
                update_shipment_pricing(awb,revision=revision)
        except:
            error_list.append(int(awb))

      else:
        shipment_not_found.append(int(awb))
      print count

    if error_list:
        ecomm_send_mail(
            'Weight Update Failed', '', 
            ['jinesh@prtouch.com', 'birjus@ecomexpress.in','onkar@prtouch.com','jignesh@prtouch.com'],
            str(error_list)
        ) 

def convert_to_cod(awb, coll_val):
    shipment = Shipment.objects.get(airwaybill_number=awb)
    if shipment.product_type == 'cod' or shipment.billing:
        return False 

    cod = Product.objects.get(product_name='cod')
    shipment.shipext.product = cod
    shipment.shipext.save()

    shipment.product_type = 'cod'
    shipment.collectable_value = coll_val
    shipment.save()

    shipment = Shipment.objects.get(airwaybill_number=awb)
    if int(shipment.shipper.id) == 6:
        update_jasper_awb(awb)
    else:
        update_shipment_pricing(awb)
