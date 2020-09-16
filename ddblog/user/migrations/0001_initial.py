# Generated by Django 2.2.12 on 2020-07-28 02:12

from django.db import migrations, models
import user.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('username', models.CharField(max_length=11, primary_key=True, serialize=False, verbose_name='用户名')),
                ('nickname', models.CharField(max_length=30, verbose_name='昵称')),
                ('email', models.EmailField(max_length=254)),
                ('password', models.CharField(max_length=32, verbose_name='密码')),
                ('sign', models.CharField(default=user.models.random_sign, max_length=50, verbose_name='个人签名')),
                ('info', models.CharField(default='', max_length=150, verbose_name='个人简介')),
                ('avatar', models.ImageField(null=True, upload_to='avatar')),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'user_user_profile',
            },
        ),
    ]