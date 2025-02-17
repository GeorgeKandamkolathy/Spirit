# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import Http404
from django.db.models import Q


from spirit.core.utils.http import safe_redirect
from spirit.core.utils.paginator import paginate
from spirit.core.utils.views import is_post, post_data, is_ajax
from spirit.core.utils.ratelimit.decorators import ratelimit
from spirit.core.utils.decorators import moderator_required
from spirit.core.utils import markdown, paginator, render_form_errors, json_response
from spirit.topic.models import Topic
from .models import Comment, CommentTag
from .forms import CommentForm, CommentMoveForm, CommentImageForm, CommentFileForm, CommentTagForm
from .utils import comment_posted, post_comment_update, pre_comment_update, post_comment_move

from .report import ReportMaker


@login_required
@ratelimit(rate='1/10s')
def publish(request, topic_id, pk=None):
    initial = None
    if pk:  # todo: move to form
        comment = get_object_or_404(
            Comment.objects.for_access(user=request.user), pk=pk)
        quote = markdown.quotify(comment.comment, comment.user.st.nickname)
        initial = {'comment': quote}

    user = request.user
    topic = get_object_or_404(
        Topic.objects.visible(user),
        pk=topic_id)
    form = CommentForm(
        user=user,
        topic=topic,
        data=post_data(request),
        initial=initial)
    
    if is_post(request) and not request.is_limited() and form.is_valid():
        if not user.st.update_post_hash(form.get_comment_hash()):
            # Hashed comment may have not been saved yet
            default_url = lambda: (Comment
                .get_last_for_topic(topic_id)
                .get_absolute_url())
            return safe_redirect(request, 'next', default_url, method='POST')

        comment = form.save()
        print(form.mentions)
        comment_posted(comment=comment, mentions=form.mentions)
        return safe_redirect(request, 'next', comment.get_absolute_url(), method='POST')

    return render(
        request=request,
        template_name='spirit/comment/publish.html',
        context={
            'form': form,
            'topic': topic})


@login_required
def update(request, pk):
    comment = Comment.objects.for_update_or_404(pk, request.user)
    form = CommentForm(data=post_data(request), instance=comment)
    if is_post(request) and form.is_valid():
        pre_comment_update(comment=Comment.objects.get(pk=comment.pk))
        comment = form.save()
        post_comment_update(comment=comment)
        return safe_redirect(request, 'next', comment.get_absolute_url(), method='POST')
    return render(
        request=request,
        template_name='spirit/comment/update.html',
        context={'form': form})


@moderator_required
def delete(request, pk, remove=True):
    comment = get_object_or_404(Comment, pk=pk)
    if is_post(request):
        (Comment.objects
         .filter(pk=pk)
         .update(is_removed=remove))
        return safe_redirect(request, 'next', comment.get_absolute_url())
    return render(
        request=request,
        template_name='spirit/comment/moderate.html',
        context={'comment': comment})


@require_POST
@moderator_required
def move(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    form = CommentMoveForm(topic=topic, data=request.POST)

    if form.is_valid():
        comments = form.save()

        for comment in comments:
            comment_posted(comment=comment, mentions=None)
            topic.decrease_comment_count()
            post_comment_move(comment=comment, topic=topic)
    else:
        messages.error(request, render_form_errors(form))

    return safe_redirect(request, 'next', topic.get_absolute_url(), method='POST')


def find(request, pk):
    comment = get_object_or_404(Comment.objects.select_related('topic'), pk=pk)
    comment_number = (
        Comment.objects
        .filter(topic=comment.topic, date__lte=comment.date)
        .count())
    url = paginator.get_url(
        comment.topic.get_absolute_url(),
        comment_number,
        10,
        'page')
    return redirect(url)


@require_POST
@login_required
def image_upload_ajax(request):
    if not is_ajax(request):
        return Http404()

    form = CommentImageForm(
        user=request.user, data=request.POST, files=request.FILES)

    if form.is_valid():
        image = form.save()
        return json_response({'url': image.url})

    return json_response({'error': dict(form.errors.items())})


@require_POST
@login_required
def file_upload_ajax(request):
    if not is_ajax(request):
        return Http404()

    form = CommentFileForm(
        user=request.user, data=request.POST, files=request.FILES)

    if form.is_valid():
        file = form.save()
        return json_response({'url': file.url})

    return json_response({'error': dict(form.errors.items())})


def tag_form(request):
    form = CommentTagForm(
    )

    return render(
        request=request,
        template_name='spirit/comment/create.html',
        context={
            'form': form
            })

def create(request):

    form = CommentTagForm(
        data=post_data(request),
    )

    if is_post(request) and form.is_valid():
        tag = form.save()

        return redirect(reverse('spirit:comment:index'))

def find_tag(request, tag_name, category):

    tag = get_object_or_404(CommentTag, name=tag_name)

    comments = (
        Comment.objects.with_polls(user=request.user).visible(request.user).filter(Q(tag=tag, topic__category__title=category) | Q(tag=tag, topic__category__parent__title=category)))

    #comment_report(tag_name, category)
    filename = "comment_report_" + tag_name + "_" + category + ".pdf"
    report_file = '/media/reports/tags/' + filename

    comments = paginate(
        comments,
        per_page=20,
        page_number=request.GET.get('page', 1))

    return render(
        request=request,
        template_name='spirit/comment/find.html',
        context={
            'comments': comments,
            'tag' : tag,
            'report_url': report_file
        })

def index(request):
    tags = CommentTag.objects.all()
    

    return render(
        request=request,
        template_name='spirit/comment/index.html',
        context={
            'tags' : tags
        }
    )

def tag_delete(request, tag_name):
    tag = CommentTag.objects.get(name=tag_name)

    tag.delete()

    print("OKOKOKO")

    return redirect("spirit:comment:index")

def comment_report(tag_name, category):
    print(tag_name)
    tag = CommentTag.objects.get(name=tag_name)
    comments = Comment.objects.filter(Q(tag=tag, topic__category__title=category) | Q(tag=tag, topic__category__parent__title=category)).values()

    report = ReportMaker(
    temp_filepath="media_root/media/reports/tags/")

    filename = "comment_report_" + tag_name + "_" + category + ".pdf"

    report.make_comment_report(comments=comments, tag_name=tag_name, filepath="media_root/media/reports/tags/"+ filename)
    