from .logging_dec import get_user_by_request
from django.core.cache import cache

def cache_set(expire):
    def _cache_set(func):
        def wrapper(request, *args, **kwargs):
            #访问者 - xxx
            visitor = get_user_by_request(request)
            #被访问者
            author_username = kwargs['author_id']
            # 带查询字符串的url
            full_url = request.get_full_path()
            #判断 访问者和博主之间的关系，根据关系生成不同的cache key
            if visitor == author_username:
                #博主访问自己 'topics_cache_self_%s'%(带查询字符串的url)
                cache_key = 'topics_cache_self_%s'%(full_url)
            else:
                # 非博主访问 'topics_cache_%s'%(带查询字符串的url)
                cache_key = 'topics_cache_%s'%(full_url)
            #cache判断缓存有没有
            res = cache.get(cache_key)
            if res:
                print('---cache in cache key is %s'%(cache_key))
                # 有缓存 直接返回
                return res
            # 没有 走视图 - 存储缓存
            res = func(request, *args, **kwargs)
            cache.set(cache_key, res, expire)
            return res
        return wrapper
    return _cache_set