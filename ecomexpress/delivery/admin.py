from delivery.models import DashboardVisiblity 
from django.contrib import admin


class DashboardVisiblityAdmin(admin.ModelAdmin):
    list_display = ('employee',  'state', 'ncr_state')
    #search_fields = ('user__username', 'state__name')


admin.site.register(DashboardVisiblity, DashboardVisiblityAdmin)
