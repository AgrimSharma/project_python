from shacti_api.models import *
from django.contrib import admin


class FtpAdmin(admin.ModelAdmin):
    list_display = ('service_center', 'ftp_username', 'ftp_password','ftp_ip_address')
    search_fields = ('ftp_username', 'ftp_password','ftp_ip_address')

admin.site.register(SchactiFTPDetails, FtpAdmin)
