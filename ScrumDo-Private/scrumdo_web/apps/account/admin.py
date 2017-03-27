from django.contrib import admin
from apps.account.models import (
        Account,
        OtherServiceInfo,
        PasswordReset,
        RegistrationKey
    )

def approve_account(modeladmin, request, queryset):
    queryset.update(approved=True)
    
def disable_account(modeladmin, request, queryset):
    queryset.update(approved=False)
    


admin.site.register(OtherServiceInfo)

class AccountAdmin(admin.ModelAdmin):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    list_display = ('approved','user','email')
    list_filter = ('approved',)
    actions = (approve_account,disable_account)
    def has_add_permission(self, request):
            return False
    

class PasswordResetAdmin(admin.ModelAdmin):
    list_display = ('user', 'temp_key', 'timestamp', 'reset')

class RegistrationKeyAdmin(admin.ModelAdmin):
    list_display = ('email', 'key', 'created')

admin.site.register(PasswordReset, PasswordResetAdmin)
admin.site.register(Account,AccountAdmin)
admin.site.register(RegistrationKey, RegistrationKeyAdmin)
admin.site.disable_action('delete_selected')