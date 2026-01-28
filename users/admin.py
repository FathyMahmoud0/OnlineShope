from django.contrib import admin
from .models import CustomUser,Address

class UserAdmin(admin.ModelAdmin):
    list_display = ['id','first_name' , 'last_name' , 'username', 'email']
    list_display_links =  ['id','first_name' , 'last_name' ,'email']
    
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user','country' , 'city' , 'street', 'phone']
    list_display_links = ['user','country' , 'city' , 'street', 'phone']



admin.site.register(CustomUser,UserAdmin)
admin.site.register(Address,AddressAdmin)