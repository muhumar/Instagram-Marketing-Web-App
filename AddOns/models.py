from django.db import models
from marketing_profiles.models import Marketing_Profile
from django.core.urlresolvers import reverse

class AddOn(models.Model):
    name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=4, decimal_places=2)
    is_active = models.BooleanField(default=True)
    description = models.TextField()
    registration_date = models.DateField()
    expiry_date = models.DateField()
    updation_date = models.DateField()
    content = models.TextField(default="")

    def __str__(self):
        return self.name


class Add_On_Instance(models.Model):
    add_on = models.ForeignKey(AddOn,on_delete=models.CASCADE)
    marketing_profile = models.ForeignKey(Marketing_Profile,on_delete=models.CASCADE,related_name='marketing_addon')
    email = models.EmailField(blank=True,null=True)
    is_active = models.BooleanField(default=True)
    registration_date = models.DateField()
    expiry_date = models.DateField()
    invoice_id = models.CharField(max_length=500,default="")

    def __str__(self):
        return str(self.marketing_profile)