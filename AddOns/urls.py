from django.conf.urls import url, include

from .views import manage_add_ons,paypalform,payment_cancel,payment_done

urlpatterns = [
    url('^profile_addon/$', manage_add_ons, name='manage-addon'),
    url('^paypal-addon/$', paypalform, name='paypal-addon'),
    url('^payment-cancel-addon/$', payment_cancel, name='paypal-cancel-addon'),
    url('^payment-done-addon/$', payment_done, name='paypal-done-addon'),
]