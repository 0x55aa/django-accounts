#-*- coding:utf-8 -*-

from django import forms
#导入用户数据模型
from django.contrib.auth.models import User
from django.contrib import auth
#导入正则表达式模块
import re
#
from django.core.exceptions import ObjectDoesNotExist

from accounts.safecode import encryption
from accounts.models import Area

class RegistrationForm(forms.Form):
    """
    用户注册类，从Form类继承
    """

    #用户名文本框
    username = forms.CharField(label='用户名',min_length=3,max_length=7)
    #email
    email = forms.EmailField(label='电子邮件')
    #passwd
    password1 = forms.CharField(label='密码',min_length=6,max_length=20,widget=forms.PasswordInput())
    password2 = forms.CharField(label='确认密码',min_length=6,max_length=20,widget=forms.PasswordInput())
    #city
    
    #province = forms.ChoiceField(label='省',choices=provinces,required=False)
    citycode = forms.CharField(widget=forms.HiddenInput(attrs={'value':''}))
    #city = forms.ChoiceField(label='城市',choices=default,required=False)
    #area = forms.ChoiceField(label='区',choices=default,required=False)
    #验证码
    key = forms.CharField(widget=forms.HiddenInput(attrs={'value':''}))
    checkcode = forms.CharField(label='验证码',max_length=5)

    #验证输入用户名的合法性，正则表达式 去除特殊字符，可以是数字字母文字
    def clean_username(self):
        #去除用户输入的用户名
        username = self.cleaned_data['username']
        #正则表达式验证
        if not re.search(u'^[_a-zA-Z0-9\u4e00-\u9fa5]+$',username):
            raise forms.ValidationError('用户名中只能包含字母、数字、下划线和汉字。')
        name_list = ['root',u'官方','admin']
        for name in name_list:
            if name in username:
                raise forms.ValidationError('该用户名已存在，请重新填写！')
        try:
            #判断用户名是否被注册
            User.objects.get(username=username)
        except ObjectDoesNotExist:
            return username
        raise forms.ValidationError('该用户名已存在，请重新填写！') 
                
    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            User.objects.get(email=email)
        except ObjectDoesNotExist:
            return email
        raise forms.ValidationError('该电子邮件已被注册，请重新填写！')

    def clean_password2(self):
        if 'password1' in self.cleaned_data:
            password1 = self.cleaned_data['password1']
            password2 = self.cleaned_data['password2']
            if password1 == password2:
                return password2
            raise forms.ValidationError('两次输入密码不同，请重新输入')
    
    def clean_citycode(self):
        citycode = self.cleaned_data['citycode']
        try:
            area = Area.objects.get(code=citycode)
            return area
        except ObjectDoesNotExist:
            raise forms.ValidationError('城市选择错误！')
    
    #验证码转换
    def clean_checkcode(self):
        if 'email' in self.cleaned_data:
            safecode = self.cleaned_data['checkcode']
            key = self.cleaned_data['key']
            safecode1 = safecode.encode('utf-8')
            if key == encryption(safecode1):
                pass
            else:
                raise forms.ValidationError('验证码输入错误')


class LoginForm(forms.Form):
    """
    用户login类，从Form类继承
    """
    #email
    email = forms.EmailField(label='电子邮件')
    #passwd
    password = forms.CharField(label='密码',min_length=6,max_length=20,widget=forms.PasswordInput())
    #是否记住登录
    remember = forms.BooleanField(label='下次自动登录',required=False)

    
    def clean_email(self):

        email = self.cleaned_data['email']

        try:
            #判断email是否被注册
            User.objects.get(email = self.cleaned_data['email'])
        except ObjectDoesNotExist:
            raise forms.ValidationError('该email不存在或密码错误，请重新填写！')

        return email
    
    def clean_password(self):
        if 'email' in self.cleaned_data:
            email = self.cleaned_data['email']
            password=self.cleaned_data['password']
            
            u = User.objects.get(email = email)
            user = auth.authenticate(username=u.username,password=password)
            if user is not None and user.is_active:
                return password
        
            raise forms.ValidationError('该email不存在或密码错误，请重新填写！')



   
#用户设置类
class SettingForm(forms.Form):

    DEGREE_CHOICES = (

        ('', '请选择'),
        ('博士', '博士'),
        ('硕士', '硕士'),
        ('本科', '本科'),
        ('专科', '专科'),
        ('高中', '高中'),
        ('初中', '初中'),
        ('小学', '小学'),
        ('其它', '其它'),
    )
    PROFESSION_CHOICES = (
        ('', '请选择'),
        ('在校学生', '在校学生'),('销售', '销售'),('个体经营/零售', '个体经营/零售'),('市场/市场拓展/公关', '市场/市场拓展/公关'),('商务/采购/贸易', '商务/采购/贸易'),
        ('酒店/餐饮/旅游/其他服务', '酒店/餐饮/旅游/其他服务'),('客户服务/技术支持', '客户服务/技术支持'),('计算机/互联网/IT', '计算机/互联网/IT'),('通信技术', '通信技术'),('美术/设计/创意', '美术/设计/创意'),
        ('交通/仓储/物流', '交通/仓储/物流'),('工程/机械技工', '工程/机械技工'),('生产/加工/制造', '生产/加工/制造'),('电气/能源/动力', '电气/能源/动力'),('电子/半导体/仪器仪表', '电子/半导体/仪器仪表'),
        ('教育/培训', '教育/培训'),('法律', '法律'),('财务/审计/统计', '财务/审计/统计'),('金融/银行/证券/投资', '金融/银行/证券/投资'),('建筑/房地产/装修/物管', '建筑/房地产/装修/物管'),
        ('美容/保健', '美容/保健'),('政府工作人员', '政府工作人员'),('人力资源', '人力资源'),('经营管理/高级管理', '经营管理/高级管理'),('医疗/卫生', '医疗/卫生'),
        ('军人/警察', '军人/警察'),('能源/矿产/地质勘察', '能源/矿产/地质勘察'),('化工', '化工'),('生物/制药/医疗器械', '生物/制药/医疗器械'),('行政/后勤', '行政/后勤'),
        ('农林牧渔劳动者', '农林牧渔劳动者'),('农村外出务工人员', '农村外出务工人员'),('翻译', '翻译'),('学术/科研', '学术/科研'),('文体/影视/写作/媒体', '文体/影视/写作/媒体'),
        ('其他', '其他'),('退休', '退休'),('待业/无业/失业', '待业/无业/失业'),('自由职业者', '自由职业者'),
    )
    #city
    citycode = forms.CharField(widget=forms.HiddenInput(attrs={'value':''}),required=False)
    realname = forms.CharField(label='真实姓名',min_length=2,max_length=20,required=False)
    phone = forms.CharField(label='电话',min_length=7,max_length=20,required=False)
    degree = forms.ChoiceField(label='学历',required=False,choices=DEGREE_CHOICES)
    profession = forms.ChoiceField(label='职业',required=False,choices=PROFESSION_CHOICES)
    #头像
    photo = forms.ImageField(label='头像',required=False)
    id_cardnum = forms.CharField(label='身份证号',min_length=17,max_length=18,required=False)
    #身份证照片
    id_cardpic = forms.ImageField(label='身份证照片',required=False)

    def clean_citycode(self):
        citycode = self.cleaned_data['citycode']
        if re.search(u'^[0-9]+$',citycode):
            try:
                area = Area.objects.get(code=citycode)
                return area
            except ObjectDoesNotExist:
                raise forms.ValidationError('城市选择错误！')
        else:
            return ''

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not re.search(u'^[0-9]+$',phone):
            raise forms.ValidationError('输入格式不正确，只能包含数字。')
        return phone

    def clean_id_cardnum(self):
        id_cardnum = self.cleaned_data['id_cardnum']
        if not re.search(u'^[0-9]+$',id_cardnum):
            raise forms.ValidationError('输入格式不正确，只能包含数字。')
        return id_cardnum
    
