# -*- coding: utf-8 -*-

from django import core
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils import timezone

from ..user.models import UserProfile

from ..core.conf import settings
from ..core.utils.models import AutoSlugField
from .managers import CategoryQuerySet
from django.utils.text import slugify


User = get_user_model()

class Category(models.Model):
    """
    Category model

    :ivar reindex_at: Last time this model was marked\
    for reindex. It makes the search re-index the topic,\
    it must be set explicitly
    :vartype reindex_at: `:py:class:models.DateTimeField`
    """
    parent = models.ForeignKey(
        'self',
        verbose_name=_("category parent"),
        null=True,
        blank=True,
        on_delete=models.CASCADE)

    title = models.CharField(_("title"), max_length=75)
    project_id = models.IntegerField(default=0)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.CharField(_("description"), max_length=255, blank=True)
    color = models.CharField(
        _("color"), max_length=7, blank=True,
        help_text=_("Title color in hex format (i.e: #1aafd0)."))
    sort = models.PositiveIntegerField(_("sorting order"), default=0)
    reindex_at = models.DateTimeField(_("modified at"), default=timezone.now)

    is_global = models.BooleanField(
        _("global"), default=True,
        help_text=_(
            'Designates whether the topics will be'
            'displayed in the all-categories list.'))
    is_closed = models.BooleanField(_("closed"), default=False)
    is_removed = models.BooleanField(_("removed"), default=False)
    is_private = models.BooleanField(_("private"), default=False)

    users = models.ManyToManyField(User, default=1, null=True, blank=True)

    objects = CategoryQuerySet.as_manager()

    class Meta:
        ordering = ['title', 'pk']
        verbose_name = _("category")
        verbose_name_plural = _("categories")

    def get_absolute_url(self):
        if self.pk == settings.ST_TOPIC_PRIVATE_CATEGORY_PK:
            return reverse('spirit:topic:private:index')
        else:
            return reverse(
                'spirit:category:detail',
                kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        """Override the save method to auto-generate a slug and add the owner to members if not already exist"""
        if not self.pk:
            # If the project hasn't been created yet, it won't have a PK, thus we can auto-generate the slug
            self.slug = slugify(self.title)

            # The slug should be unique and if it exists already, append a counter to the end
            suffix = Category.objects.filter(slug__startswith=self.slug).count()

            if suffix:
                self.slug = f'{self.slug}-{suffix + 1}'

        # Have to save the model before accessing many-to-many fields
        super().save(*args, **kwargs)

    @property
    def is_subcategory(self):
        if self.parent_id:
            return True
        else:
            return False

    def __str__(self) -> str:
        return self.title