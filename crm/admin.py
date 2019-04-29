from django.contrib import admin

from .models import Profile,Email_Activation

# Register your models here.
class ProfileModelAdmin(admin.ModelAdmin):
    list_display = ["username", "email",'password','registration_date']

    class Meta:
        model = Profile


admin.site.register(Profile,ProfileModelAdmin)


class EmailActivationAdmin(admin.ModelAdmin):
    search_fields = ['email']
    class Meta:
        model = Email_Activation


admin.site.register(Email_Activation,EmailActivationAdmin)

