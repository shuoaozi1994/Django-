import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator


from tools.logging_dec import logging_check, get_user_by_request
from tools.cache_dec import cache_set
from user.models import UserProfile
from topic.models import Topic
from message.models import Message
from django.core.cache import cache
import html
#10300-10399

# Create your views here.
class TopicView(View):

    def clear_topics_caches(self, request):
        #删除 文章列表缓存
        # v1/topics/gxn
        # v1/topics/gxn?category=tec
        # v1/topics/gxn?category=no-tec
        all_path = request.path_info
        all_key_p = ['topics_cache_self_', 'topics_cache_']
        all_keys = []
        for key_p in all_key_p:
            for key_h in ['', '?category=tec', '?category=no-tec']:
                all_keys.append(key_p + all_path + key_h)
        print(all_keys)
        #删除缓存
        cache.delete_many(all_keys)


    def make_topic_res(self, author, author_topic, is_self):

        if is_self:
            #博主访问自己
            # select * from topic_topic where id > author_topic.id and author_id=author.username order by id ASC limit 1
            next_topic = Topic.objects.filter(id__gt=author_topic.id,author=author).first()
            # select * from topic_topic where id < author_topic.id and author_id=author.username order by id DESC limit 1
            last_topic = Topic.objects.filter(id__lt=author_topic.id,author=author).last()

        else:
            next_topic = Topic.objects.filter(id__gt=author_topic.id, author=author, limit='public').first()
            last_topic = Topic.objects.filter(id__lt=author_topic.id, author=author, limit='public').last()

        #留言回复相关
        all_messages = Message.objects.filter(topic=author_topic).order_by('-created_time')
        m_count = 0
        msg_list = []
        reply_dict = {}
        for msg in all_messages:
            if msg.parent_message:
                #回复
                reply_dict.setdefault(msg.parent_message, [])
                reply_dict[msg.parent_message].append({'msg_id':msg.id, 'publisher':msg.publisher.nickname,'publisher_avatar':str(msg.publisher.avatar), 'content':msg.content,'created_time':msg.created_time.strftime('%Y-%m-%d %H:%M:%S')})
            else:
                #留言
                m_count += 1
                msg_list.append({'id':msg.id, 'content':msg.content,'publisher':msg.publisher.nickname, 'publisher_avatar':str(msg.publisher.avatar),'created_time':msg.created_time.strftime('%Y-%m-%d %H:%M:%S'), 'reply':[]})
        #关联 留言和回复
        for m in msg_list:
            if m['id'] in reply_dict:
                m['reply'] = reply_dict[m['id']]

        result = {'code':200, 'data':{}}
        result['data']['nickname'] = author.nickname
        result['data']['title'] = author_topic.title
        result['data']['category'] = author_topic.category
        result['data']['created_time'] = author_topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
        result['data']['content'] = author_topic.content
        result['data']['introduce'] = author_topic.introduce
        result['data']['author'] = author.nickname
        result['data']['next_id'] = next_topic.id if next_topic else None
        result['data']['next_title'] = next_topic.title if next_topic else None
        result['data']['last_id'] = last_topic.id if last_topic else None
        result['data']['last_title'] = last_topic.title if last_topic else None
        #TODO 留言相关为假数据
        result['data']['messages'] = msg_list
        result['data']['messages_count'] = m_count
        return result


    def make_topics_res(self, author, author_topics):

        res = {'code':200, 'data':{}}
        topics_res = []
        for topic in author_topics:
            d = {}
            d['id'] = topic.id
            d['title'] = topic.title
            d['category'] = topic.category
            d['introduce'] = topic.introduce
            d['created_time'] = topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
            d['author'] = author.nickname
            topics_res.append(d)
        res['data']['topics'] = topics_res
        res['data']['nickname'] = author.nickname
        return res

    #@method_decorator(cache_set(600))
    def get(self,request, author_id):
        print('---topic get in view---')
        #/v1/topics/guoxiaonao
        #获取博客列表
        #1，访问者 - visitor
        #2，博主 - author
        try:
            author = UserProfile.objects.get(username=author_id)
        except Exception as e:
            result = {'code':10303, 'error':'The author is not existed !'}
            return JsonResponse(result)

        visitor_username = get_user_by_request(request)
        is_self = False

        t_id = request.GET.get('t_id')
        if t_id:
            #取指定文章id的数据
            if visitor_username == author.username:
                is_self = True
                #博主访问自己
                try:
                    author_topic = Topic.objects.get(id=t_id,author=author)
                except Exception as e:
                    result = {'code':10308, 'errir': 'No topic'}
                    return JsonResponse(result)
            else:
                try:
                    author_topic = Topic.objects.get(id=t_id, limit='public', author=author)
                except Exception as e:
                    result = {'code': 10309, 'errir': 'No topic'}
                    return JsonResponse(result)
            #生成具体返回
            res = self.make_topic_res(author, author_topic, is_self)
            return JsonResponse(res)

        else:
            #文章列表页数据
            category = request.GET.get('category')
            filter_category = False
            if category in ['tec', 'no-tec']:
                #判断是否符合要求
                filter_category = True

            if visitor_username == author.username:
                #博主访问自己的博客，可获取 公开+私人的内容
                if filter_category:
                    author_topics = Topic.objects.filter(author_id=author_id, category=category)
                else:
                    author_topics = Topic.objects.filter(author_id=author_id)
            else:
                #非博主访问，只获取 公开 内容
                if filter_category:
                    author_topics = Topic.objects.filter(author_id=author_id,limit='public', category=category)
                else:
                    author_topics = Topic.objects.filter(author_id=author_id, limit='public')
            res = self.make_topics_res(author, author_topics)
            return JsonResponse(res)


    @method_decorator(logging_check)
    def post(self, request, author_id):
        #发表博客 - 校验登录
        author = request.myuser
        json_str = request.body
        json_obj = json.loads(json_str)

        title = json_obj['title']
        #防止xss注入
        title = html.escape(title)
        content = json_obj['content']
        #根据提交的纯文本内容，切割30个字作为简介
        content_text = json_obj['content_text']
        introduce = content_text[:30]

        limit = json_obj['limit']
        if limit not in ['public', 'private']:
            result = {'code':10300, 'error':'Please give me right limit'}
            return JsonResponse(result)
        category = json_obj['category']
        #TODO 检查同上

        #插入数据
        Topic.objects.create(title=title,content=content,limit=limit,category=category,introduce=introduce, author=author)
        #删除相关缓存
        self.clear_topics_caches(request)
        return JsonResponse({'code':200, 'username':author.username})





