# -*- coding: utf-8 -*-

from django.db.models import Q

from haystack import indexes
from haystack.fields import MultiValueField

from ..category.models import Category

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

class IntegerMultiValueField(MultiValueField):
    field_type = 'integer' 

    def prepare(self, obj):
        return self.convert(super(IntegerMultiValueField, self).prepare(obj))

    def convert(self, value):
        if value is None:
            return None

        if hasattr(value, "__iter__") and not isinstance(value, int):
            return value

        return [value]
<<<<<<< HEAD
=======

TEXT_FIELD = indexes.CharField
if settings.ST_NGRAM_SEARCH:
    TEXT_FIELD = indexes.NgramField

>>>>>>> nitely-master

class TopicIndex(indexes.SearchIndex, indexes.Indexable):

    text = TEXT_FIELD(document=True, use_template=True, stored=False)
    category_id = indexes.IntegerField(model_attr='category_id', stored=False)
    is_removed = BooleanField(stored=False)

    title = indexes.CharField(model_attr='title', indexed=False)
    slug = indexes.CharField(model_attr='slug', indexed=False)
    comment_count = indexes.IntegerField(model_attr='comment_count', indexed=False)
    last_active = indexes.DateTimeField(model_attr='last_active', indexed=False)
    main_category_name = indexes.CharField(indexed=False)
    user = MultiValueField(null=True)
    private = indexes.BooleanField(null=True)
    removed = indexes.BooleanField(null=True)

    def prepare_user(self, obj):
        category = Category.objects.get(id=obj.category_id)
        users = []
        for user in category.users.all():
            users = users + [user.id]
        print(category.users.all())
        return users
    
    def prepare_public(self, obj):
        category = Category.objects.get(id=obj.category_id)
        return category.is_private
    
    def prepare_removed(self, obj):
        category = Category.objects.get(id=obj.category.id)
        if obj.category.parent != None:
            if obj.category.parent.is_removed==True:
                print("parent")
                return True
        if obj.category.is_removed==True:
            print("cat")
            return True
        if obj.is_removed==True:
            print("topic")
            return True
        print("ok")
        return False
    
    # Overridden
    def get_model(self):
        return Topic

    # Overridden
    def index_queryset(self, using=None):
        return (Topic.objects.all())