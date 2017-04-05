from location.models import Region, Zone, State, City, Branch, \
                            AreaMaster, ServiceCenter, PinRoutes, Pincode, Address, Contact, TransitMasterGroup, \
                            TransitMaster, ServiceCenterTransitMasterGroup, TransitMasterCutOff, PickupPincodeServiceCentreMAP, \
                            RTSPincodeServiceCentreMAP, RTOPincodeServiceCentreMAP, ZoneLabel
from django.contrib import admin

#class TransitMasterAdmin(admin.ModelAdmin):
#    list_display = ('transit_master', 'dest_service_center', 'duration', 'cutoff_time', 'mode')
#    search_fields = ('pincode', 'service_center__city__city_name', 'service_center__center_name')

class PincodeAdmin(admin.ModelAdmin):
    list_display = ('pincode', 'service_center')
    search_fields = ('pincode', 'service_center__city__city_name', 'service_center__center_name')

class TransitMasterAdmin(admin.ModelAdmin):
    list_display = ('transit_master', 'org_service_center','dest_service_center', 'duration', 'cutoff_time')
    search_fields = ('transit_master__name', 'org_service_center__center_shortcode', 'dest_service_center__center_shortcode', 'org_service_center__center_name', 'dest_service_center__center_name', 'duration')

class TransitMasterCutOffAdmin(admin.ModelAdmin):
    list_display = ('transit_master_orignal', 'transit_master_dest','cutoff_time')
    search_fields = ('transit_master_orignal', 'transit_master_dest', 'cutoff_time')

class PickupPincodeServiceCentreMAPAdmin(admin.ModelAdmin):
    list_display = ('pincode', 'service_center', 'added_on', 'updated_on')
    search_fields = ('pincode', 'service_center')

class RTSPincodeServiceCentreMAPAdmin(admin.ModelAdmin):
    list_display = ('pincode', 'service_center', 'added_on', 'updated_on')
    search_fields = ('pincode', 'service_center')

class RTOPincodeServiceCentreMAPAdmin(admin.ModelAdmin):
    list_display = ('pincode', 'service_center', 'added_on', 'updated_on')
    search_fields = ('pincode', 'service_center')

class ZoneLabelAdmin(admin.ModelAdmin):
    list_display = ('name','name')

class ZoneAdmin(admin.ModelAdmin):
    list_display = (':', 'service_center')
    search_fields = ('pincode', 'service_center__city__city_name', 'service_center__center_name')


admin.site.register(ZoneLabel,ZoneLabelAdmin)
admin.site.register(Region)
admin.site.register(Zone)
admin.site.register(State)
admin.site.register(City)
admin.site.register(Branch)
admin.site.register(AreaMaster)
admin.site.register(ServiceCenter)
admin.site.register(PinRoutes)
admin.site.register(Pincode, PincodeAdmin)
admin.site.register(Address)
admin.site.register(TransitMasterGroup)
admin.site.register(TransitMaster, TransitMasterAdmin)
admin.site.register(ServiceCenterTransitMasterGroup)
admin.site.register(TransitMasterCutOff,TransitMasterCutOffAdmin)
admin.site.register(PickupPincodeServiceCentreMAP,PickupPincodeServiceCentreMAPAdmin)
admin.site.register(RTSPincodeServiceCentreMAP,RTSPincodeServiceCentreMAPAdmin)
admin.site.register(RTOPincodeServiceCentreMAP,RTOPincodeServiceCentreMAPAdmin)

