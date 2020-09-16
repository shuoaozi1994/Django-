from django.http import JsonResponse
from django.shortcuts import render
from tools.logging_dec import logging_check
from topic.models import Topic
from .models import Message
import json
#10400-10499

# Create your views here.
@logging_check
def message_view(request, topic_id):
    #/v1/messages/topic_id

    user = request.myuser
    json_str = request.body
    json_obj = json.loads(json_str)
    content = json_obj.get('content')
    parent_id = int(json_obj.get('parent_id', 0))

    #创建留言、回复
    try:
        topic = Topic.objects.get(id=topic_id)
    except Exception as e:
        result = {'code':10400, 'error':'The topic is not existed'}
        return JsonResponse(result)

    Message.objects.create(topic=topic, content=content,parent_message=parent_id, publisher=user)
    return JsonResponse({'code':200})








