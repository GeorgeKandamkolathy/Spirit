# -*- coding: utf-8 -*-

from django.db.models import Q

from haystack import indexes

from ..core.conf import settings
from ..topic.models import Topic


# See: django-haystack issue #801
# convert() from search-engine
# stored value to python value,
# so it only matters when using
# search_result.get_stored_fields()
class BooleanField(indexes.BooleanField):

    bool_map = {'true': True, 'false': False}

    def convert(self, value):
        if value is None:
            return None

        if value in self.bool_map:
            return self.bool_map[value]

        return bool(value)


TEXT_FIELD = indexes.CharField
if settings.ST_NGRAM_SEARCH:
    TEXT_FIELD = indexes.NgramField


class TopicIndex(indexes.SearchIndex, indexes.Indexable):

    text = TEXT_FIELD(document=True, use_template=True, stored=False)
    category_id = indexes.IntegerField(model_attr='category_id', stored=False)
    is_removed = BooleanField(stored=False)

    title = indexes.CharField(model_attr='title', indexed=False)
    slug = indexes.CharField(model_attr='slug', indexed=False)
    comment_count = indexes.IntegerField(model_attr='comment_count', indexed=False)
    last_active = indexes.DateTimeField(model_attr='last_active', indexed=False)
    main_category_name = indexes.CharField(indexed=False)

    # Overridden
    def get_model(self):
        return Topic

    # Overridden
    def index_queryset(self, using=None):
        return (Topic.objects.visible(self.user))