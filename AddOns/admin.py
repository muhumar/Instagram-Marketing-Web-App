from django.contrib import admin
from .models import AddOn
from .models import Add_On_Instance

class Add_On_Model_Admin(admin.ModelAdmin):
    list_display = ['email','marketing_profile','add_on','registration_date','expiry_date']
    search_fields = ["email"]
    list_filter = ["email", "registration_date"]

    class Meta:
        model = Add_On_Instance


admin.site.register(AddOn)
admin.site.register(Add_On_Instance,Add_On_Model_Admin)
