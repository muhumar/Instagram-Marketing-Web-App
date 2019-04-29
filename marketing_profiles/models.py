from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date,timedelta

# from AddOns.models import Add_On_Instance
# Create your models here.

class Marketing_Profiles_Manager(models.Manager):
    def get_profile_list(self, request):
        marketing_profiles = Marketing_Profile.objects.filter(user=request.user)
        return marketing_profiles

    def get_marketing_profile_detail(self,id):
        qs = Marketing_Profile.objects.first(id=id)
        if qs.count() == 1:
            return qs.first()
        return None

    def activate_marketing_profiles(self,checkbox_list,user):
        qs = Marketing_Profile.objects.filter(user=user).values_list('id', flat=True)
        today_date = date.today()
        next_month_date = date.today() + timedelta(days=30)
        qs_list = list(qs)
        checkbox_list = list(map(int, checkbox_list))
        for i in checkbox_list:
            qs_list.remove(i)
        for i in qs_list:
            marketing_profile = Marketing_Profile.objects.get(pk=i, user=user)
            marketing_profile.is_active = True
            marketing_profile.registration_date = today_date
            marketing_profile.expiry_date = next_month_date
            marketing_profile.save()
        return True

    def deactivate_marketing_profile(self, checkbox_list, user):
        checkbox_list = list(map(int, checkbox_list))
        today_date = date.today()
        next_month_date = date.today() + timedelta(days=30)
        for i in checkbox_list:
            marketing_profile = Marketing_Profile.objects.get(pk=i, user=user)
            marketing_profile.is_active = False
            marketing_profile.registration_date = today_date
            marketing_profile.expiry_date = next_month_date
            marketing_profile.save()
            # qs = Add_On_Instance.objects.filter(user = user,marketing_profile=marketing_profile)
            # if qs.exists():
            #     for j in qs:
            #         j.delete()
        return True

    def get_active_profile(self,user):
        active_account_list = []
        marketing_profiles = Marketing_Profile.objects.filter(user = user,is_active=True)
        for primary_key in marketing_profiles:
            active_account_list.append(primary_key.id)
        return active_account_list

    def get_deactive_profile(self,user):
        active_account_list = []
        marketing_profiles = Marketing_Profile.objects.filter(user = user,is_active=False)
        for primary_key in marketing_profiles:
            active_account_list.append(primary_key.id)
        return active_account_list

    def profile_to_be_activated(self,checked_list,active_list,user):
        all_profiles_list = []
        list = active_list + checked_list
        qs = Marketing_Profile.objects.filter(user=user)
        for i in qs:
            all_profiles_list.append(i.id)
        operations_list = [x for x in all_profiles_list if not x in list]
        return operations_list

    def check_trial_versions(self, user):
        today_date = date.today()
        next_month_date = date.today() + timedelta(days=30)

        marketing_profiles = Marketing_Profile.objects.filter(user=user, is_active=True)
        if next_month_date >= today_date:
            print("True is the date yeah.")
        if marketing_profiles.exists():
            for profiles in marketing_profiles:
                if today_date >= profiles.expiry_date:
                    profiles.trial = False
                    profiles.registration_date = today_date
                    profiles.expiry_date = next_month_date
                    profiles.save()
                else:
                    print("nothing.")
        else:
            return True




class Marketing_Profile(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    email = models.EmailField(blank=True, null=True)
    profile_username = models.CharField(max_length=100)
    profile_password = models.CharField(max_length=120)
    trial = models.CharField(max_length=20,default=True)
    total = models.DecimalField(max_digits=3, decimal_places=1)
    registration_date = models.DateField()
    expiry_date = models.DateField()
    targeting_audience = models.CharField(max_length=500)
    is_active = models.BooleanField(default=True)
    invoice_id = models.CharField(max_length=500)


    objects = Marketing_Profiles_Manager()

    def __str__(self):
        return self.profile_username

    def get_absolute_url(self):
        return reverse("marketing:detail", kwargs={'pk': self.pk})