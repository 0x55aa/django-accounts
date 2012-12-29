# coding:utf-8
from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    #register
    url(r'^register/$','accounts.views.register'),
    #用于获取注册时的城市
    url(r'^city/(?P<citycode>[0-9]{6})/$','accounts.views.city'),
    #login
    url(r'^login/$','accounts.views.login'),
    #logout
    url(r'^logout/$','accounts.views.logout'),

    #用户设置
    url(r'^setting/$','accounts.views.useraccounts'),
    #passwd reset
    url(r'^resetpassword/$','django.contrib.auth.views.password_reset',{'template_name':'account/resetpassword.html','email_template_name':'account/password_reset_mail.html','post_reset_redirect':'/account/passwordresetdone/',}),
    #密码重置链接发送成功
    url(r'^passwordresetdone/$', 'django.contrib.auth.views.password_reset_done', {'template_name' : 'account/password_reset_done.html'}),
    #密码重置链接
    url(r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', {'template_name' : 'account/password_reset.html','post_reset_redirect': '/account/passwordresetcomplete/' }),
    #密码重置成功
    url(r'^passwordresetcomplete/$', 'django.contrib.auth.views.password_reset_complete', {'template_name' : 'account/password_reset_complete.html'}),

    #passwd change
    url(r'^changepassword/$','django.contrib.auth.views.password_change',{'template_name' : 'account/password_change.html','post_change_redirect':'/account/passwordchangedone/',}),
    #passwd changed密码修改成功
    url(r'^passwordchangedone/$','django.contrib.auth.views.password_change_done',{'template_name' : 'account/password_change_done.html',}),


    #getsafecode
    url(r'^safecode/$','accounts.views.getverificationcode'),
    #getsafepic
    url(r'^safepic/(?P<pid>[0-9]+)/$','accounts.views.getverificationpic'),

    #用户通过qq，新浪账号登录
    url(r'^weblogin/(?P<logintype>[qweibo]+)/$', 'accounts.views.weblogin'),
    url(r'^callback/(?P<logintype>[qweibo]+)/$', 'accounts.views.webcallback'),                       

    
)
