"""Insta URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url,include
from . import views
from marketing_profiles.views import marketing_profile_detail_view
from django.contrib.auth import views as auth_views

app_name='crm'

urlpatterns = [
    url('^signup/$', views.sign_up, name='signup'),
    # url('^logout/$', views.logout_view, name='logout'),
    url(r'^logout/$', views.logout_page, name='logout'),
    url('^profile/$', views.view_profile, name='view_profile'),
    url('^paypal/$', views.paypalform, name='paypal'),
    url('^paypal-done/$', views.payment_done, name='paypal-account-done'),
    url('^paypal-cancel/$', views.payment_cancel, name='paypal-cancel'),
    url('^email/confirm/(?P<key>[0-9A-Za-z]+)/$', views.AccountEmailActivateView.as_view(), name='email_confirmation')


]
