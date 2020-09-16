import json
import hashlib
import random
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from user.models import UserProfile
from btoken.views import make_token
from tools.logging_dec import logging_check
from django.core.cache import cache
from django.conf import settings
from tools.sms import YunTongXin
from .tasks import send_sms_c
#10100-10199


# Create your views here.
#FBV function based view
def user_view(request):

    if request.method == 'GET':
        #获取数据
        pass
    elif request.method == 'POST':
        pass
    elif request.method == 'PUT':
        pass

#CBV class based view
class UserViews(View):
    #若接到未定义方法的 http动作，视图类返回405响应

    def get(self, request, username=None):

        if username:
            #v1/users/<str:username> #获取指定用户数据
            try:
                user = UserProfile.objects.get(username=username)
            except Exception as e:
                print('--get get user error %s'%(e))
                result = {'code':10104, 'error':'user error'}
                return JsonResponse(result)

            if request.GET.keys():
                #按具体字段返回
                data = {}
                for k in request.GET.keys():
                    if k == 'password':
                        continue
                    #TODO 注意avatar
                    if hasattr(user, k):
                        data[k] = getattr(user, k)
                result = {'code':200, 'username':username, 'data':data}
            else:

                result = {'code':200, 'username':username, 'data':{'info':user.info, 'sign':user.sign, 'nickname':user.nickname, 'avatar': str(user.avatar) }}

            return JsonResponse(result)

        else:
            #v1/users 获取所有用户数据
            pass

        return JsonResponse({'code':200})

    def post(self,request):

        json_str = request.body
        json_obj = json.loads(json_str)
        if not json_str:
            result = {'code':10100, 'error':'no date'}
            return JsonResponse(result)
        #{'username': 'guoxiaonao', 'email': 'aaa@qq.com', 'password_1': '123456', 'password_2': '123456'}

        username = json_obj['username']
        email = json_obj['email']
        password_1 = json_obj['password_1']
        password_2 = json_obj['password_2']
        phone = json_obj['phone']
        sms_num = json_obj['sms_num']

        #校验验证码
        code_cache_key = 'sms_%s'%(phone)
        old_code = cache.get(code_cache_key)

        if old_code != int(sms_num):
            return JsonResponse({'code':10111, 'error':"The code is error"})

        #校验用户名是否可用
        old_users = UserProfile.objects.filter(username=username)
        if old_users:
            #当前用户名已注册
            result = {'code':10101, 'error':'The username is already existed'}
            return JsonResponse(result)
        #密码做md5
        if password_1 != password_2:
            result = {'code':10102, 'error':'The password is not same'}
            return JsonResponse(result)

        m = hashlib.md5()
        m.update(password_1.encode())
        #创建用户 - UserProfile插入数据
        try:
            user = UserProfile.objects.create(username=username,nickname=username, password=m.hexdigest(), email=email)
        except Exception as e:
            print('create user error is %s'%(e))
            result = {'code': 10103, 'error': 'The username is already existed'}
            return JsonResponse(result)

        #签发token - 免登陆1天
        token = make_token(username)
        return JsonResponse({'code': 200, 'username':username, 'data':{'token':token.decode()}})

    @method_decorator(logging_check)
    def put(self, request, username=None):

        json_str = request.body
        json_obj = json.loads(json_str)
        sign = json_obj['sign']
        info = json_obj['info']
        nickname = json_obj['nickname']

        user = UserProfile.objects.get(username=username)
        user.sign = sign
        user.info = info
        user.nickname = nickname

        user.save()
        return JsonResponse({'code':200, 'username':username})

@logging_check
def user_avatar(request, username=None):

    if request.method != 'POST':
        result = {'code':10108, 'error':'Please use POST'}
        return JsonResponse(result)
    #获取当前登录用户
    user = request.myuser
    user.avatar = request.FILES['avatar']
    user.save()
    return JsonResponse({'code':200})


def sms_view(request):

    json_str = request.body
    json_obj = json.loads(json_str)
    phone = json_obj.get('phone')

    #检查当前是否有已经发送的随机码
    cache_key = 'sms_%s'%(phone)
    old_code = cache.get(cache_key)
    if old_code:
        result = {'code':10109, 'error':'You have a old code'}
        return JsonResponse(result)
    code = random.randint(1000, 9999)
    #存储发送的验证码
    cache.set(cache_key, code, 60)
    #发送验证码
    #同步
    #res = send_sms(phone, code)
    #celery版本
    send_sms_c.delay(phone, code)
    #TODO 如果是非正常， redis中 code 删除
    return JsonResponse({'code':200})

def send_sms(phone, code):

    config = {
        "accountSid": settings.SMS_ACCOUNT_ID,
        "accountToken": settings.SMS_ACCOUNT_TOKEN,
        "appId": settings.SMS_APP_ID,
        "templateId": settings.SMS_TEMPLATE_ID
    }
    yun = YunTongXin(**config)
    res = yun.run(phone, code)
    return res













