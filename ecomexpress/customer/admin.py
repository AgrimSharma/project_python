from customer.models import Shipper, Customer, FuelSurcharge, FuelSurchargeZone, CashOnDelivery, CashOnDeliveryZone, FreightSlabOriginZone, FreightSlabCity, FreightSlab, FreightSlabZone, CODFreightSlab, CODFreightSlabZone, BrandedFullTimeEmployeeCustomer,BrandedFleetCustomer, MinActualWeight, VolumetricWeightDivisor, SDLSlab, SDLSlabCustomer, CustomerAPI, RTSFreightZone, RTSFuelZone, RTSFreight, RTSFuel, SDDZone, SDDSlabZone, RTSFreightSlab, RTSFreightSlabZone, ReverseFreightSlab, ReverseFreightSlabZone, FreightSlabDestZone, CustomerAWBUsedLimit
from django.contrib import admin


class VolumetricWeightDivisorAdmin(admin.ModelAdmin):
    list_display = ('customer', 'divisor')
    search_fields = ('customer__name', 'divisor')

class MinActualWeightAdmin(admin.ModelAdmin):
    list_display = ('customer', 'weight')
    search_fields = ('customer__name', 'weight')

class SDLSlabAdmin(admin.ModelAdmin):
    list_display = ('mode', 'slab', 'weight_rate', 'range_from', 'range_to')
    search_fields = ('slab', 'weight_rate')

class SDLSlabCustomerAdmin(admin.ModelAdmin):
    list_display = ('customer', 'mode', 'slab', 'weight_rate', 'range_from', 'range_to')
    search_fields = ('slab', 'weight_rate', 'customer__name')

class CustomerAPIAdmin(admin.ModelAdmin):
    list_display = ('customer', 'username', 'password', 'ipaddress')
    search_fields = ('username', 'ipaddress', 'customer__name')

class CashOnDeliveryAdmin(admin.ModelAdmin):
    list_display = ('customer', 'COD_service_charge', 'start_range', 'end_range', 'flat_COD_charge', 'minimum_COD_charge')
    search_fields = ('COD_service_charge', 'customer__name')

class CashOnDeliveryZoneAdmin(admin.ModelAdmin):
    list_display = ('customer', 'c_zone_org', 'c_zone_dest', 'COD_service_charge', 'start_range', 'end_range', 'flat_COD_charge', 'minimum_COD_charge')
    search_fields = ('c_zone_org', 'c_zone_dest', 'customer__name')

class FreightSlabAdmin(admin.ModelAdmin):
    list_display = ('customer', 'mode', 'slab', 'weight_rate', 'range_from', 'range_to')
    search_fields = ('customer__name', 'slab')
class FreightSlabZoneAdmin(admin.ModelAdmin):
    list_display = ('freight_slab', 'zone_org', 'zone_dest', 'rate_per_slab')
    search_fields = ('zone_org__zone_name', 'zone_dest__zone_name', 'freight_slab__customer__name')


class FreightSlabCityAdmin(admin.ModelAdmin):
    list_display = ('customer', 'mode', 'slab', 'weight_rate', 'range_from', 'range_to', 'city_org', 'city_dest', 'rate_per_slab')
    search_fields = ('city_org__city_name','city_dest__city_name', 'customer__name')

class FreightSlabOriginZoneAdmin(admin.ModelAdmin):
    list_display = ('customer', 'mode', 'slab', 'weight_rate', 'range_from', 'range_to', 'org_zone', 'city_dest', 'rate_per_slab')
    search_fields = ('org_zone__zone_name','city_dest__city_name', 'customer__name')

class FreightSlabDestZoneAdmin(admin.ModelAdmin):
    list_display = ('customer', 'mode', 'slab', 'weight_rate', 'range_from', 'range_to', 'dest_zone', 'city_org', 'rate_per_slab')
    search_fields = ('dest_zone__zone_name','city_org__city_name', 'customer__name')

class CODFreightSlabAdmin(admin.ModelAdmin):
    list_display = ('customer', 'mode', 'slab', 'weight_rate', 'range_from', 'range_to')
    search_fields = ('customer__name', 'slab')
class CODFreightSlabZoneAdmin(admin.ModelAdmin):
    list_display = ('freight_slab', 'zone_org', 'zone_dest', 'rate_per_slab')
    search_fields = ('zone_org__zone_name', 'zone_dest__zone_name', 'freight_slab__customer__name')

class CustomerAWBUsedLimitAdmin(admin.ModelAdmin):
    list_display = ('customer', 'awb_limit')
    search_fields = ('customer__name', 'awb_limit')

admin.site.register(Shipper)
admin.site.register(Customer)
admin.site.register(FuelSurcharge)
admin.site.register(FuelSurchargeZone)
admin.site.register(CashOnDelivery, CashOnDeliveryAdmin)
admin.site.register(CashOnDeliveryZone, CashOnDeliveryZoneAdmin)
admin.site.register(FreightSlab, FreightSlabAdmin)
admin.site.register(FreightSlabCity, FreightSlabCityAdmin)
admin.site.register(FreightSlabOriginZone, FreightSlabOriginZoneAdmin)
admin.site.register(FreightSlabDestZone, FreightSlabDestZoneAdmin)
admin.site.register(FreightSlabZone, FreightSlabZoneAdmin)
admin.site.register(BrandedFleetCustomer)
admin.site.register(BrandedFullTimeEmployeeCustomer)
admin.site.register(VolumetricWeightDivisor, VolumetricWeightDivisorAdmin)
admin.site.register(MinActualWeight, MinActualWeightAdmin)
admin.site.register(SDLSlab, SDLSlabAdmin)
admin.site.register(SDLSlabCustomer, SDLSlabCustomerAdmin)
admin.site.register(SDDZone)
admin.site.register(SDDSlabZone)
admin.site.register(CustomerAPI, CustomerAPIAdmin)
admin.site.register(RTSFreightZone)
admin.site.register(RTSFuelZone)
admin.site.register(RTSFreight)
admin.site.register(RTSFuel)
admin.site.register(RTSFreightSlab)
admin.site.register(RTSFreightSlabZone)
admin.site.register(ReverseFreightSlab)
admin.site.register(ReverseFreightSlabZone)
admin.site.register(CODFreightSlab, CODFreightSlabAdmin)
admin.site.register(CODFreightSlabZone, CODFreightSlabZoneAdmin)
admin.site.register(CustomerAWBUsedLimit, CustomerAWBUsedLimitAdmin)
