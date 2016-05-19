# -*- coding: utf-8 -*-

import string

from haystack import indexes
from haystack.utils import log as logging

from .models import (GitlabProject, GitlabMergeRequest,
                     GitlabIssue, GitlabComment)


logger = logging.getLogger('haystack')

# The string maketrans always return a string encoded with latin1
# http://stackoverflow.com/questions/1324067/how-do-i-get-str-translate-to-work-with-unicode-strings
table = string.maketrans(
    string.punctuation,
    '.' * len(string.punctuation)
).decode('latin1')


class GitlabProjectIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True, stored=False)
    title = indexes.EdgeNgramField(model_attr='name')
    description = indexes.EdgeNgramField(model_attr='description', null=True)
    tag = indexes.EdgeNgramField()
    url = indexes.EdgeNgramField(model_attr='url', indexed=False)
    icon_name = indexes.EdgeNgramField()
    type = indexes.EdgeNgramField()
    created = indexes.DateTimeField(model_attr='created_at', null=True)

    def prepare_tag(self, obj):
        return u"{}".format(obj.name_with_namespace.split('/')[0].strip())

    def get_ful_name(self):
        self.objs.name

    def get_model(self):
        return GitlabProject

    def prepare_type(self, obj):
        return u'project'


class GitlabMergeRequestIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.EdgeNgramField(document=True, use_template=True, stored=False)
    title = indexes.EdgeNgramField(model_attr='title')
    description = indexes.EdgeNgramField(model_attr='description')
    tag = indexes.EdgeNgramField(model_attr='state')
    url = indexes.EdgeNgramField(model_attr='url', indexed=False)
    icon_name = indexes.EdgeNgramField()
    type = indexes.EdgeNgramField(model_attr='type')

    modified_by = indexes.EdgeNgramField(model_attr='modified_by', null=True)
    modified_by_url = indexes.EdgeNgramField(model_attr='modified_by_url',
                                        null=True)
    modified = indexes.DateTimeField(model_attr='created_at', null=True)

    def get_model(self):
        return GitlabMergeRequest

    def prepare_type(self, obj):
        return u'merge_request'


class GitlabIssueIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.EdgeNgramField(document=True, use_template=True, stored=False)
    title = indexes.EdgeNgramField(model_attr='title')
    description = indexes.EdgeNgramField(model_attr='description')
    tag = indexes.EdgeNgramField(model_attr='state')
    url = indexes.EdgeNgramField(model_attr='url', indexed=False)
    icon_name = indexes.EdgeNgramField()
    type = indexes.EdgeNgramField(model_attr='type')

    modified_by = indexes.EdgeNgramField(model_attr='modified_by', null=True)
    modified_by_url = indexes.EdgeNgramField(model_attr='modified_by_url',
                                        null=True)
    modified = indexes.DateTimeField(model_attr='created_at', null=True)

    def get_model(self):
        return GitlabIssue

    def prepare_type(self, obj):
        return u'issue'


class GitlabCommentIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.EdgeNgramField(document=True, use_template=True, stored=False)
    title = indexes.EdgeNgramField(model_attr='title')
    description = indexes.EdgeNgramField(model_attr='description')
    tag = indexes.EdgeNgramField()
    url = indexes.EdgeNgramField(model_attr='url', indexed=False)
    icon_name = indexes.EdgeNgramField()
    type = indexes.EdgeNgramField(model_attr='type')

    modified_by = indexes.EdgeNgramField(model_attr='modified_by', null=True)
    modified_by_url = indexes.EdgeNgramField(model_attr='modified_by_url',
                                        null=True)
    modified = indexes.DateTimeField(model_attr='created_at', null=True)

    def get_model(self):
        return GitlabComment

    def prepare_tag(self, obj):
        return obj.tag

    def prepare_type(self, obj):
        return u'comment'
