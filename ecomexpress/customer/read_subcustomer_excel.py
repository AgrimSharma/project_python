'''
Created on 15-Apr-2013

@author: mugdha
'''
import xlrd
import re
from collections import defaultdict

from location.models import Address, Pincode
from customer.models import Shipper, Customer, ShipperMapping


def get_str(val):
    val = val.encode('ascii', 'ignore') if isinstance(val, unicode) else str(val)
    return val

def save_shipper_address(address, phone, pincode):
    ads = [get_str(x).strip() for x in address.strip().split(',')][:4]
    ads_vars = [ '', '', '', '']

    for i in range(len(ads)):
        ads_vars[i] = ads[i]

    # purify phone number
    try:
        phone = str(phone)
        phone = re.sub(r'[a-zA-Z]+', '', phone)
        phone = re.sub(r'\s+', '', phone)
        phone = phone.replace('-', '')
        if '/' in phone:
            phone = phone.split('/')[0]
        else:
            phone = phone.split(',')[0]
    except:
        phone = 0
    if len(ads_vars[0])> 99:
        ads_vars[0] = ads_vars[0][:99]
        ads_vars[1] = ads_vars[0][99:] + ads_vars[1]
    if len(ads_vars[1])> 99:
        ads_vars[1] = ads_vars[1][:99]
        ads_vars[2] = ads_vars[1][99:] + ads_vars[2]
    if len(ads_vars[2])> 99:
        ads_vars[2] = ads_vars[2][:99]
        ads_vars[3] = ads_vars[2][99:] + ads_vars[3]
    if len(ads_vars[3])> 99:
        ads_vars[3] = ads_vars[3][:99]

    adres = Address.objects.create(address1=ads_vars[0],
            address2=ads_vars[1], address3=ads_vars[2], address4=ads_vars[3],
            city=pincode.service_center.city, state=pincode.service_center.city.state,
            phone=phone, pincode=pincode.pincode)
    return adres
def removeNonAscii(s): return "".join(i for i in s if ord(i)<128)

def update_subcustomers_list(file_contents, c_id):
    """ read the data from excel file and save it into a database
        the excel columns should be in the order:
        name, address, phone, pincode as it is
    """
    errors = defaultdict(list)
    # open an excel workbook
    # filepath = '/home/mugdha/Desktop/Ecomexpress.xls'
    work_book = xlrd.open_workbook(file_contents=file_contents)

    # grab a list of worksheets in a workbook
    work_sheet = work_book.sheet_by_index(0)
    # TODO check whether column headings are as specified.

    # TODO: iterate over each worksheet in a workbook and check whether there is any content

    cust = Customer.objects.get(pk=c_id)
    # iterate over each row of worksheet: first row is supposed to be columns heading
    for x in range(1, work_sheet.nrows):
        # grab the cell content of each row of worksheet and add it to a empty list
        row_data = []
        for y in range(work_sheet.ncols):
            # cell_type = work_sheet.cell_type(x,y)
            cell_value = work_sheet.cell_value(x,y)
            row_data.append(cell_value)

        # save the data from list to corresponding models
        name = removeNonAscii(row_data[0]) # second column is supposed to be name of subcustomer
        address = row_data[1]
        phone = row_data[2]
        pin = row_data[3]
        return_pin = row_data[4] if row_data[4] else None
        alias_code = row_data[5] if row_data[5] else None

        if len(name) > 100:
            errors['file_error'].append(row_data)
            continue
        # if pincode not existing in list then raise error
        try:
            pin = str(int(pin))
            pincode = Pincode.objects.get(pincode=pin)
            if return_pin:
               return_pincode = Pincode.objects.get(pincode=return_pin)
        except (Pincode.DoesNotExist, ValueError):
            # we can not save this data to database as we dont have
            # this pin in our list
            errors['pin_error'].append(row_data)
            continue

        phone = "" if not phone else phone
        #if not Shipper.objects.filter(customer=cust, name=name, address__pincode=pincode.pincode).exists():
        if not Shipper.objects.filter(customer=cust, name=name, address__pincode = pin):
            adres = save_shipper_address(address, phone, pincode)
            # Before saving new sub customer check for duplication
            shp = Shipper.objects.create(customer=cust, name=name, address=adres, alias_code = alias_code)
             
        else:
           shp = Shipper.objects.get(customer=cust, name=name, address__pincode = pin)
           shp.alias_code = alias_code
           shp.save()
        if not ShipperMapping.objects.filter(shipper=shp):
            ShipperMapping.objects.create(shipper=shp, forward_pincode = pin, return_pincode = return_pin)
        else:
            ShipperMapping.objects.filter(shipper=shp).update(forward_pincode = pin, return_pincode = return_pin)
    return errors
