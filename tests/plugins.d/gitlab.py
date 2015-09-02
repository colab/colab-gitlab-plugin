
from django.utils.translation import ugettext_lazy as _
from colab.plugins.utils.menu import colab_url_factory

# Gitlab plugin - Put this in plugins.d/gitlab.py to actiate ##
# from django.utils.translation import ugettext_lazy as _
# from colab.plugins.utils.menu import colab_url_factory

name = 'colab_gitlab'
verbose_name = 'Gitlab Plugin'

upstream = 'localhost'
#middlewares = []

urls = {
    'include': 'colab_gitlab.urls',
    'namespace': 'gitlab',  # TODO: do not allow to change namespace
    'prefix': 'gitlab',
}

menu_title = _('Code')

url = colab_url_factory('gitlab')

menu_urls = (
    url(display=_('Public Projects'), viewname='gitlab',
        kwargs={'path': '/public/projects'}, auth=False),
    url(display=_('Profile'), viewname='gitlab',
        kwargs={'path': '/profile'}, auth=True),
    url(display=_('New Project'), viewname='gitlab',
        kwargs={'path': '/projects/new'}, auth=True),
    url(display=_('Projects'), viewname='gitlab',
        kwargs={'path': '/dashboard/projects'}, auth=True),
    url(display=_('Groups'), viewname='gitlab',
        kwargs={'path': '/profile/groups'}, auth=True),
    url(display=_('Issues'), viewname='gitlab',
        kwargs={'path': '/dashboard/issues'}, auth=True),
    url(display=_('Merge Requests'), viewname='gitlab',
        kwargs={'path': '/merge_requests'}, auth=True),

)
