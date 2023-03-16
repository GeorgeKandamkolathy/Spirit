# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponsePermanentRedirect

from djconfig import config

from spirit.core.utils.http import safe_redirect
from spirit.core.utils.views import is_post, post_data
from spirit.core.utils.paginator import paginate, yt_paginate
from spirit.core.utils.ratelimit.decorators import ratelimit
from spirit.category.models import Category
from spirit.comment.forms import CommentForm
from spirit.comment.utils import comment_posted
from spirit.comment.models import Comment
from .models import Topic
from .forms import TopicForm
from . import utils


@login_required
@ratelimit(rate='1/10s')
def publish(request, category_id=None):
    category = None
    if category_id:
        category = get_object_or_404(
            Category.objects.visible(request.user),
            pk=category_id)

    user = request.user
    print(post_data(request))
    form = TopicForm(
        user=user,
        data=post_data(request),
        current=category
    )
    cform = CommentForm(
        user=user,
        data=post_data(request))
    if (is_post(request) and
            all([form.is_valid(), cform.is_valid()]) and
            not request.is_limited()):
        if not user.st.update_post_hash(form.get_topic_hash()):
            default_url = lambda: form.get_category().get_absolute_url()
            return safe_redirect(
                request, 'next', default_url, method='POST')
        # wrap in transaction.atomic?
        topic = form.save()
        cform.topic = topic
        comment = cform.save()
        comment_posted(comment=comment, mentions=cform.mentions)
        return redirect(topic.get_absolute_url())
    return render(
        request=request,
        template_name='spirit/topic/publish.html',
        context={'form': form, 'cform': cform})


@login_required
def update(request, pk):
    topic = Topic.objects.for_update_or_404(pk, request.user)
    category_id = topic.category_id
    form = TopicForm(
        current="TargetCreationForm",
        user=request.user,
        data=post_data(request),
        instance=topic)
    if is_post(request) and form.is_valid():
        topic = form.save()
        if topic.category_id != category_id:
            Comment.create_moderation_action(
                user=request.user, topic=topic, action=Comment.MOVED)
        return safe_redirect(request,'next', topic.get_absolute_url(), method='POST')
    return render(
        request=request,
        template_name='spirit/topic/update.html',
        context={'form': form})


def detail(request, pk, slug):
    topic = Topic.objects.get_public_or_404(pk, request.user)

    if topic.slug != slug:
        return HttpResponsePermanentRedirect(topic.get_absolute_url())

    utils.topic_viewed(request=request, topic=topic)

    comments = (
        Comment.objects
        .for_topic(topic=topic)
        .with_likes(user=request.user)
        .with_polls(user=request.user)
        .order_by('date'))

    comments = paginate(
        comments,
        per_page=config.comments_per_page,
        page_number=request.GET.get('page', 1))

    return render(
        request=request,
        template_name='spirit/topic/detail.html',
        context={
            'topic': topic,
            'comments': comments})


def index_active(request):
    categories = (
        Category.objects
        .visible(request.user))

    topics = (
        Topic.objects
        .visible(request.user)
        .global_()
        .with_bookmarks(user=request.user)
        .order_by('-is_globally_pinned', '-last_active')
        .select_related('category'))

    topics = yt_paginate(
        topics,
        per_page=config.topics_per_page,
        page_number=request.GET.get('page', 1))

    return render(
        request=request,
        template_name='spirit/topic/active.html',
        context={
            'categories': categories,
            'topics': topics})
