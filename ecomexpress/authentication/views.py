import ntpath
import datetime
import string, random
import xlrd
import mimetypes

from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.contrib import auth
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from django.views.defaults import page_not_found
from django.conf import settings
from django.core.servers.basehttp import FileWrapper

from privateviews.decorators import login_not_required
from customer.models import Customer
from authentication.models import get_url_for_user
from service_centre.general_updates import *
from authentication.models import *
from reports.ecomm_mail import ecomm_send_mail_content
from authentication.forms import OutscanEmployeeForm, EmployeeMasterForm

#Displaying all Employees
#@director_only
def employee(request):
    employees = EmployeeMaster.objects.all().exclude(staff_status=2)
    employeesinactive = EmployeeMaster.objects.all().filter(staff_status=2)
    form = OutscanEmployeeForm()
    return render_to_response("authentication/employee.html",
                              {'employees':employees,'employeesinactive':employeesinactive,'outempform':form},
                               context_instance=RequestContext(request))

def outemp(request):
    if request.method == "POST":
        form = OutscanEmployeeForm(request.POST)
        if form.is_valid():
            employee_code = form.cleaned_data['employee_code']
            firstname = form.cleaned_data['firstname']
            lastname = form.cleaned_data['lastname']
            service_centre = form.cleaned_data['service_centre']
            de = Department.objects.get(name="Outsourced")
            emp = EmployeeMaster.objects.filter(employee_code=employee_code)
            if emp.exists():
                employees = EmployeeMaster.objects.exclude(staff_status=2)
                employeesinactive = EmployeeMaster.objects.filter(staff_status=2)
                error = "Employee code already exists."
                form = OutscanEmployeeForm()
                return render_to_response("authentication/employee.html",
                                          {'employees':employees,
                                             'employeesinactive':employeesinactive,
                                             'outempform':form,'emperror':error},
                                           context_instance=RequestContext(request))
            emp_master = form.save(commit=True)
            return HttpResponseRedirect('/authentication/employee/')
        else:
            return HttpResponse(form.errors)

def employee_registration(request):
    if request.method == "POST":
        form = EmployeeMasterForm(request.POST)

        try:
            user = User.objects.get(email=request.POST['email'])
            if EmployeeMaster.objects.filter(user=user):
                return HttpResponse('Email already exists')
        except:
            pass
        if form.is_valid():
            employee_code = form.cleaned_data['employee_code']
            emp = EmployeeMaster.objects.filter(employee_code=employee_code)
            if emp:
                employees = EmployeeMaster.objects.all().exclude(staff_status=2)
                employeesinactive = EmployeeMaster.objects.all().filter(staff_status=2)
                error = "Employee code already exists."
                form = OutscanEmployeeForm()
                return render_to_response("authentication/employee.html",
                                          {'employees':employees,
                                             'employeesinactive':employeesinactive,
                                             'outempform':form,'emperror':error},
                                           context_instance=RequestContext(request))
            emp_master = form.save(commit=True)

            #for password period
            to_day = datetime.datetime.today()
            from_date = datetime.datetime.today()
         
            try:
                c = Customer.objects.get(code=str(emp_master.lastname))
                end_date = datetime.datetime(to_day.year+3, to_day.month, to_day.day, 0, 0, 0)
            except Customer.DoesNotExist:
                end_date = from_date + datetime.timedelta(days=30)

            PasswordPeriod.objects.create(user=emp_master, start_date=from_date, end_date=end_date)
            #End password period
            #sending email
            subject = "Registration for Ecom Express"
            email_msg = "Dear "+str(emp_master.firstname)+", \n Please note your login details. Username: "+str(emp_master.user.username)+" and Password: "+str(emp_master.user.password)+" Please login at eepl.ecomexpress.in to view your profile. Incase of technical difficulty write back to us at support@ecomexpress.in \n Thank You, \n Ecom Express Team"
            to_email = emp_master.email
            from_email = "support@ecomm.com"
            send_mail(subject,email_msg,from_email,[to_email])

            return HttpResponseRedirect('/authentication/employee/')
        else:
            return HttpResponse(form.errors)
    else:
        total_emp = EmployeeMaster.objects.filter().order_by("-id")[:1]
        emp_code = str(int(total_emp[0].id)+1)
        employee_code = str(emp_code)+("".join([random.choice(string.digits) for x in range(1, 6-int(len(emp_code)))]))
        form = EmployeeMasterForm(initial={'employee_code':employee_code})
        return render_to_response("authentication/registration.html",
                                  {'emp_form':form},
                                  context_instance=RequestContext(request))

#Editing Employees details
def edit_employee(request, id):
   employees = EmployeeMaster.objects.get(id=id)

   if request.method == "POST":
       form = EmployeeMasterForm(request.POST,instance=employees)
       if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect('/authentication/employee/')
       else:
            return HttpResponse(form.errors)
   else:
       form = EmployeeMasterForm(instance=employees)
       return render_to_response("authentication/registration.html",
                {'emp_form':form, 'status':'edit', 'id':id},
                context_instance=RequestContext(request))

#Deleting an Employee
def delete_employee(request, id):
   employees = EmployeeMaster.objects.get(id=id)
   user = User.objects.get(id=employees.user_id)
   user.is_active = False #Deactivating employees user profile
   employees.delete()
   return HttpResponseRedirect('/authentication/employee/')

#Login Authentication
@login_not_required
def login_authenticate(request):
     if request.POST:
         username = request.POST['username']
         password = request.POST['password']
         newuser = auth.authenticate(username=username, password=password)
         if newuser is None:
             return render_to_response("authentication/login.html",
                                  {"error": "Username and Password doesn't match."},
                                  context_instance=RequestContext(request))

         login(request, newuser)
         if not newuser.is_active:
             return render_to_response("authentication/login.html",
                                  {"error": "User Account Doesn't Exist."},
                                  context_instance=RequestContext(request))

         e=EmployeeMaster.objects.get(user__id =newuser.id)
         to_day = datetime.datetime.today()
         p = PasswordPeriod.objects.filter(user=e)
         if p.exists():
            passperiod = p.latest('start_date')
         else:
            try:
                c = Customer.objects.get(code=str(e.lastname))
                end_date = datetime.datetime(to_day.year+3, to_day.month, to_day.day, 0, 0, 0)
            except Customer.DoesNotExist:
                end_date = to_day+datetime.timedelta(days=30)
            passperiod = PasswordPeriod.objects.create(user=e,
                            start_date=to_day,
                            end_date=end_date)

         if passperiod.end_date < to_day:
            logout(request)
            return HttpResponseRedirect('/authentication/update_password/')
         redirect_url = get_url_for_user(request.user)
 #        redirect_url = '/track_me/?awb=&order='
         return HttpResponseRedirect(redirect_url)
     else:
        return render_to_response("authentication/login.html",
                                  context_instance=RequestContext(request))

#Logout user
def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/")

def change_password(request):
    if request.POST:
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == "":
            return HttpResponse("Please enter password")
        if password1 <> password2:
            return HttpResponse("Password does not match")

        u = request.user
        if u.check_password(password1):
          warning = "Please use another password"
          return render_to_response("authentication/change_password.html", {"warning":warning},
                                  context_instance=RequestContext(request))
        else:
          p = PasswordPeriod.objects.filter(user=u.employeemaster).latest('start_date')
          from_date = datetime.datetime.today()
          to_date = from_date + datetime.timedelta(days=30)
          p.start_date = from_date
          p.end_date = to_date
          p.save()
          u.set_password(password1)
          u.save()
        return HttpResponseRedirect('/pickup/')
    else:
        return render_to_response("authentication/change_password.html",
                                  context_instance=RequestContext(request))

@login_not_required
def update_password(request):
    if request.method != 'POST':
        return render_to_response("authentication/update_password.html",
                                  context_instance=RequestContext(request))
    elif request.method == 'POST':
        username = request.POST['UserName']
        passwordold = request.POST['passwordold']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == "" or password2 == "" or password1 != password2:
            return render_to_response("authentication/update_password.html",
                                  {"warning": "Invalid Passwords Entry."},
                                  context_instance=RequestContext(request))

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return render_to_response("authentication/update_password.html",
                                  {"warning": "UserName matching User Does Not Exist"},
                                  context_instance=RequestContext(request))

        if not user.check_password(passwordold):
            return render_to_response("authentication/update_password.html",
                                  {"warning":"Incorrect Current Password"},
                                  context_instance=RequestContext(request))

        if user.check_password(password1):
            return render_to_response("authentication/update_password.html",
                             {"warning":"You can't use your old password. Please use another one."},
                             context_instance=RequestContext(request))

	user.set_password(password1)
	user.save()
	empmaster = user.employeemaster
	from_date = datetime.datetime.today()
	to_date = from_date + datetime.timedelta(days=30)
	PasswordPeriod.objects.filter(user=empmaster).update(start_date=from_date, end_date=to_date)

	newuser = auth.authenticate(username=user.username, password=password1)
	login(request, newuser)
        redirect_url = get_url_for_user(request.user)
        return HttpResponseRedirect(redirect_url)

@login_not_required
def access_denied(request):
    return render_to_response("authentication/access_denied.html",
                                  context_instance=RequestContext(request))

def active_employee(request, id):
    employees = EmployeeMaster.objects.get(id=id)
    activate_employees([employees.employee_code])
    employees = EmployeeMaster.objects.all()
    return HttpResponseRedirect('/authentication/employee/')

def deactive_employee(request, id):
    employees = EmployeeMaster.objects.get(id=id)
    deactivate_employees([employees.employee_code])
    employees = EmployeeMaster.objects.all()
    return HttpResponseRedirect('/authentication/employee/')

@login_not_required
@csrf_exempt
def myresetpassword(request):
    if request.method == 'POST':
        id_code = request.POST['id_code']
        emp = EmployeeMaster.objects.filter(employee_code =id_code)
        if emp:
            employee = emp[0]
            char_set = string.ascii_uppercase + string.digits
            password = ''.join(random.sample(char_set*6, 6))
            employee.user.set_password(password)
            employee.user.save()
            subject = "Password Reset"
            email_msg = "Dear "+str(employee.firstname)+", \n Please note your login details. Username: "+str(employee.user.username)+" and Password: "+str(password)+" Please login at eepl.ecomexpress.in to view your profile. Incase of technical difficulty write back to us at support@ecomexpress.in \n Thank You, \n Ecom Express Team"
            to_email = ['arun@prtouch.com','jinesh@prtouch.com',employee.email]
            ecomm_send_mail_content(subject, email_msg, to_email)
            data = {'title':'Your new password has been mailed to {0}'.format(employee.email)}
    else:
        data = {}
    return render_to_response("authentication/resetpassword.html",
                            data, context_instance=RequestContext(request))

def mass_employee_creation(request):
    form = OutscanEmployeeForm()
    if request.method == 'POST':
        ship_file = request.FILES['emp_file']
        content = ship_file.read()
        wb = xlrd.open_workbook(file_contents=content)
        sheetnames = wb.sheet_names()
        sh = wb.sheet_by_name(sheetnames[0])
        emp_code = sh.col_values(0)[1:]
        firstname = sh.col_values(1)[1:]
        lastname = sh.col_values(2)[1:]
        usertype = sh.col_values(3)[1:]
        department = sh.col_values(4)[1:]
        email = sh.col_values(5)[1:]
        add1 = sh.col_values(6)[1:]
        add2 = sh.col_values(7)[1:]
        add3 = sh.col_values(8)[1:]
        service_centre = sh.col_values(9)[1:]
        mobile_number = sh.col_values(10)[1:]
        error_list = []
        emp_zip = zip(emp_code, firstname,lastname,usertype,department,email,add1,add2,add3,service_centre,mobile_number)
        for emp_code, firstname, lastname, usertype, department, email,add1,add2,add3,service_centre,mobile_number in emp_zip:
            try:
                emp_code = int(emp_code)
            except ValueError:
                emp_code = emp_code
            employees = EmployeeMaster.objects.filter(employee_code=emp_code)
            if employees.exists():
                error_list.append('{0} : Employee code already used'.format(emp_code))
                continue
            employees = EmployeeMaster.objects.filter(email=email)
            if employees.exists():
                error_list.append('{0} : Email already used'.format(email))
                continue
            user = User.objects.create_user(username=email,email=email,password=emp_code)
            sc = ServiceCenter.objects.filter(center_shortcode=service_centre)
            if sc.exists():
                sc = sc[0]
            else:
                error_list.append('{0} : Service Center does not exist'.format(service_centre))
                continue

            dep = Department.objects.filter(name=department)
            if dep.exists():
                dep = dep[0]
            else:
                error_list.append('{0} : Service Center does not exist'.format(department))
                continue

            emp = EmployeeMaster.objects.create(user=user, employee_code=emp_code, firstname=firstname, lastname=lastname,
                        user_type=usertype, email=email, address1=add1, address2=add2, address3=add3, service_centre=sc,
                        mobile_no=mobile_number,department=dep)
    employees = EmployeeMaster.objects.all().exclude(staff_status=2)
    employeesinactive = EmployeeMaster.objects.all().filter(staff_status=2)
    return render_to_response("authentication/employee.html",
                              {'error_list':error_list,'employees':employees,
                                 'employeesinactive':employeesinactive,
                                 'outempform':form},
                               context_instance=RequestContext(request))


@login_required
def serve_file(request, path):
    file_name = settings.STATIC_ROOT + '/uploads/' + path
    head_name, tail_name = ntpath.split(file_name)
    try:
        f = file(file_name, "rb")
    except Exception, e:
        return page_not_found(request, template_name='404.html')
    try:
        wrapper = FileWrapper(f)
        response = HttpResponse(wrapper, mimetype=mimetypes.guess_type(file_name)[0])
        response['Content-Length'] = os.path.getsize(file_name)
        response['Content-Disposition'] = 'attachment; filename={0}'.format(tail_name)
        return response
    except Exception, e:
        return page_not_found(request, template_name='500.html')
