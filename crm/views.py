from django.shortcuts import render,redirect, get_object_or_404, HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from .models import Profile
from django.dispatch import receiver
import time
from django.contrib import messages
from django.contrib.auth import logout
from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.contrib.auth.models import User
from django.views.generic import View
from .models import Email_Activation
from django.urls import reverse
from django.utils.safestring import mark_safe
from marketing_profiles.models import Marketing_Profile
from marketing_profiles.utils import unique_invoice_id_generator
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
from AddOns.models import Add_On_Instance
from datetime import date,timedelta
from django.template.loader import get_template

from django.core.mail import send_mail,EmailMessage
from django.conf import settings


def Email_sending(subject,message,sender_email,to_email):
    send_mail(subject,
              message,
              sender_email,
              to_email,
              fail_silently=False)

User = get_user_model()
def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')


@login_required
def view_profile(request):
    context={}
    if request.method == 'GET':
        # if request.session['email']:
        #     email = request.session['email']
        #     print(email)
        #     profile_obj = get_object_or_404(Profile, email=email)
        # else:
        profile_obj = get_object_or_404(Profile, email=request.user.email)
        context = {'profile_obj':profile_obj}
        return render(request, 'crm/view_profile.html', context)

    if request.method == "POST":
        password = request.POST.get('password')
        email = request.POST.get('email')
        profile_obj = Profile.objects.get(email=email)
        user = User.objects.get(email=email)
        profile_obj.password = password
        profile_obj.save()
        user.set_password(str(password))
        user.save()
        login(request,user)
        request.session['email'] = email
        messages.success(request,"Password Successfully Updated.")
        return redirect('crm:view_profile')
    return render(request,'crm/view_profile.html',context)


def sign_up(request):
    key = unique_invoice_id_generator(Marketing_Profile, Add_On_Instance)
    name = request.POST.get('name')
    email = request.POST.get('email')
    password = request.POST.get('password')
    confirm_password = request.POST.get('confirm_password')
    hear_about_us = request.POST.get('hear_about_us')
    reg_date = date.today()
    expiry_date = date.today() + timedelta(days=14)
    if request.method == 'POST':
        username = name +" " +str(key)
        qs = User.objects.filter(email=email)
        print(qs.first())
        if qs.exists():
            messages.error(request, "Email {email} Already Exists.".format(email=email))
            return redirect('crm:signup')
        elif password != confirm_password:
            messages.error(request, "Passwords Don't match.")
            return redirect('crm:signup')
        else:
            if password != confirm_password:
                messages.error(request, "Passwords Don't match.")
                return redirect('crm:signup')
            new_user = User(username=username, email=email)
            new_user.set_password(str(password))
            new_user.save()
            profile_obj = Profile(username=username, name=name , email=email, active=True,password=password,expiry_date=expiry_date, registration_date=reg_date, user=new_user,hear_about_us=hear_about_us)
            profile_obj.save()
            messages.success(request, "Please Login to Proceed.")
            return redirect('login')
    return render(request, 'signup.html', {})


def login_page(request):
    if request.user.is_authenticated:
        return redirect('marketing:marketing_profile')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            username = User.objects.get(email=email.lower()).username
            user = authenticate(request, username=username, password=password)
            if user is not None:
                profile_object = get_object_or_404(Profile, email=email)
                if profile_object is None:
                    messages.error(request, "Invalid Credentials")
                    return redirect('login')
                if user is not None:
                    if not profile_object.active:
                        messages.error(request, "Please click on the sent email to activate your profile.")
                        return redirect('login')
                    request.session.set_expiry(1500)
                    login(request, user)
                    marketing_profile = Marketing_Profile.objects.check_trial_versions(request.user)
                    request.session['email']=email
                    profile_obj = Profile.objects.get(user=request.user)
                    if profile_obj.first_time:
                        profile_obj.first_time = False
                        profile_obj.save()
                        return redirect('marketing:add_account')
                    else:
                        return redirect('marketing:marketing_profile')
        except:
            messages.error(request,'You need to sign up to get registered.')
            return redirect('crm:signup')
        else:
            messages.error(request, "No users exists with these Credentials.")
            return redirect('login')
    return render(request, 'login.html', {})


class AccountEmailActivateView(View):
    def get(self,request, key, *args, **kwargs):
        qs = Email_Activation.objects.filter(key__iexact=key).confirmable()
        if qs.count() == 1:
            obj = qs.first()
            obj.activate()
            messages.success(request,'You email has been confirmed. Please login.')
            return redirect('login')
        else:
            qs = Email_Activation.objects.filter(key__iexact=key,activated=True)
            reset_link = reverse('crm:signup')
            if qs.exists():
                msg = """Your email has already been activated. Do you want to <a href="{link}">reset you password?</a>""".format(link=reset_link)
                messages.success(request,mark_safe(msg))
                return redirect('login')
        return render(request, 'registration/activation-error.html',{})

@login_required
def paypalform(request):
    invoice_id = unique_invoice_id_generator(Marketing_Profile, Add_On_Instance)
    paypal_dict = {

        "cmd": "_xclick-subscriptions",
        "business": 'billut123-facilitator@gmail.com',
        "a1": "9.90",
        "p1": "14",
        "t1": "D",
        "a3": "49.99",  # monthly price
        "p3": 1,  # duration of each unit (depends on unit)
        "t3": "M",  # duration unit ("M for Month")
        "src": "1",  # make payments recur
        "sra": "1",  # reattempt payment on payment error
        "no_note": "1",  # remove extra notes (optional)
        'invoice':invoice_id,
         "item_name": request.session['account_username'],
         "notify_url": request.build_absolute_uri(reverse('crm:paypal')),
        "return": request.build_absolute_uri(reverse('crm:paypal-account-done')),
        "cancel_return": request.build_absolute_uri(reverse('marketing:marketing_profile')),
    }

    request.session['invoice_id'] = invoice_id
    # Create the instance.
    form = PayPalPaymentsForm(initial=paypal_dict,button_type='subscribe')
    context = {"form": form,'details':'9.9$ for 14 days','details2':'then 49.99$/month'}
    return render(request, "crm/paypalform.html", context)


@csrf_exempt
def payment_done(request):
    if request.method == 'GET':
        username = request.session['account_username']
        password = request.session['account_password']
        audience = request.session['targeting_audience']
        invoice_id = request.session['invoice_id']
        # date = time.strftime("%Y-%m-%d")
        reg_date = date.today()
        expiry_date = date.today() + timedelta(days=14)
        marketing_profile = Marketing_Profile(user=request.user,email=request.user.email ,profile_username=username, profile_password=password,targeting_audience=audience,total=49.99,registration_date=reg_date, expiry_date=expiry_date,invoice_id = invoice_id)
        marketing_profile.save()
        del request.session['account_username']
        del request.session['account_password']
        del request.session['targeting_audience']
        del request.session['invoice_id']
        # Email_sending('Payment', 'This is the message', settings.EMAIL_HOST_USER, [request.user.email])
        messages.success(request, "Payment successful. Profile Added.")

        return redirect('marketing:marketing_profile')
    return redirect('marketing:marketing_profile')


# def payment_done(sender, **kwargs):
#     ipn_obj = sender
#     print(ipn_obj.GET)
#     print(ipn_obj.POST)
#     payStatus = ipn_obj.GET.get('payment_status', '')
#     print("paystatus",payStatus)
#     # if ipn_obj.txn_type == 'web_accept':
#     #     # if ipn_obj.payment_status == ST_PP_COMPLETED:
#     #     #     print("yesssss")
#     # payStatus = ipn_obj.POST.get('payment_status', '')
#     # print("paystatus",payStatus)
#     # if ipn_obj.payment_status == ST_PP_COMPLETED:
#         # username = ipn_obj.session['account_username']
#         # password = ipn_obj.session['account_password']
#         # audience = ipn_obj.session['targeting_audience']
#         # print(username,password,audience,"audience")
#         # reg_date = date.today()
#         # expiry_date = date.today() + timedelta(days=14)
#         # invoice_id = unique_invoice_id_generator(Marketing_Profile, Add_On_Instance)
#         # marketing_profile = Marketing_Profile(user=ipn_obj.user, profile_username=username, profile_password=password,targeting_audience=audience,total=49.99,registration_date=reg_date, expiry_date=expiry_date,invoice_id = invoice_id)
#         # marketing_profile.save()
#     print("profile Saved.")
#         # del sender.session['account_username']
#         # del sender.session['account_password']
#         # del sender.session['targeting_audience']
#     # email = EmailMessage('Payment',
#     #                          'This is the message',
#     #                          settings.EMAIL_HOST_USER,
#     #                          [ipn_obj.user.email])
#     #     email.send()
#         # Email_sending('Payment', 'This is the message', settings.EMAIL_HOST_USER, [ipn_obj.user.email])
#         # messages.success(sender, "Payment successful. Profile Added.")
#         # return redirect('marketing:marketing_profile')
#     # else:
#     #     print("nothing")
#     return redirect('marketing:marketing_profile')
#
# valid_ipn_received.connect(payment_done)

@csrf_exempt
def payment_cancel(request):
    return render(request,'crm/payment_cancel.html',context=None)