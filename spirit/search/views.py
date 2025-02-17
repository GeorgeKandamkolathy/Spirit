# -*- coding: utf-8 -*-

from django.http import request
from django.shortcuts import redirect
from haystack.inputs import Raw
from haystack.query import SearchQuerySet
from haystack.views import SearchView as BaseSearchView
from haystack.query import SQ
from djconfig import config
from datetime import datetime


from spirit.core.utils import json_response
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from spirit.core.utils.views import post_data
from spirit.core.utils.paginator import paginate


from .forms import AdvancedSearchForm, BaseSearchForm
from ..core.utils.paginator import yt_paginate
from ..comment.models import Comment

class SearchView(BaseSearchView):
    """
    This view does not pre load data from\
    the database (``load_all=False``),\
    all required fields to display the\
    results must be stored (ie: ``indexed=False``).

    Avoid doing ``{{ result.object }}`` to\
    prevent database hits.
    """
    def __init__(self, *args, **kwargs):  # no-qa   
        super(SearchView, self).__init__(
            template='spirit/search/search.html',
            form_class=BaseSearchForm,
            load_all=True)

    def build_page(self):
        paginator = None
        results = self.results.visible(self.request.user)
        for result in self.results:
            print(result.user)
            print(str(self.request.user.id))
        paginator = paginate(
            results,
            per_page=config.topics_per_page,
            page_number=self.request.GET.get('page', 1))
        page = [
            {'title': r.title, 'main_category_name':r.category.title, 'comment_count': r.comment_count, 'last_active': r.last_active,
             'pk': r.pk}
            for r in paginator]
        print(paginator)
        return paginator, page
    
    def extra_context(self):
        extra = super(SearchView, self).extra_context()

        extra['user'] = self.request.user

        return extra

def date_filter(request):

    if request.method == 'POST': 
        data = post_data(request)
        print(data)
        if data['start'] != '':
            start = datetime.strptime(data['start'], '%Y-%m-%d')
        else:
            start = datetime.now()
        if data['end'] != '':
            end = datetime.strptime(data['end'], '%Y-%m-%d')
        else:
            end = datetime.now()
        comments = Comment.objects.with_polls(user=request.user).filter(custom_date__range=[start, end])
        comments = paginate(
            comments,
            per_page=config.comments_per_page,
            page_number=request.GET.get('page', 1))

    return redirect('/forum/search/date/?min='+ start.strftime('%Y-%m-%d') +'&max=' + end.strftime('%Y-%m-%d'))

def date_paginate(request):

    start = request.GET.get('min')
    end = request.GET.get('max')
    start = datetime.strptime(start, '%Y-%m-%d')
    end = datetime.strptime(end, '%Y-%m-%d')

    commentsObjs = Comment.objects.with_polls(user=request.user).visible(request.user).filter(custom_date__range=[start, end])
    comments = paginate(
        commentsObjs,
        per_page=config.comments_per_page,
        page_number=request.GET.get('page', 1))

    return render(
        request=request,
        template_name='spirit/search/date.html',
        context={'comments': comments})

