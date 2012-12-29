# coding:utf-8
from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'mysite.views.home', name='home'),
    #导入数据
    url(r'^sport/$', 'activity.views.home'),
    #account
    url(r'^accounts/',include('accounts.urls')),
)
