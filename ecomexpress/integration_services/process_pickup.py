import datetime
import re
from collections import defaultdict
from django.http import HttpResponse

# from openpyxl.reader.excel import load_workbook
import xlrd

from customer.models import Customer, Shipper, ShipperMapping
from location.models import Pincode, Address
from .models import PickupEnroll


class ProcessPickup(object):

    def __init__(self, file_content, user):
        self.file_content = file_content
        self.user = user
        self.customer_codes = list(Customer.objects.filter(
            activation_status=True).values_list('code', flat=True))
        # format will be {'row_number': ['error message 1',.. ]}
        self.errors = defaultdict(list)
        self.pickups = []

    def clean_customer(self, code):
        if str(int(code)) in self.customer_codes:
            customer = Customer.objects.get(code=int(code))
            return True, customer
        return False, '{0}: not a valid customer code'.format(code)

    def clean_pincode(self, pincode):
        pattern = re.compile(r'[1-9][0-9][0-9][0-9][0-9][1-9]')
        if not pattern.match(str(pincode)):
            # Only accept if Pincode is 6 digits and
            # doesn't start or end with 0
            return False, "{0}: Incorrect pincode format".format(pincode)
        try:
            Pincode.objects.get(pincode=pincode)
        except Pincode.DoesNotExist:
            return False, "{0}: Pincode Doesnot Exist".format(pincode)

        return True, pincode

    def clean_long_string(self, vendor_name):
        """
        Vendor name contains alpha numeric and space
        """
        pattern = re.compile(r'[\w+\s]*')
        if not pattern.match(vendor_name):
            return False, "{0}: Incorrect format".format(vendor_name)

        return True, vendor_name

    def clean_contact(self, contact):
        pattern = re.compile(r'[\d\-\s]*')
        if not pattern.match(str(contact)):
            return False, "{0}: Incorrect format".format(contact)

        return True, contact

    def clean_number(self, contact):
        pattern = re.compile(r'[0-9]+')
        if not pattern.match(str(contact)):
            return False, "{0}: Incorrect format".format(contact)

        return True, contact

    def clean_date(self, pickup_date):
        pd = xlrd.xldate_as_tuple(int(pickup_date), 0)
        pickup_date = datetime.date(pd[0], pd[1], pd[2])
        if not pickup_date >= datetime.date.today():
            return False, "{0}: Can't be in the past".format(pickup_date)

        return True, pickup_date

    def get_row(self, row, row_count):
        success, customer = self.clean_customer(int(row[0].value))
        if not success:
            self.errors[row_count].append(customer)

        success, pincode = self.clean_pincode(int(row[1].value))
        if not success:
            self.errors[row_count].append(pincode)

        success, vendor_name = self.clean_long_string(row[2].value.strip())
        if not success:
            self.errors[row_count].append(vendor_name)

        success, vendor_address = self.clean_long_string(row[3].value.strip())
        if not success:
            self.errors[row_count].append(vendor_address)

        success, vendor_contact = self.clean_contact(row[4].value)
        if not success:
            self.errors[row_count].append(vendor_contact)
        
        
        success, shipment_count = self.clean_number(int(row[5].value))
        if not success:
            self.errors[row_count].append(shipment_count)
        '''
        success, pickup_date = self.clean_date(int(row[6].value))
        if not success:
            self.errors[row_count].append(pickup_date)
        '''
        pickup_date = datetime.datetime.strptime(row[6].value, "%d/%m/%Y")
        data = {
            'customer': customer,
            'pincode': pincode,
            'vendor_name': vendor_name,
            'vendor_address': vendor_address,
            'vendor_contact': vendor_contact,
            'shipment_count': shipment_count,
            'pickup_date': pickup_date
        }

        if len(self.errors[row_count]) > 0:
            return False, data
        else:
            return True, data

    def create_pickup(self, cleaned_row):
        customer = cleaned_row.get('customer')
        pincode = cleaned_row.get('pincode')
        vendor_name = cleaned_row.get('vendor_name')
        address = cleaned_row.get('vendor_address')
        # get shipper. if vendor name & pincode combination exists
        # use it else create it
        try:
            shipper = Shipper.objects.get(
                name=vendor_name, customer=customer, address__pincode=pincode)
        except Shipper.DoesNotExist:
            pin = Pincode.objects.get(pincode=pincode)
            address1 = address[:100]
            address2 = address[100:200]
            address3 = address[200:300]
            address4 = address[300:400]
            shipper_address = Address.objects.create(
                city=pin.service_center.city,
                state=pin.service_center.city.state,
                address1=address1, address2=address2, address3=address3,
                address4=address4, pincode=pincode)
            shipper = Shipper.objects.create(
                name=vendor_name, customer=customer, address=shipper_address)
            ShipperMapping.objects.create(
                shipper=shipper, forward_pincode=pincode, return_pincode=0)
        sc = Pincode.objects.get(pincode=pincode).pickup_sc
        # create pickup enroll object
        pinckup_enroll = PickupEnroll.objects.create(
            created_by=self.user.employeemaster,
            customer=customer,
            vendor_name=vendor_name,
            address=address,
            pincode=pincode,
            shipment_count=cleaned_row.get('shipment_count'),
            pickup_date=cleaned_row.get('pickup_date'),
            delivery_service_centre=sc,
            shipper=shipper)
        return pinckup_enroll

    def read_excel(self):
        # file_data = self.file_content.read()
        # if not file_data:
            # return {'success': False, 'messsage': 'No valid data found'}

        # wb = load_workbook(self.file_content)
        # sh = wb.get_sheet_by_name(wb.get_sheet_names()[0])
        wb = xlrd.open_workbook(file_contents=self.file_content)
        sh = wb.sheet_by_index(0)

        for row_count in range(1, sh.nrows):
            # get the row data
            success, cleaned_row = self.get_row(sh.row(row_count), row_count)
            # if success create pickup else add to error list
            if success:
                pickup = self.create_pickup(cleaned_row)
                self.pickups.append(pickup.id)
        return self.pickups, self.errors
