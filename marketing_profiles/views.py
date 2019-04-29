from django.shortcuts import render, redirect
from django.http import JsonResponse,HttpResponse,HttpResponseRedirect
from .models import Marketing_Profile
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.contrib import messages
from AddOns.models import AddOn, Add_On_Instance
from marketing_profiles.utils import unique_invoice_id_generator
from paypal.standard.forms import PayPalPaymentsForm
from datetime import date,timedelta
# from Insta.send_emails import send_random_mails
from django.template.loader import get_template
from crm.models import Profile
import hashlib
from django.core.mail import send_mail,BadHeaderError,EmailMessage
from django.conf import settings

@login_required
def add_account(request):
    context = {}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        targeting = request.POST.get('targeting')
        if username is "" or password is "" or targeting is "":
            messages.success(request, "Field/s Empty.")
            return redirect('marketing:add_account')

        else:
            if username is not "":
                print("username condition.")
                qs = Marketing_Profile.objects.filter(profile_username=username,user=request.user)
                if qs.exists():
                    messages.error(request, "Marketing Profile with this username already associated with your account. However, you can cancel/activate the subscription anytime.")
                    return redirect('marketing:view_subscription')
                qs2 = Marketing_Profile.objects.filter(profile_username=username)
                if qs2.exists():
                    messages.error(request,
                                   "Marketing Profile with this username already associated with some other account. However, you can add any other marketing profile anytime.")
                    return redirect('marketing:add_account')

            request.session['account_username'] = username
            request.session['account_password'] = password
            request.session['targeting_audience'] = targeting
            messages.success(request, "Make sure your Instagram account password is correct. An incorrect password will delay the marketing.")

            return redirect('crm:paypal')
    return render(request, 'marketing_profiles/add_account.html', context)


@login_required
@csrf_exempt
def view_subscription(request):
    context = {}
    if request.is_ajax() or request.method == 'POST':
        deactivate = True
        activate_profiles = True
        deactivate_profiles = True
        checked_account_list = request.POST.getlist('mycheckboxes[]')
        checked_account_list = list(map(int, checked_account_list))
        deactive_profile_list = Marketing_Profile.objects.get_deactive_profile(request.user)
        account_activated_list = list(set(deactive_profile_list) - set(checked_account_list))
        print(account_activated_list)
        if account_activated_list != []:
            request.session['account_activate_username'] = Marketing_Profile.objects.get(id=account_activated_list[0]).profile_username
            print(request.session['account_activate_username'])
        active_account_list = Marketing_Profile.objects.get_active_profile(request.user)
        final_list = list(set(active_account_list).intersection(checked_account_list))
        print("final list",final_list)
        if final_list == []:
            deactivate = False

        if not deactivate:
            profile_activate_id = Marketing_Profile.objects.profile_to_be_activated(checked_account_list, active_account_list, user=request.user)
            request.session['account_id'] = profile_activate_id
            print(checked_account_list)
        if deactivate:
            activate_profiles = Marketing_Profile.objects.activate_marketing_profiles(checked_account_list, request.user)
            deactivate_profiles = Marketing_Profile.objects.deactivate_marketing_profile(checked_account_list, request.user)
            if activate_profiles and deactivate_profiles:
                marketing_profile = Marketing_Profile.objects.get(id=final_list[0])
                profile = Profile.objects.get(user = request.user)
                context = {
                    'name': profile.name,
                    'content': 'Marketing Profile name: {name}'.format(name=marketing_profile.profile_username)
                }
                txt_ = get_template('emails/cancel_subscription.txt').render(context)
                html_ = get_template('emails/cancel_subscription.html').render(context)

                subject = 'Your cancellation request'
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [request.user.email]
                sent_mail = send_mail(
                    subject=subject,
                    message=txt_,
                    from_email=from_email,
                    recipient_list=recipient_list,
                    html_message=html_,
                    fail_silently=False
                )
                body = 'User with email id: {email} has cancelled his subscription for Marketing Profile:{profile}'.format(email=request.user.email,profile=marketing_profile.profile_username)
                msg = EmailMessage('Marketing Profile Subscription Cancellation.',body,settings.EMAIL_HOST_USER,[settings.EMAIL_HOST_USER])
                msg.send()
                return JsonResponse({
                    'value': True,
                    'deactivate': deactivate
                })
        else:
            return JsonResponse({
                'value': False
            })
    else:
        qs = Marketing_Profile.objects.get_profile_list(request)
        print(qs)
        context = {
            'marketing_profiles': qs
        }
    return render(request, 'marketing_profiles/view_subscription.html', context)


@login_required
def marketing_profile_detail_view(request):
    qs = Marketing_Profile.objects.get_profile_list(request)
    qs2 = AddOn.objects.filter(is_active=True)
    profile_obj = Profile.objects.get(user=request.user)

    name = profile_obj.name
    name=name.replace(" ", "")

    email = profile_obj.email
    secret_token = ':V7NrBQqKBy'

    result=email+secret_token
    result = hashlib.md5(result.encode())

    url='https://marketingforinstagram.igblade.com/login?name='+ name +'&email='+email+'&reports=1&token='+ result.hexdigest()
    print(url)
    context = {
        'marketing_profiles': qs,
        'qs2': qs2,
        'growth_dashboard_url':url
    }
    return render(request, 'marketing_profiles/dashboard.html', context)


@login_required
def MarketingProfileDetailView(request, pk):
    instance = Marketing_Profile.objects.filter(pk=pk)
    add_ons = Add_On_Instance.objects.filter(marketing_profile=pk)
    context = {
        'instance': instance,
        'add_ons': add_ons
    }
    return render(request, 'marketing_profiles/details.html', context)


@login_required
def marketing_profile_password_change(request):
    name = request.POST.get('name')
    password = request.POST.get('password')
    marketing_profile = Marketing_Profile.objects.get(profile_username=name, user=request.user)
    if marketing_profile.profile_password != password:
        marketing_profile.profile_password = password
#         send email
        message = "Your client {email} has changed its marketing profile's: {profile_name} password to: {password}".format(email=request.user.email,profile_name=marketing_profile.profile_username,password=marketing_profile.profile_password)
        email = EmailMessage('Password Changed',message,settings.EMAIL_HOST_USER,[settings.EMAIL_HOST_USER])
        email.send()
        marketing_profile.save()
        messages.success(request,"Password of marketing profile has been changed successfully.")
        return redirect('marketing:view_subscription')
    else:
        messages.success(request, "Password of marketing profile has not been changed.")
        return redirect('marketing:marketing_profile')


def paypalform(request):
    invoice_id = unique_invoice_id_generator(Marketing_Profile, Add_On_Instance)
    request.session['invoice_id'] = invoice_id
    paypal_dict = {

        "cmd": "_xclick-subscriptions",
        "business": 'billut123-facilitator@gmail.com',
        "a3": "49.99",  # monthly price
        "p3": 1,  # duration of each unit (depends on unit)
        "t3": "M",  # duration unit ("M for Month")
        "src": "1",  # make payments recur
        "sra": "1",  # reattempt payment on payment error
        "no_note": "1",# remove extra notes (optional)
        'invoice':invoice_id,
        "item_name": request.session['account_activate_username'],
        "notify_url": request.build_absolute_uri(reverse('marketing:account-paypal')),
        "return": request.build_absolute_uri(reverse('marketing:account-paypal-done')),
        "cancel_return": request.build_absolute_uri(reverse('marketing:marketing_profile')),
    }

    # Create the instance.
    form = PayPalPaymentsForm(initial=paypal_dict, button_type='subscribe')
    context = {"form": form,'details2':'49.99$/month'}
    return render(request, "crm/paypalform.html", context)


@csrf_exempt
def payment_done(request):
    account_id = request.session['account_id']

    invoice_id = request.session['invoice_id']
    account_id = account_id[0]
    marketing_profile = Marketing_Profile.objects.get(id=account_id,user=request.user)
    reg_date = date.today()
    expiry_date = date.today() + timedelta(days=30)
    if marketing_profile:
        marketing_profile.is_active = True
        marketing_profile.registration_date = reg_date
        marketing_profile.expiry_date = expiry_date
        marketing_profile.invoice_id = invoice_id
        marketing_profile.trial = False
        marketing_profile.save()
        del request.session['account_id']
        del request.session['invoice_id']
        messages.success(request, 'Payment has been successful.')
        return redirect('marketing:marketing_profile')
    else:
        print("no way bro.")
    return redirect('marketing:view_subscription')


@csrf_exempt
def payment_cancel(request):
    return render(request, 'crm/payment_cancel.html', context=None)

def send_complaints_to_admin(request):
    subject = request.POST.get('subject', '')
    message = request.POST.get('message', '')
    from_email = request.user.email
    message += "  "
    message += from_email
    if subject and message and from_email:
        try:
            send_mail(subject, message, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER])
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        return HttpResponseRedirect('/')
    else:
        return HttpResponse('Make sure all fields are entered and valid.')