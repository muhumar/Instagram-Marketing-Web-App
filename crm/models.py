from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import get_template
from django.conf import settings
from django.db.models.signals import pre_save,post_save
from Insta.utils import random_string_generator,unique_key_generator
from django.core.urlresolvers import reverse


class Profile(models.Model):
    username    = models.CharField(max_length=200)
    name        = models.CharField(max_length=120,default=" ",null=True,blank=True)
    email       = models.EmailField(unique=True)
    password    = models.CharField(max_length=120)
    user        = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', editable=False, null=True)
    registration_date = models.DateField()
    expiry_date = models.DateField()
    first_time  = models.BooleanField(default=True)
    active      = models.BooleanField(default=False)
    total       = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    hear_about_us = models.CharField(max_length=120, blank=True,null=True,default="")

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse(Profile, kwargs={'email': self.email})

class EmailActivationQuerySet(models.query.QuerySet):
    def confirmable(self):
        now = timezone.now()
        start_range = now - timedelta(days=7)

        end_range = now

        return self.filter(
            activated = False,
            forced_expired = False
        ).filter(
            timestamp__gt=start_range,
            timestamp__lte=end_range
        )


class EmailActivationManager(models.Manager):
    def get_queryset(self):
        return EmailActivationQuerySet(self.model, using=self._db)

    def confirmable(self):
        return self.get_queryset().confirmable()


class Email_Activation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    name = models.CharField(max_length=120,default="",null=True,blank=True)
    key = models.CharField(max_length=120)
    activated = models.BooleanField(default=False)
    forced_expired = models.BooleanField(default=False)
    expires = models.IntegerField(default=7)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = EmailActivationManager()

    def __str__(self):
        return self.email

    def can_activate(self):
        qs = Email_Activation.objects.filter(pk=self.pk).confirmable()
        if qs.exists():
            return True
        return False

    def activate(self):
        if self.can_activate():
            user = self.user
            profile_obj=Profile.objects.get(user=user)
            profile_obj.active = True
            profile_obj.save()
            self.activated = True
            self.save()
            return True
        return False


    def regenerate(self):
        self.key = None
        self.save()
        if self.key is not None:
            return True
        return False

    def send_activation_email(self):
        if not self.activated and not self.forced_expired:
            if self.key:
                base_url = getattr(settings,'BASE_URL', 'http://127.0.0.1:8000')
                key_path = reverse('crm:email_confirmation', kwargs={'key':self.key})
                path = '{base}{path}'.format(base=base_url, path=key_path)
                context = {
                    'path': path,
                    'email':self.email,
                    'name': self.name
                }

                key = random_string_generator(size=45)
                txt_ = get_template('emails/verify.txt').render(context)
                html_ = get_template('emails/verify.html').render(context)

                subject = 'Confirm your uptoSocial email.'
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [self.email]
                sent_mail = send_mail(
                    subject=subject,
                    message=txt_,
                    from_email=from_email,
                    recipient_list=recipient_list,
                    html_message=html_,
                    fail_silently=False
                )

                return sent_mail
        return False

def pre_save_email_activation(instance,sender,*args,**kwargs):
    if not instance.activated and not instance.forced_expired:
        if not instance.key:
            instance.key=unique_key_generator(instance)


pre_save.connect(pre_save_email_activation,sender=Email_Activation)

def post_save_user_create_receiver(sender,instance,created,*args,**kwargs):
    if created:
        obj = Email_Activation.objects.create(user=instance.user,email=instance.email,name = instance.name)
        obj.send_activation_email()
        print("Created.")

post_save.connect(post_save_user_create_receiver,sender=Profile)

