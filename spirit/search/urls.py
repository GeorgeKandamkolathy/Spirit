# -*- coding: utf-8 -*-

from django.conf.urls import re_path
from django.urls import path
from . import views


app_name = 'search'
urlpatterns = [
    re_path(r'date/$', views.date_filter, name='date'),
    re_path(r'^$', views.SearchView(), name='search'),

]
