# coding:utf-8

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import auth
from django.http import HttpResponseRedirect,HttpResponse,Http404
#导入用户数据模型
from django.contrib.auth.models import User
from django.contrib.auth.views import password_reset
from django.utils import simplejson
from PIL import Image


from accounts.forms import RegistrationForm,LoginForm,SettingForm
from accounts.models import History_Login,Users,Area
from accounts.safecode import picChecker,encryption,dencryption
from django.conf import settings

def register(request):
    """
    用户注册
    """
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password2'],
                email=form.cleaned_data['email'],
                )
            user.save()
            #保存用户城市数据
            users = Users(
                user=user,
                city=form.cleaned_data['citycode'],
                )
            users.save()
            
            #注册成功  
            return  render_to_response('warn.html',{'warning':'注册成功！',}, context_instance=RequestContext(request)) 
        
    else:
        form = RegistrationForm()

    return render_to_response('account/register.html',{'form':form,},
                    context_instance=RequestContext(request))

def city(request,citycode):
    """
    
    """
    citys = Area.objects.filter(citycode=citycode)
    #木有城市
    if citys.count() == 0:
        return HttpResponse('0')
    #return json
    li = [{"code": "0", "name": "请选择"}]
    for a in citys:
        city = {}
        city["code"] = a.code
        city["name"] = a.name
        li.append(city)
    json = simplejson.dumps(li)  
    return HttpResponse(json)

def login(request):
    """
    登录
    """
    #登录成功，返回页面
    if 'next' in request.GET:
        next = request.GET['next']
    else:
        next = '/'
    if request.method=='POST':
        form = LoginForm(request.POST)
        #数据合法
        if form.is_valid():
            u = User.objects.get(email = request.POST['email'])
            user = auth.authenticate(username=u.username,password=request.POST['password'])
            auth.login(request,user)
            #用户登录记录
            history_login = History_Login(
                user = u,
                #logout_time =  
                user_ip = request.META['REMOTE_ADDR'],
                )
            history_login.save()
            #检查是否记住登录
            if 'remember' not in request.POST.keys():
                request.session.set_expiry(0)
            
            if request.POST['next']:
                next = request.POST['next']
                
            return HttpResponseRedirect(next,)
    else:
        form = LoginForm()
        #用于跳转，返回登录前页面
        if 'HTTP_REFERER' in request.META:
            next = request.META['HTTP_REFERER']
            

    return render_to_response('account/login.html',{'form':form,'next':next,},
                        context_instance=RequestContext(request))
@login_required
def logout(request):
    """
    退出
    """
    #用户退出记录
    history_login = History_Login.objects.filter(user=request.user).order_by('-id')[0]
    history_login.save()

    auth.logout(request)
    return HttpResponseRedirect('/',)

@login_required
def useraccounts(request):
    """
    用户信息设置
    """
    userinfo = Users.objects.get(user=request.user)
    if request.method == 'POST':
        form = SettingForm(request.POST)
        if form.is_valid():

            if form.cleaned_data['citycode'] != '':
                userinfo.city = form.cleaned_data['citycode']
            userinfo.realname = form.cleaned_data['realname']
            userinfo.degree = form.cleaned_data['degree']
            userinfo.profession = form.cleaned_data['profession']
            userinfo.id_cardnum = form.cleaned_data['id_cardnum']
            userinfo.phone = form.cleaned_data['phone']

            if 'photo' in request.FILES:
                image = request.FILES["photo"]
                img119= Image.open(image)
                img119.thumbnail((119,119),Image.ANTIALIAS)
                url='/photos/119_'+ str(request.user.id)+ ".jpg"
                name= settings.MEDIA_ROOT+url
                img119.save(name,"jpeg")
                userinfo.photo = url
            if 'id_cardpic' in request.FILES:
                image = request.FILES["id_cardpic"]
                img= Image.open(image)
                url='/idcardpics/'+ str(request.user.id)+ ".jpg"
                name= settings.MEDIA_ROOT+url
                img.save(name,"jpeg")
                userinfo.id_cardpic = url
            userinfo.save()
            return  render_to_response('warn.html',{'warning':'修改资料成功！',}, context_instance=RequestContext(request)) 
        
    else:
        #显示用户信息
        
        form = SettingForm(initial={'realname':userinfo.realname,'phone':userinfo.phone,
                                    'degree':userinfo.degree,'profession':userinfo.profession,
                                    'id_cardnum':userinfo.id_cardnum,'citycode': userinfo.city.name,
                                    })

    return render_to_response('account/useraccounts.html',{'form':form,'photo':userinfo.photo,'id_cardpic':userinfo.id_cardpic,},
                    context_instance=RequestContext(request))
    

#获取验证码字符串
def getverificationcode(request):
    a = picChecker()
    #s = a.getPicString().upper()
    s = a.getPicString()
    d = encryption(s=s)
    
    return HttpResponse(d)
  
#获取验证码图片
def getverificationpic(request,pid):
    a = picChecker()
    #jiemi
    e = dencryption(s=pid)
    if e == False:
        raise Http404
    b = a.createChecker(s=e)

    return HttpResponse(b[1],'image/gif')
    #return HttpResponse(b[0])
     


####################qq新浪登录##################################
from websiteaccess import APIClient


def weblogin(request,logintype):
    """
    网站接入登录
    跳转到授权页面
    """
    if logintype in ['qq','weibo']:
        client = APIClient(logintype=logintype)
        url = client.get_authorize_url()
        return HttpResponseRedirect(url)
    else:
        raise Http404()

def webcallback(request,logintype):
    """
    回调函数，获取access_token
    创建user,保存uid。查找用户，登录。
    userid:接入网站登录的唯一标识  新浪：uid  腾讯：openid
    """
    if logintype in ['qq','weibo']:
        if 'code' in request.GET:
            code = request.GET['code']
        client = APIClient(logintype=logintype)
        r = client.request_access_token(code)
        access_token = r.access_token
        expires_in = r.expires_in
        if logintype == 'qq':
            userid = client.request_qq_uid(access_token)    
        else:
            userid = r.uid
        # TODO: 在此可保存access token
        client.set_access_token(access_token, expires_in, userid)
        
        return HttpResponse(access_token+'   '+str(expires_in)+'   '+userid)
        return HttpResponseRedirect(url)
    else:
        raise Http404()


