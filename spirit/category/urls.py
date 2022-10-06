# -*- coding: utf-8 -*-

from django.conf.urls import re_path

from . import views


app_name = 'category'
urlpatterns = [
    re_path(r'^$', views.index, name='index'),

    re_path(r'(?P<slug>[\w-]+)/$', views.detail, name='detail'),
]
