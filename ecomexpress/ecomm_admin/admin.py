from ecomm_admin.models import *
from django.contrib import admin

#class ClientAdmin(admin.ModelAdmin):
# list_display = ('name', 'partner','email', 'mobile','status')
# search_fields = ['name']


admin.site.register(Legality)
admin.site.register(Brentrate)
#admin.site.register(ValueAddedCargoHandlingSurcharge)
admin.site.register(BrandedFleet)
admin.site.register(BrandedFullTimeEmployee)
admin.site.register(SOPDays)
admin.site.register(PickupStatusMaster)
admin.site.register(ShipmentStatusMaster)
admin.site.register(Mode)
admin.site.register(Coloader)
admin.site.register(HolidayMaster)
admin.site.register(ServiceTax)
