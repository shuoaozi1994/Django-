import jwt

#django提供一个特殊的装饰器，@method_decorator(logging_check)
# function dec 函数式装饰器
# method dec  方法装饰器
#method_decorator 将自定义的 function dec 转换成 method dec
from django.http import JsonResponse
from django.conf import settings
from user.models import UserProfile

def logging_check(func):
    def wrap(request, *args, **kwargs):

        token = request.META.get('HTTP_AUTHORIZATION')
        if not token:
            result = {'code':403,  'error':'Please login'}
            return JsonResponse(result)

        try:
            res = jwt.decode(token, settings.JWT_TOKEN_KEY)
        except Exception as e:
            print('jwt decode error is %s'%(e))
            result = {'code':403, 'error': 'Please login'}
            return JsonResponse(result)

        username = res['username']
        user = UserProfile.objects.get(username=username)
        request.myuser = user

        return func(request, *args, **kwargs)
    return wrap


def get_user_by_request(request):
    #返回访问者的 用户名
    token = request.META.get('HTTP_AUTHORIZATION')
    if not token:
        return None
    try:
        res = jwt.decode(token, settings.JWT_TOKEN_KEY)
    except Exception as e:
        print('jwt decode error is %s'%(e))
        return None

    username = res['username']
    return username



