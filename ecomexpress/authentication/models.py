import pdb
from django.db import models
from django.contrib.auth.models import User
from location.models import ServiceCenter
# Create your models here.


GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

USER_TYPES = (
        ('Staff', 'Staff'),
        ('Supervisor', 'Supervisor'),
        ('Sr Supervisor', 'Sr Supervisor'),
        ('Manager', 'Manager '),
        ('Sr Manager', 'Sr Manager'),
        ('Director', 'Director'),
        ('Customer', 'Customer'),
    )

DEPARTMENT_LIST = (
        ('Account', 'Account'),
        ('Customer Service', 'Customer Service'),
        ('Customer Service Accounts', 'Customer Service Accounts'),
        ('Finance', 'Finance'),
        ('HR', 'HR'),
        ('Hub', 'Hub'),
        ('IT','IT'),
        ('Operations','Operations'),
        ('Sale', 'Sale'),
        )
LOGIN_CHOICES = (
    (0, "Allow Concurrent Login (Required)"),
    (0, 'False'),
    (1, 'True')
)

class Department(models.Model):
    name = models.CharField(max_length=150, choices=DEPARTMENT_LIST)
    added_on = models.DateTimeField(auto_now=True)

    def __unicode__(self):
       return self.name


#Employee Details table, additional information to be fetched/sent from/to orangeCRM
class EmployeeMaster(models.Model):
    user = models.OneToOneField(User, null=True, blank=True)
    employee_code = models.CharField(max_length=10, null=True, blank=True)
    firstname = models.CharField(max_length=60)
    lastname = models.CharField(max_length=60)
    user_type = models.CharField(max_length = 15, choices=USER_TYPES, blank=True, default='Staff',)
    email = models.CharField(max_length=100, null=True, blank=True)
    address1 = models.CharField(max_length=200, null=True, blank=True)
    address2 = models.CharField(max_length=200, null=True, blank=True)
    address3 = models.CharField(max_length=200, null=True, blank=True)
    service_centre = models.ForeignKey(ServiceCenter, null=True, blank=True)
    base_service_centre = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name='emp_base_sc')
    mobile_no = models.CharField(max_length=60)
    department = models.ForeignKey(Department)
    login_active = models.IntegerField(max_length=2, default=0)
    staff_status = models.IntegerField(max_length=2, default=0) #0:perm, 1:temp, 2:deact
    allow_concurent_login = models.IntegerField(max_length=2, choices=LOGIN_CHOICES, null=True, blank=True, default=0)
    query_limit = models.IntegerField(max_length=5, null=True, blank=True, default=50)
    ebs = models.BooleanField(default=False)
    ebs_customer = models.ForeignKey('customer.Customer', blank=True, null=True)
    temp_emp_status = models.BooleanField(default=False)
    effective_date=models.DateField(null=True, blank=True)
    temp_days=models.IntegerField(max_length=5, null=True, blank=True, default=7)

   #TODO: fields to be included in orangeCRM
   #dob = models.DateField(null=True, blank=True)
   #gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
   #permanent_address = models.CharField(max_length=200, null=True, blank=True)
   #refrence_1 = models.CharField(max_length=60, null=True, blank=True)
   #refrence_2 = models.CharField(max_length=60, null=True, blank=True)
   #blood_group = models.CharField(max_length=5, null=True, blank=True)
   #pan_card = models.CharField(max_length=20, null=True, blank=True)
   #bank_name = models.CharField(max_length=70, null=True, blank=True)
   #  bank_accountnumber
   # bank_ifsccode

   #nomination_1 = models.CharField(max_length=60, null=True, blank=True)
   #nomination_2 = models.CharField(max_length=60, null=True, blank=True)
   #pf_nominee = models.CharField(max_length=60, null=True, blank=True)
   #df_nominee = models.CharField(max_length=60, null=True, blank=True)

    def __unicode__(self):
        return str(self.firstname) + " " + str(self.lastname) + " - "+ str(self.employee_code)

    def get_name_with_email(self):
        return str(self.firstname) + " -  " + str(self.lastname) + " - " + str(self.email)

    def get_name_with_employee_code(self):
        #return str(self.firstname) + " -  " + str(self.lastname) + " - " + str(self.employee_code)
        return str(self.firstname) + " - " + str(self.employee_code)

    def save(self,*args, **kwargs):

        if not self.query_limit:
            self.query_limit = 50
        super(EmployeeMaster, self).save(*args, **kwargs)

class EmployeeMasterCustomer(models.Model):
    customer = models.ForeignKey('customer.Customer')
    employee_master = models.ForeignKey(EmployeeMaster)
    added_on = models.DateTimeField(auto_now=True)

class PasswordPeriod(models.Model):
    user = models.ForeignKey("authentication.EmployeeMaster")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

def get_url_for_user(user):
    usr_url_dict = {
        'reports':'/reports',
        'pickup':'/pickup',
        'customer':'/customer',
        'billing':'/billing',
        'delivery':'/delivery',
        'employee':'/authentication/employee',
        'track_me':'/track_me/?awb=&order=',
        'cust_login':'/track_me/customer_status/'
    }

    #try:
        #user.employeemaster.department
    #except Department.DoesNotExist:
        #return usr_url_dict.get('track_me')

    if user.employeemaster.user_type == 'Director':
        return usr_url_dict.get('pickup')
    elif user.employeemaster.user_type == 'Customer':
        return usr_url_dict.get('cust_login')
    elif user.employeemaster.department.name == 'HR':
        return usr_url_dict.get('employee')
    elif user.employeemaster.department.name == 'Sale':
        return usr_url_dict.get('track_me')
    elif user.employeemaster.department.name == 'Finance':
        return usr_url_dict.get('delivery')
    elif user.employeemaster.department.name == 'IT' and user.employeemaster.user_type == 'Sr Manager':
        return usr_url_dict.get('pickup')
    elif user.employeemaster.department.name == 'IT' and user.employeemaster.user_type == 'Supervisor':
        return usr_url_dict.get('track_me')
    elif user.employeemaster.department.name == 'IT' and user.employeemaster.user_type == 'Sr Supervisor':
        return usr_url_dict.get('reports')
    elif user.employeemaster.department.name == 'Customer Service' and user.employeemaster.user_type == 'Supervisor':
        return usr_url_dict.get('track_me')
    elif user.employeemaster.department.name == 'Customer Service' and user.employeemaster.user_type == 'Account':
        return usr_url_dict.get('pickup')
    elif user.employeemaster.department.name == 'Operations' and user.employeemaster.user_type == 'Manager':
        return usr_url_dict.get('pickup')
    elif user.employeemaster.department.name == 'Operations' and user.employeemaster.user_type == 'Staff':
        return usr_url_dict.get('delivery')
    elif user.employeemaster.department.name == 'Hub' and user.employeemaster.user_type == 'Manager':
        return usr_url_dict.get('hub')
    else:
        return usr_url_dict.get('track_me')

def is_user_allowed_access(user, access_url):
    _roles_access = {
        'remittance':['track_me', 'reports', 'customer', 'billing'],
        'cs_sr_svsr':['track_me', 'reports', 'pickup'],
        'cs_svsr':['track_me'],
        'cs_manager':['tracke_me', 'pickup', 'airwaybill', 'reports', 'delivery'],
        'cs_accounts':['tracke_me', 'pickup'],
        'op_svsr':['service-centre', 'pickup', 'delivery', 'track_me', 'reports'],
        'op_staff':['delivery', 'service_centre', 'pickup', 'track_me'],
        'hr':['track_me', 'authentication'],
        'base':['track_me'],
        'hu_manager':['track_me','hub','reports','delivery','service-centre'],
        'hub':['track_me','hub','delivery'],
        'sale':['track_me'],
        'it_sup':['track_me','airwaybill', 'billing', 'reports', 'authentication', 'customer'],
        'it_srsup':['track_me','airwaybill','billing','customer','reports', 'delivery'],
        'cu_cust':['track_me','authentication'],
        'dirc':['airwaybill','pickup','track_me','service-centre','reports','hub','billing','customer','delivery','authentication'],
        'op_mngr':['service_centre', 'pickup', 'delivery', 'track_me', 'reports','hub'],
        'acc_sup':['reports','track_me'],
        'customer':['reports','track_me']
    }

    if access_url in ['access_denied', 'static']:
        return True

    if access_url == 'hub' and user.employeemaster.service_centre.center_shortcode in\
                            ['BOM', 'BLR', 'AHH', 'JAH', 'LKH', 'DEH', 'OKP']:
        return True
    if user.employeemaster.user_type in ['Director']:
        return True
    elif user.employeemaster.department.name == 'IT' and user.employeemaster.user_type == 'Sr Manager':
        return True
    elif user.employeemaster.department.name == 'Account' and user.employeemaster.user_type == 'Supervisor':
        return True
    elif user.employeemaster.department.name == 'HR':
        return access_url in _roles_access.get('hr')
    elif user.employeemaster.department.name == 'Sale':
        return access_url in _roles_access.get('base')
    elif user.employeemaster.department.name == 'Finance' and \
            user.employeemaster.user_type in ['Sr Manager', 'Manager']:
        return access_url in _roles_access.get('remittance')
    elif user.employeemaster.department.name == 'Customer Service' \
            and user.employeemaster.user_type in ['Sr Supervisor', 'Supervisor']:
        return access_url in _roles_access.get('cs_sr_svsr')
    elif user.employeemaster.department.name == 'Customer Service' and \
            user.employeemaster.user_type == 'Manager':
        return access_url in _roles_access.get('cs_manager')
    elif user.employeemaster.department.name == 'Customer Service Accounts' \
            and user.employeemaster.user_type == 'Supervisor':
        return access_url in _roles_access.get('cs_accounts')
    elif user.employeemaster.department.name == 'Operations' and user.employeemaster.user_type == 'Supervisor':
        return access_url in _roles_access.get('op_svsr')
    elif user.employeemaster.department.name == 'Operations' and user.employeemaster.user_type == 'Staff':
        return access_url in _roles_access.get('op_staff')

    elif user.employeemaster.department.name == 'Hub' and user.employeemaster.user_type == 'Manager':
        return access_url in _roles_access.get('hu_manager')
    elif user.employeemaster.department.name == 'Hub':
        return access_url in _roles_access.get('hub')
    elif user.employeemaster.department.name == 'HR':
        return access_url in _roles_access.get('hr')
    elif user.employeemaster.department.name == 'Sale':
        return access_url in _roles_access.get('sale')
    elif user.employeemaster.department.name == 'IT' and user.employeemaster.user_type == 'Supervisor':
        return access_url in _roles_access.get('it_sup')
    elif user.employeemaster.department.name == 'IT' and user.employeemaster.user_type == 'Sr Supervisor':
        return access_url in _roles_access.get('it_srsup')
    elif user.employeemaster.department.name == 'cu_cust':
        return access_url in _roles_access.get('cu_cust')
    elif user.employeemaster.department.name == 'Operations' and user.employeemaster.user_type == 'Manager':
        return access_url in _roles_access.get('op_mngr')
    elif user.employeemaster.department.name == 'Finance' and user.employeemaster.user_type == 'Sr Supervisor':
        return access_url in _roles_access.get('acc_sup')
    elif user.employeemaster.department.name == 'Operations' and user.employeemaster.user_type == 'Customer':
        return access_url in _roles_access.get('customer')

    else:
        return access_url in _roles_access.get('base')

