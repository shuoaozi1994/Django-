from django.urls import path
from . import views

urlpatterns = [
    #v1/topics/author_id
    path('<str:author_id>', views.TopicView.as_view())


]