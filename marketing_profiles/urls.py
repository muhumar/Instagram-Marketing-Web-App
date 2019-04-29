


from django.contrib import admin
from django.conf.urls import url, include
from . import views
from .views import send_complaints_to_admin,marketing_profile_detail_view,MarketingProfileDetailView,add_account,view_subscription,marketing_profile_password_change

urlpatterns = [
    url('^$', marketing_profile_detail_view, name='marketing_profile'),
    url('^account/', add_account, name='add_account'),
    url('^subscription/$', view_subscription, name='view_subscription'),
    url('^change_password/$', marketing_profile_password_change, name='marketing_pass_change'),
    url('^account-paypal/$', views.paypalform, name='account-paypal'),
    url('^account-done/$', views.payment_done, name='account-paypal-done'),
    url('^account-cancel/$', views.payment_cancel, name='account-paypal-cancel'),
    url('^support/$', send_complaints_to_admin, name='send-complaints'),
    url('^detail/(?P<pk>\d+)/', MarketingProfileDetailView, name='detail'),

]