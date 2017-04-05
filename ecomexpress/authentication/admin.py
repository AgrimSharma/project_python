from authentication.models import *
from django.contrib import admin

#class ClientAdmin(admin.ModelAdmin):
# list_display = ('name', 'partner','email', 'mobile','status')
# search_fields = ['name']


admin.site.register(EmployeeMaster)
