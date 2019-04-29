from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from paypal.standard.models import ST_PP_COMPLETED
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from datetime import datetime


@receiver(valid_ipn_received)
def ipn_receiver(sender, **kwargs):
    ipn_obj = sender

    # check for Buy Now IPN
    if ipn_obj.txn_type == 'web_accept':

        if ipn_obj.payment_status == ST_PP_COMPLETED:
            # payment was successful
            print('great!')


    # check for subscription signup IPN
    elif ipn_obj.txn_type == "subscr_signup":
        print("Subscription Signup")

    elif ipn_obj.txn_type == "subscr_payment":
        print("Subscription Signup")


    # check for failed subscription payment IPN
    elif ipn_obj.txn_type == "subscr_failed":
        print("Subscription Failed")

    # check for subscription cancellation IPN
    elif ipn_obj.txn_type == "subscr_cancel":
        print("Subscription Cancel")
