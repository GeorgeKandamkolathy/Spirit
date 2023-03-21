# -*- coding: utf-8 -*-

from django.urls import re_path
from django.urls import path
from . import views


app_name = 'search'
urlpatterns = [
    re_path(r'date/form$', views.date_filter, name='date'),
    re_path(r'date/$', views.date_paginate, name='date_page'),
    re_path(r'^$', views.SearchView(), name='search'),

]
