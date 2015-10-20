from django.utils.translation import ugettext as _

def get_filters(request):
    return {
        'gitlab_projects': {
            'name': _(u'Projects'),
            'icon': 'hdd',
            'fields': (
                ('title', _(u'Name'), request.GET.get('title')),
                (
                    'description',
                    _(u'Description'), 
                    request.GET.get('description'),
                ),
            ),
        },
        'gitlab_merge_requests': {
            'name': _(u'Merge Requests'),
            'icon': 'random',
            'fields': (
                ('title', _(u'Name'), request.GET.get('title')),
                (
                    'description',
                    _(u'Description'), 
                    request.GET.get('description'),
                ),
                ('tag', _(u'State'), request.GET.get('tag')),
            ),
        },
        'gitlab_issues': {
            'name': _(u'Issues'),
            'icon': 'info-sign',
            'fields': (
                ('title', _(u'Name'), request.GET.get('title')),
                (
                    'description',
                    _(u'Description'), 
                    request.GET.get('description'),
                ),
                ('tag', _(u'State'), request.GET.get('tag')),
            ),
        },
        'gitlab_comments': {
            'name': _(u'Comments'),
            'icon': 'comment',
            'fields': (
                ('title', _(u'Name'), request.GET.get('title')),
                (
                    'description',
                    _(u'Description'), 
                    request.GET.get('description'),
                ),
            ),
        },
    }
