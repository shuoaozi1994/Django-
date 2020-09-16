from django.db import models
from topic.models import Topic
from user.models import UserProfile

# Create your models here.
class Message(models.Model):
    #留言和回复
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    content = models.CharField(max_length=100, verbose_name='留言回复内容')
    publisher = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    parent_message = models.IntegerField(verbose_name='回复留言的id',default=0)


