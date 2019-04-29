from django.contrib import admin
from .models import Marketing_Profile

# Register your models here.
class MarketingProfileModelAdmin(admin.ModelAdmin):
    list_display = ['email',"profile_username", 'profile_password','registration_date', 'expiry_date']
    search_fields = ["email"]
    list_filter = ["email", "registration_date"]
    class Meta:
        model = Marketing_Profile

admin.site.register(Marketing_Profile,MarketingProfileModelAdmin)