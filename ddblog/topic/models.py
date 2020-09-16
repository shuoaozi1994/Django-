from django.db import models
from user.models import UserProfile

# Create your models here.

class Topic(models.Model):

    title = models.CharField(max_length=90, verbose_name='文章标题')
    #tec-技术 no-tec-非技术类
    category = models.CharField(max_length=20, verbose_name='文章分类')
    #public-公开 private-私有的
    limit = models.CharField(max_length=10, verbose_name='文章权限')
    introduce = models.CharField(max_length=90, verbose_name='文章简介')
    content = models.TextField(verbose_name='文章内容')
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)



