import os
import sys

from django.conf import settings
from django.shortcuts import redirect
from colab.plugins.views import ColabProxyView


class GitlabProxyView(ColabProxyView):
    app_label = 'colab_gitlab'
    diazo_theme_template = 'proxy/gitlab.html'
    rewrite = (
        (r'^/[^/]+/profile/password/edit/?$', 'password_change'),
        ('^/gitlab/users/sign_in(.*)$', r'{}\1'.format(settings.LOGIN_URL)),
    )

    def verify_forbidden_path(self, request):
        path = request.path

        prefix = settings.COLAB_APPS['colab_gitlab'].get('urls')
        prefix = prefix.get('prefix').replace('^', '/')
        forbidden = '{}profile'.format(prefix)

        if forbidden in path and not request.is_ajax():
            return True
        return False

    def dispatch(self, request, *args, **kwargs):

        self.request = request

        if self.verify_forbidden_path(self.request):
            tab = '#gitlab_profile'
            path = r'/account/{}/edit'.format(self.request.user)

            if 'groups' in self.request.path:
                path += '?path={}/'.format(request.path)

            return redirect(path+tab)

        return super(GitlabProxyView, self).dispatch(request, *args, **kwargs)


class GitlabProfileProxyView(ColabProxyView):
    app_label = 'colab_gitlab'
    diazo_theme_template = 'widgets/gitlab_profile.html'

    @property
    def diazo_rules(self):
        child_class_file = sys.modules[self.__module__].__file__
        app_path = os.path.abspath(os.path.dirname(child_class_file))
        diazo_path = os.path.join(app_path, 'widgets/profile/diazo.xml')

        self.log.debug("diazo_rules: %s", diazo_path)
        return diazo_path
