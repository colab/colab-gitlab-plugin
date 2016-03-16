from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib import messages
from colab_gitlab.views import GitlabProxyView, GitlabProfileProxyView
from colab.widgets.widget_manager import Widget
import re
from django.utils.safestring import mark_safe


class GitlabProfileWidget(GitlabProxyView, Widget):
    identifier = 'gitlab_profile'
    name = _('Development')
    tmp_session_key = '__gitlab_session'
    new_session_key = '_gitlab_session'
    colab_form = None

    def default_url(self):
        gitlab_prefix = settings.COLAB_APPS['colab_gitlab'].get('urls')
        gitlab_prefix = gitlab_prefix.get('prefix').replace('^', '/')
        return gitlab_prefix + 'profile/account'

    def fix_url(self, url):
        return re.sub('^.*/gitlab/', '', url)

    def is_colab_form(self, request):
        if self.colab_form is None:
            self.colab_form = request.POST.get('colab_form', False)
        return self.colab_form

    def must_respond(self,request):
        return not self.is_colab_form(request) and '/gitlab' in request.GET.get('path','')

    def change_request_method(self, request):
        if not len(request.POST) or not self.must_respond(request):
            request.method = "GET"
        elif not request.POST.get("_method", None):
            request.method = "POST"
        else:
            request.method = request.POST.get("_method").upper()

    def requested_url(self, request):
        url = request.GET.get('path', '')
        if not url or not self.must_respond(request):
            url = self.default_url()

        return self.fix_url(url)

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

    def generate_content(self, **kwargs):
        request = kwargs.get('context', {}).get('request', None)

        self.change_request_method(request)
        response = self.dispatch(request, self.requested_url(request))

        if hasattr(response, 'content'):
            self.content = response.content
        else:
            self.content = "".join(response.streaming_content)


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
