# -*- coding: utf-8 -*-

from django.db.models.query_utils import Q
from django.http.request import QueryDict
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, get_user_model
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from ...core.utils.views import is_post, post_data
from ...core.utils.decorators import administrator_required, authenticated_required
from ..models import Category
from .forms import CategoryForm, SubCategoryForm

User = get_user_model()


@administrator_required
def index(request):
    categories = (
        Category.objects
        .filter(Q(parent=None), Q(is_private=False) | Q(users__exact=request.user))
        .ordered())
    return render(
        request=request,
        template_name='spirit/category/admin/index.html',
        context={'categories': categories})


@administrator_required
def create(request):
    form = CategoryForm(data=post_data(request))
    if is_post(request) and form.is_valid():
        form.save()
        return redirect(reverse("spirit:admin:category:index"))
    return render(
        request=request,
        template_name='spirit/category/admin/create.html',
        context={'form': form})

@authenticated_required
def create_subcategory(request, category_id):
    if (is_post(request)):
        data = request.POST.copy()
        data['parent'] = category_id
        form = SubCategoryForm(data=data)
    else:
        form = SubCategoryForm(data=post_data(request))
    if is_post(request) and form.is_valid():
        form.save()
        return redirect(reverse("spirit:topic:index-active"))
    return render(
        request=request,
        template_name='spirit/category/admin/create.html',
        context={'form': form})

@administrator_required
def update(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    form = CategoryForm(
        data=post_data(request),
        instance=category)

    if is_post(request) and form.is_valid():
        if ('is_removed' in post_data(request)):
            if(post_data(request)['is_removed']):
                categories = Category.objects.filter(parent=category)
                categories.update(is_removed=True)
        form.save()
        messages.info(request, _("The category has been updated!"))
        return redirect(reverse("spirit:admin:category:index"))

    return render(
        request=request,
        template_name='spirit/category/admin/update.html',
        context={'form': form})


# XXX fix race conditions
@require_POST
@administrator_required
def _move(request, category_id, direction):
    if direction == 'up':
        sort_filter = 'sort__lt'
        order_by = '-sort'
    else:
        assert direction == 'down'
        sort_filter = 'sort__gt'
        order_by = 'sort'

    category = get_object_or_404(
        Category.objects.select_related('parent'),
        pk=category_id)
    sibling = (
        Category.objects
        .public()
        .filter(
            parent=category.parent,
            **{sort_filter: category.sort})
        .order_by(order_by)
        .first())
    if sibling:
        sort = category.sort
        category.sort = sibling.sort
        sibling.sort = sort
        category.save()
        sibling.save()
    return redirect(reverse("spirit:admin:category:index"))


@administrator_required
def move_up(request, category_id):
    return _move(request, category_id, 'up')


@administrator_required
def move_dn(request, category_id):
    return _move(request, category_id, 'down')
