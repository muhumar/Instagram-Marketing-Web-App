from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from .models import AddOn,Add_On_Instance
from django.urls import reverse
import time
from marketing_profiles.models import Marketing_Profile
from marketing_profiles.utils import unique_invoice_id_generator
from paypal.standard.forms import PayPalPaymentsForm
from django.http import JsonResponse
from datetime import date,timedelta
# from Insta.send_emails import send_random_mails
from django.core.mail import send_mail,EmailMessage
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from crm.models import Profile


@csrf_exempt
@login_required
def manage_add_ons(request):
    context = {}
    if request.is_ajax() and request.method == 'POST':
        id = request.POST.getlist('add_on_id[]')
        del_addon = Add_On_Instance.objects.get(id=id[0])
        profile = Profile.objects.get(user = request.user)
        context = {
            'name':profile.name,
            'content': 'Marketing Profile : {name} add on: {addon}'.format(addon=del_addon.add_on.name,name=del_addon.marketing_profile.profile_username)
        }
        del_addon.delete()
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
        body = 'User with email id: {email} has cancelled the subscription of add on: {addon} for marketing profile:{profile}'.format(email=request.user.email,addon=del_addon.add_on.name,profile=del_addon.marketing_profile.profile_username)
        msg = EmailMessage('Add On Cancellation',body,settings.EMAIL_HOST_USER,[settings.EMAIL_HOST_USER])
        msg.send()

        return JsonResponse({
            'data':True
        })
    return render(request, 'marketing_profiles/dashboard.html', context)


def paypalform(request):
    id = request.POST.get('id')
    marketing_profile_id = request.POST.get('checkboxes[]')
    request.session['add_on_id'] = id
    request.session['marketing_profile_id'] = marketing_profile_id
    if marketing_profile_id == None:
        return redirect('marketing:marketing_profile')
    add_on_already_added = Add_On_Instance.objects.filter(add_on=id, marketing_profile=marketing_profile_id)
    if add_on_already_added.exists():
        messages.error(request,'Add on already added for this profiles.')
        return redirect('marketing:marketing_profile')
    invoice_id = unique_invoice_id_generator(Marketing_Profile, Add_On_Instance)
    request.session['invoice_id'] = invoice_id
    reg_date = date.today()
    expiry_date = date.today() + timedelta(days=30)
    print(reg_date,expiry_date)

    marketing_profile= Marketing_Profile.objects.get(id=marketing_profile_id)
    if marketing_profile:

        add_on = AddOn.objects.get(id=id)

        paypal_dict = {

            "cmd": "_xclick-subscriptions",
            "business": 'billut123-facilitator@gmail.com',
            "a3": add_on.price,  # monthly price
            "p3": 1,  # duration of each unit (depends on unit)
            "t3": "M",  # duration unit ("M for Month")
            "src": "1",  # make payments recur
            "sra": "1",  # reattempt payment on payment error
            "no_note": "1",  # remove extra notes (optional)
            'invoice':invoice_id,
            "item_name": marketing_profile.profile_username + '-' + add_on.name,
            "notify_url": request.build_absolute_uri(reverse('add-on:paypal-addon')),
            "return": request.build_absolute_uri(reverse('add-on:paypal-done-addon')),
            "cancel_return": request.build_absolute_uri(reverse('marketing:marketing_profile')),
        }

        # Create the instance.
        form = PayPalPaymentsForm(initial=paypal_dict, button_type='subscribe')
        context = {"form": form,'details':'{}$/month'.format(add_on.price)}
        return render(request, "crm/paypalform.html", context)
    else:
        messages.error(request,'No Marketing Profile Available.')
        return redirect('marketing:marketing_profile')


@csrf_exempt
def payment_done(request):
    addon_id = request.session['add_on_id']
    print("add on",addon_id)
    marketing_profile_id = request.session['marketing_profile_id']
    invoice_id = request.session['invoice_id']
    reg_date = date.today()
    expiry_date = date.today() + timedelta(days=30)
    add_on_instance = Add_On_Instance(add_on=AddOn(addon_id), marketing_profile=Marketing_Profile(marketing_profile_id),email = request.user.email ,registration_date=reg_date, expiry_date=expiry_date, invoice_id=invoice_id)
    add_on_instance.save()
    del request.session['add_on_id']
    del request.session['marketing_profile_id']
    del request.session['invoice_id']
    return redirect('marketing:marketing_profile')


@csrf_exempt
def payment_cancel(request):
    return render(request,'crm/payment_cancel.html',context=None)

