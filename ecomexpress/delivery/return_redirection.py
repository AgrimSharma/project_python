import datetime

from airwaybill.models import AirwaybillNumbers, AirwaybillCustomer
from billing.charge_calculations import add_to_shipment_queue
from delivery.models import get_expected_dod
from ecomm_admin.models import ShipmentStatusMaster
from location.models import Pincode
from service_centre.models import Shipment, ShipmentExtension
from service_centre.general_updates import update_shipment_history

def update_rts_shipment(awb, ref_awb, employee):
    # CHECKS
    # 1) if Reference airwaybill number already used (AirwaybillNumber object
    # True) or Shipment Exists Error: 'Reference Airwaybill already used
    # 2) Parent shipment's rts_status should be 0. Error: RTS Shipment can't
    # again RTS'd
    # 3) Parent shipment's status should be 8. Error: Delivered Shipment can't
    # be RTS'd
    # closure code is not allowed to edit

    try:
        parent_ship = Shipment.objects.get(airwaybill_number=awb)
        if parent_ship.status not in [1, 2, 6, 8]:
            return {
                'message': "Please update shipment as undelivered first",
                'success': False}
        elif parent_ship.rts_status != 0:
            return {
                'message': "RTS shipment cat'be RTS'd again.",
                'success': False}
        elif parent_ship.reason_code and parent_ship.reason_code.code in\
                [111, 999, 888, 333, 310, 200, 208, 302, 311]:
            msg = parent_ship.reason_code.code_description
            return {
                'message': "{0} cat'be RTS'd".format(msg),
                'success': False}
        elif parent_ship.reverse_pickup:
            return {
                'message': "Reverse shipment cat'be RTS'd",
                'success': False}
    except Shipment.DoesNotExist:
        return {
            'message': "Parent Airwaybill number Doesn't Exist",
            'success': False}

    try:
        awb_num = AirwaybillNumbers.objects.get(airwaybill_number=ref_awb)
        if awb_num.status:
            return {
                'message': "RTS Airwaybill number already used.",
                'success': False}
        try:
            if awb_num.awbc_info.all()[0].customer.id != 12:
                return {
                    'message': "Child Airwaybill Number Should belong to EcomExpress",
                    'success': False}
        except IndexError:
            pass
    except AirwaybillNumbers.DoesNotExist:
        return {
            'message': "Invalid RTS Airwaybill number.",
            'success': False}
    try:
        Shipment.objects.get(airwaybill_number=ref_awb)
        return {
            'message': "RTS Airwaybill number already used.",
            'success': False}
    except Shipment.DoesNotExist:
        pass

    # PROCESSING - get the following data to update shipment and rts-shipment
    # 1) reference_sc, reference_pincode, reference_destination
    #     get sc, pincode, city based on pickup subcustomer
    #     dest_city = shipment.pickup.subcustomer_code.city
    #     if ShipperMapping Exists:
    #         pincode = shippermapping.ref_pincode
    #         sc = pincode.service_center
    #     else:
    #         pincode = shipment.pickup.pincode
    #         sc = shipment.pickup.subcustomer_code.address.pincode.sc
    #     (if pickup.subcustomer does not exist, take pincode from pickup)
    pincode = None
    if parent_ship.pickup.subcustomer_code:
        pincode = parent_ship.pickup.subcustomer_code.address.pincode
    if not pincode:
        pincode = parent_ship.pickup.pincode
    ref_pincode = Pincode.objects.get(pincode=pincode.strip())
    # get the return sc from pincode if it exists 
    # else take the pincode service center
    if ref_pincode.return_sc:
        ref_sc = ref_pincode.return_sc
    else:
        ref_sc = ref_pincode.service_center
    ref_city = ref_sc.city
    reason_code = ShipmentStatusMaster.objects.get(id=5)

    # 2) get expected dod:
    expected_dod = get_expected_dod(parent_ship.current_sc)

    if not expected_dod:
        expected_dod = parent_ship.expected_dod

    # UPDATES
    # 1) RTSShipment
    #    - ref airwaybill number
    #    - awb
    #    - inscan_date = now
    #    - shipment_date = None
    #    - status = 1
    #    - rd_status = 0
    #    - rto_status = 0
    #    - rts_status = 1
    #    - status_type = 0
    #    - return_shipment = 3
    #    - rts_date = now
    #    - service center
    #    - pincode
    #    - original_dest
    #    - expected_dod
    now = datetime.datetime.now()
    ref_ship = Shipment.objects.create(
        airwaybill_number=ref_awb, ref_airwaybill_number=awb,
        inscan_date=now, shipment_date=now,
        status=1, rd_status=0, rto_status=1, rts_status=1,
        status_type=0, return_shipment=3, rts_date=now,
        service_centre=ref_sc, pincode=pincode,
        expected_dod=expected_dod, destination_city=ref_city,
        pickup = parent_ship.pickup,
        reverse_pickup = parent_ship.reverse_pickup,
        order_number = parent_ship.order_number,
        product_type = parent_ship.product_type,
        shipper = parent_ship.shipper,
        consignee= parent_ship.consignee,
        consignee_address1= parent_ship.consignee_address1,
        consignee_address2= parent_ship.consignee_address2,
        consignee_address3= parent_ship.consignee_address3,
        consignee_address4= parent_ship.consignee_address4,
        manifest_location = parent_ship.manifest_location,
        current_sc = parent_ship.current_sc,
        state = parent_ship.state,
        mobile = parent_ship.mobile,
        telephone = parent_ship.telephone,
        item_description= parent_ship.item_description,
        pieces= parent_ship.pieces,
        collectable_value= parent_ship.collectable_value,
        declared_value= parent_ship.declared_value,
        actual_weight= parent_ship.actual_weight,
        chargeable_weight = parent_ship.chargeable_weight,
        volumetric_weight= parent_ship.volumetric_weight,
        length= parent_ship.length,
        breadth= parent_ship.breadth,
        height= parent_ship.height,
        reason_code = parent_ship.reason_code,
        remark = parent_ship.remark,
        original_dest = parent_ship.original_dest,
        rts_reason = parent_ship.rts_reason,
        sdd = parent_ship.sdd,
        rejection = parent_ship.rejection,
        sdl = parent_ship.sdl,
        tab = parent_ship.tab)

    AirwaybillNumbers.objects.filter(airwaybill_number=awb).update(status=True)

    # 2) add shipment to queue(ref_ship)
    add_to_shipment_queue(ref_awb)

    # 3) update_history(ref_ship, 1, "Returing to Shipper: Original airwaybilll
    # number: (parent awb), reason_code)
    update_shipment_history(
        ref_ship, reason_code=reason_code, employee_code=employee,
        sc=employee.service_centre, status=1,
        remarks="Returing to Shipper: Original airwaybillnumber:{0}".format(awb)
    )

    # 4) Shipment
    #    - ref_airwaybill number
    #    - updated_on
    #    - rts_date
    #    - reason_code (5/777)
    #    - rto_status (1)
    #    - rts_status (2)
    #    - return_shipment (3)
    parent_ship.ref_airwaybill_number = ref_awb
    parent_ship.updated_on = now
    parent_ship.rts_date = now
    parent_ship.reason_code = reason_code
    parent_ship.rto_status = 1
    parent_ship.rts_status = 2
    parent_ship.return_shipment = 3
    parent_ship.save()

    ShipmentExtension.objects.filter(shipment=parent_ship).update(misroute_code=reason_code)

    # 5) update shipment history (shipment, status = 17, remarks =
    #    "Redirection under new airwaybill number, reason_code=777)
    update_shipment_history(
        parent_ship, reason_code=reason_code, employee_code=employee,
        sc=employee.service_centre, status=17,
        remarks=("Redirection under new airwaybill number {0}".format(ref_awb)))
    return {
        'success': True, 
        'message': "RTS Succesfully updated for {0}".format(awb,)}
