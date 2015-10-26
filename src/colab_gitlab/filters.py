from django.utils.translation import ugettext as _


def get_filters(request):
    return {
        'gitlab_projects': {
            'name': _(u'Projects'),
            'icon': 'hdd',
            'fields': (
                ('title', _(u'Name'), ''),
                (
                    'description',
                    _(u'Description'),
                    request.get('description'),
                ),
            ),
        },
        'gitlab_merge_requests': {
            'name': _(u'Merge Requests'),
            'icon': 'random',
            'fields': (
                ('title', _(u'Name'), request.get('title')),
                (
                    'description',
                    _(u'Description'),
                    request.get('description'),
                ),
                ('tag', _(u'State'), request.get('tag')),
            ),
        },
        'gitlab_issues': {
            'name': _(u'Issues'),
            'icon': 'info-sign',
            'fields': (
                ('title', _(u'Name'), request.get('title')),
                (
                    'description',
                    _(u'Description'),
                    request.get('description'),
                ),
                ('tag', _(u'State'), request.get('tag')),
            ),
        },
        'gitlab_comments': {
            'name': _(u'Comments'),
            'icon': 'comment',
            'fields': (
                ('title', _(u'Name'), request.get('title')),
                (
                    'description',
                    _(u'Description'),
                    request.get('description'),
                ),
            ),
        },
    }
