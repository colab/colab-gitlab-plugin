from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib import messages
from colab_gitlab.views import GitlabProxyView, GitlabProfileProxyView
from colab.widgets.widget_profile import  ProfileWidget
import re
from django.utils.safestring import mark_safe


class GitlabProfileWidget(GitlabProxyView, ProfileWidget):
    identifier = 'gitlab_profile'
    name = _('Development')
    tmp_session_key = '__gitlab_session'
    new_session_key = '_gitlab_session'
    app_name = 'colab_gitlab'

    def default_url(self, request):
        return '{}/profile/account'.format(self.prefix)

    def dispatch(self, request, url):
        gitlab_proxy_view = GitlabProfileProxyView()

        self.add_session_cookie(request)

        if request.COOKIES.get(self.new_session_key, '') == '':
            messages.error(request, _('Something went wrong with gitlab '
                                      'authentication, please relog.'))
            return

        response = gitlab_proxy_view.dispatch(request, url)

        if response.status_code == 302:
            request.method = 'GET'
            response = gitlab_proxy_view.dispatch(request, self.fix_url(response.get('Location')))

        self.remove_session_cookie(request)

        return response

    def add_session_cookie(self, request):
        request.COOKIES.set(self.new_session_key,
                            request.COOKIES.get(self.tmp_session_key, ''))
        cookie_text = request.META['HTTP_COOKIE'].replace(self.tmp_session_key,
                                                          self.new_session_key)
        request.META['HTTP_COOKIE'] = cookie_text

    def remove_session_cookie(self, request):
        del request.COOKIES[self.new_session_key]
        cookie_text = request.META['HTTP_COOKIE'].replace(self.new_session_key,
                                                          self.tmp_session_key)
        request.META['HTTP_COOKIE'] = cookie_text
