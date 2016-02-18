from django.utils.translation import ugettext_lazy as _
from colab_gitlab.views import GitlabProxyView, GitlabProfileProxyView
from colab.widgets.widget_manager import Widget
import re


class GitlabProfileWidget(GitlabProxyView, Widget):
    identifier = 'gitlab_profile'
    name = _('Development')
    default_url = '/gitlab/profile/account'

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
            requested_url = self.default_url
        else:
            requested_url = path

        self.change_request_method(request)
        requested_url = self.fix_requested_url(requested_url)

        gitlab_proxy_view = GitlabProfileProxyView()
        self.login_in_gitlab(request)
        response = gitlab_proxy_view.dispatch(request, requested_url)

        if response.status_code == 302:
            requested_url = self.fix_requested_url(response.get('Location'))
            request.method = 'GET'
            response = gitlab_proxy_view.dispatch(request, requested_url)

        if hasattr(response, 'content'):
            self.content = response.content
        else:
            self.content = "".join(response.streaming_content)

    def fix_requested_url(self, url):
        return re.sub('^(.*)/gitlab/', '', url)

    def login_in_gitlab(self, request):
        token = '32e80744e104cd10c909289694ea1164'
        request.COOKIES['_remote_user'] = 'macartur'
        request.COOKIES['_gitlab_session'] = token
        request.META['HTTP_COOKIE'] += '; _remote_user=macartur; _gitlab_session='+token
