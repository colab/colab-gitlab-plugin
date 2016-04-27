from django.db import models
from django.utils.translation import ugettext_lazy as _
from colab.plugins.utils.models import Collaboration
from hitcounter.models import HitCounterModelMixin


class GitlabProject(models.Model, HitCounterModelMixin):

    id = models.IntegerField(primary_key=True)
    description = models.TextField(blank=True, null=True)
    public = models.BooleanField(default=True)
    name = models.TextField()
    name_with_namespace = models.TextField()
    created_at = models.DateTimeField(blank=True)
    last_activity_at = models.DateTimeField(blank=True)
    path_with_namespace = models.TextField(blank=True, null=True)
    icon_name = u'hdd'

    @property
    def namespace(self):
        return self.path_with_namespace.split('/')[0]

    @property
    def url(self):
        return u'/gitlab/{}'.format(self.path_with_namespace)

    class Meta:
        verbose_name = _('Gitlab Project')
        verbose_name_plural = _('Gitlab Projects')


class GitlabGroup(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    path = models.CharField(max_length=100)
    owner_id = models.IntegerField(null=True)

    def __unicode__(self):
        return u'{}'.format(self.path)

    @property
    def projects(self):
        projects = GitlabProject.objects.all()
        result = list()
        for project in projects:
            if self.path in project.namespace:
                result.append(project)
        return result

    @property
    def url(self):
        return u'/gitlab/groups/{}'.format(self.path)

    class Meta:
        verbose_name = _('Gitlab Group')
        verbose_name_plural = _('Gitlab Groups')


class GitlabUser(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=100)

    class Meta:
        verbose_name = _('Gitlab User')
        verbose_name_plural = _('Gitlab User')


class GitlabMergeRequest(Collaboration):

    id = models.IntegerField(primary_key=True)
    iid = models.IntegerField(null=True)
    target_branch = models.TextField()
    source_branch = models.TextField()
    project = models.ForeignKey(GitlabProject, null=True,
                                on_delete=models.SET_NULL)
    description = models.TextField()
    title = models.TextField()
    state = models.TextField()
    created_at = models.DateTimeField(blank=True, null=True)

    @property
    def modified(self):
        return self.created_at

    @property
    def tag(self):
        return self.state

    type = u'merge_request'
    icon_name = u'random'

    @property
    def url(self):
        return u'/gitlab/{}/merge_requests/{}'.format(
            self.project.path_with_namespace, self.iid)

    def get_author(self):
        return self.user

    class Meta:
        verbose_name = _('Gitlab Merge Request')
        verbose_name_plural = _('Gitlab Merge Requests')

class GitlabIssue(Collaboration):

    id = models.IntegerField(primary_key=True)
    iid = models.IntegerField(null=True)
    project = models.ForeignKey(GitlabProject, null=True,
                                on_delete=models.SET_NULL)
    title = models.TextField()
    description = models.TextField()

    state = models.TextField()
    created_at = models.DateTimeField(blank=True, null=True)

    icon_name = u'info-sign'
    type = u'issue'

    @property
    def modified(self):
        return self.created_at

    @property
    def url(self):
        return u'/gitlab/{}/issues/{}'.format(
            self.project.path_with_namespace, self.iid)

    class Meta:
        verbose_name = _('Gitlab Issue')
        verbose_name_plural = _('Gitlab Issues')

class GitlabComment(Collaboration):

    id = models.IntegerField(primary_key=True)
    body = models.TextField()
    created_at = models.DateTimeField(blank=True, null=True)
    issue_comment = models.BooleanField(default=True)

    project = models.ForeignKey(GitlabProject, null=True,
                                on_delete=models.SET_NULL)

    parent_id = models.IntegerField(null=True)
    type = u'comment'

    @property
    def modified(self):
        return self.created_at

    @property
    def title(self):
        if self.issue_comment:
            issue = GitlabIssue.objects.get(id=self.parent_id)
            return issue.title
        else:
            merge_request = GitlabMergeRequest.objects.get(id=self.parent_id)
            return merge_request.title

    icon_name = u'comment'

    @property
    def description(self):
        return self.body

    @property
    def tag(self):
        if self.issue_comment:
            issue = GitlabIssue.objects.get(id=self.parent_id)
            return issue.state
        else:
            merge_request = GitlabMergeRequest.objects.get(id=self.parent_id)
            return merge_request.state

    @property
    def url(self):
        if self.issue_comment:
            url_str = u'/gitlab/{}/issues/{}#notes_{}'
        else:
            url_str = u'/gitlab/{}/merge_requests/{}#notes_{}'

        return url_str.format(self.project.path_with_namespace,
                              self.parent_id, self.id)

    class Meta:
        verbose_name = _('Gitlab Comments')
        verbose_name_plural = _('Gitlab Comments')
