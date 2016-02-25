from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from colab_gitlab.views import GitlabProxyView, GitlabProfileProxyView
from colab.widgets.widget_manager import Widget
import re


class GitlabProfileWidget(GitlabProxyView, Widget):
    identifier = 'gitlab_profile'
    name = _('Development')
    tmp_session_key = '__gitlab_session'
    new_session_key = '_gitlab_session'

    def default_url(self):
        gitlab_prefix = settings.COLAB_APPS['colab_gitlab'].get('urls')
        gitlab_prefix = gitlab_prefix.get('prefix').replace('^', '/')
        return gitlab_prefix + 'profile/account'

    def change_request_method(self, request):
        if not len(request.POST) or request.POST.get('colab_form', None):
            request.method = "GET"
        elif not request.POST.get("_method", None):
            request.method = "POST"
        else:
            request.method = request.POST.get("_method").upper()

    def generate_content(self, **kwargs):
        request = kwargs.get('context', {}).get('request', None)
        is_colab_form = request.POST.get('colab_form', False)
        path = request.GET.get('path', '')

        if is_colab_form or not path:
            requested_url = self.default_url()
        else:
            requested_url = path

        self.change_request_method(request)
        requested_url = self.fix_requested_url(requested_url)

        gitlab_proxy_view = GitlabProfileProxyView()

        self.add_session_cookie(request)

        response = gitlab_proxy_view.dispatch(request, requested_url)

        if response.status_code == 302:
            requested_url = self.fix_requested_url(response.get('Location'))
            request.method = 'GET'
            response = gitlab_proxy_view.dispatch(request, requested_url)

        if hasattr(response, 'content'):
            self.content = response.content
        else:
            self.content = "".join(response.streaming_content)

        self.remove_session_cookie(request)

    def fix_requested_url(self, url):
        return re.sub('^(.*)/gitlab/', '', url)

    def add_session_cookie(self, request):
        request.COOKIES.set(self.new_session_key,
                            request.COOKIES[self.tmp_session_key])
        cookie_text = request.META['HTTP_COOKIE'].replace(self.tmp_session_key,
                                                          self.new_session_key)
        request.META['HTTP_COOKIE'] = cookie_text

    def remove_session_cookie(self, request):
        del request.COOKIES[self.new_session_key]
        cookie_text = request.META['HTTP_COOKIE'].replace(self.new_session_key,
                                                          self.tmp_session_key)
        request.META['HTTP_COOKIE'] = cookie_text
