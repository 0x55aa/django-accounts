#-*- coding:utf-8 -*-
from django.db import models
from django.contrib.auth.models import User



class Area(models.Model):
    """
    地区表
    """
    #地区名
    code = models.CharField(max_length=6,unique=True)
    name = models.CharField(max_length=20)
    citycode = models.CharField(max_length=6)




class Users(models.Model):
    """
    用户信息表
    """
    user = models.ForeignKey(User)
    #城市
    city = models.ForeignKey(Area)
    #真实姓名
    realname = models.CharField(max_length=20,null=True)
    #电话
    phone = models.CharField(max_length=12,null=True)
    #学历
    degree = models.CharField(max_length=20,null=True)
    #职业
    profession = models.CharField(max_length=20,null=True)
    #头像
    photo = models.ImageField(upload_to='photos/' ,blank=True,null=True)
    #身份证号
    id_cardnum = models.CharField(max_length=20,null=True)
    #身份证照片
    id_cardpic = models.ImageField(upload_to='idcardpics/' ,blank=True,null=True)

    #qq sina账号登陆用户标识
    userid = models.CharField(max_length=35,null=True)


class History_Login(models.Model):

    user = models.ForeignKey(User)
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(auto_now=True)
    user_ip = models.IPAddressField()
