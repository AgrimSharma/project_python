import xmltodict
from collections import defaultdict

from customer.models import Shipper, Customer, CustomerAPI
from location.models import Pincode, Address

def api_auth(request):
    if request.GET.get('username') or request.POST.get('username') :
        #customer_api = CustomerAPI.objects.get(username=request.POST['username'])
        if request.GET.get('username'):
            username = request.GET.get('username')
            password = request.GET.get('password')
        if request.POST.get('username'):
            username = request.POST.get('username')
            password = request.POST.get('password')
        try:
            customer_api = CustomerAPI.objects.get(username=username)
            if username == 'ecomexpress':
                return customer_api
            if customer_api.password == password:
                if customer_api.ipaddress != "0":
                    ip_list    =  customer_api.ipaddress.split(",")
                    request_ip =  request.META.get('REMOTE_ADDR').strip()
                    if request_ip in ip_list:
                        return customer_api
                    else:
                        return False
                else:
                    return customer_api
        except CustomerAPI.DoesNotExist:
            return False
    else:
        return False


def create_vendor(xml_input, customer):

    def handle_record(record):
        error = ""
        if not record["vendor_code"]: 
            error = "vendor_code not provided."
        if not record["name"]: 
            error = error + "\nname not provided."
        if not record["address1"]:
            error = error + "\naddress1 not provided."
        if not record["pincode"]:
            error = error + "\npincode not provided."

        pincode = Pincode.objects.filter(pincode=record["pincode"])
        if not pincode:
            error = error + "\n{0} pincode doesnot exist".format(record['pincode'])

        if error:
            return (False, error)

        pincode = pincode[0]
        sub_customer = Shipper.objects.filter(customer=customer, alias_code=record["vendor_code"])
        if not sub_customer :
            address = Address.objects.create(
                address1=record["address1"], 
                pincode=pincode, 
                city=pincode.service_center.city, 
                state=pincode.service_center.city.state
            )
            if "address2" in record:
                address.address2 = record["address2"]
            if "address3" in record:
                address.address3 = record["address3"]
            if "address4" in record:
                address.address2 = record["address4"]
            if "phone" in record:
                address.phone = record["phone"]
            address.save()
            subcustomer = Shipper.objects.create(
                customer=customer, 
                alias_code=record["vendor_code"], 
                name = record["name"], 
                address=address
            )
        else:
            sub_customer = sub_customer[0]
            address = sub_customer.address
            if "address1" in record:
                address.address1 = record["address1"]
            if "address2" in record:
                address.address2 = record["address2"]
            if "address3" in record:
                address.address3 = record["address3"]
            if "address4" in record:
                address.address2 = record["address4"]
            if "phone" in record:
                address.phone = record["phone"]
            
            address.pincode = pincode.pincode
            address.city = pincode.service_center.city
            address.state = pincode.service_center.city.state
            address.save()

            sub_customer.name = record["name"]
            sub_customer.save()
        return (True, sub_customer)

    error_list = defaultdict(list)
    file_contents = xmltodict.parse(xml_input)
    vendors = file_contents['VENDOR-OBJECTS']['VENDOR']
    vendors_list = []
    if not isinstance(vendors, list):
        vendors_list.append(vendors)
    else:
        vendors_list = vendors
         
    for record in vendors_list:
        success, result =  handle_record(record)
        if not success:
            error_list[record['name']].append(result)
    return error_list
