from mock import patch

from django.test import TestCase
from django.http import HttpRequest, HttpResponse, StreamingHttpResponse
from colab_gitlab.widgets.profile.profile import GitlabProfileWidget
from colab_gitlab.views import GitlabProfileProxyView


class WidgetsTest(TestCase):

    module_path = 'colab_gitlab.widgets.profile.profile.GitlabProfileWidget'

    def setUp(self):
        self.profile_widget = GitlabProfileWidget()
        self.current_request = HttpRequest()
        self.current_request.method = 'POST'

        self.http_response = HttpResponse()
        self.streaming_http_response = StreamingHttpResponse()

    def test_change_request_method_with_colab_form(self):
        self.current_request.POST = {'colab_form': 'true'}
        self.profile_widget.change_request_method(self.current_request)

        self.assertEquals(self.current_request.method, 'GET')

    def test_change_request_method_with_GET_request(self):
        self.current_request.POST = {}
        self.current_request.method = 'GET'
        self.profile_widget.change_request_method(self.current_request)

        self.assertEquals(self.current_request.method, 'GET')

    def test_change_request_method_with_post_and_no__method(self):
        self.current_request.POST = {'user': 'sample_user'}
        self.profile_widget.change_request_method(self.current_request)

        self.assertEquals(self.current_request.method, 'POST')

    def test_change_request_method_with_post_and__method(self):
        self.current_request.POST = {'_method': 'sample_method',
                                     'user': 'sample_user'}
        self.profile_widget.change_request_method(self.current_request)

        self.assertEquals(self.current_request.method, 'SAMPLE_METHOD')

    def test_fix_requested_url(self):
        url = 'http://localhost:8000/gitlab/account/test'
        self.assertEquals(self.profile_widget.fix_requested_url(url),
                          'account/test')

        url = 'http://localhost:8000/account/test'
        self.assertEquals(self.profile_widget.fix_requested_url(url),
                          url)

    @patch(module_path + '.fix_requested_url')
    @patch(module_path + '.login_in_gitlab')
    @patch.object(GitlabProfileProxyView, 'dispatch')
    def test_generate_content(
            self, dispatch_mock, login_in_gitlab_mock, fix_requested_url_mock):
        fix_requested_url_mock.return_value = 'test'
        login_in_gitlab_mock.return_value = None

        self.http_response.status_code = 302
        self.http_response['Location'] = 'test/url'

        content = '<head></head><body></body>'
        self.http_response.content = content

        dispatch_mock.return_value = self.http_response

        self.current_request.POST = {'colab_form': True}
        self.current_request.GET = {'path': '/gitlab/test'}
        self.current_request.META['HTTP_COOKIE'] = ''
        params = {'context': {'request': self.current_request}}

        self.profile_widget.generate_content(**params)
        self.assertEquals(content, self.profile_widget.content)
        self.assertEquals(2, dispatch_mock.call_count)

        self.current_request.POST = {}
        self.current_request.GET = {}
        self.profile_widget.generate_content(**params)
        self.assertEquals(content, self.profile_widget.content)

        self.current_request.GET = {'path': '/gitlab/test'}
        self.profile_widget.generate_content(**params)
        self.assertEquals(content, self.profile_widget.content)

        self.http_response.status_code = 200
        self.current_request.POST = {'colab_form': True}
        self.profile_widget.generate_content(**params)
        self.assertEquals(content, self.profile_widget.content)

    @patch(module_path + '.fix_requested_url')
    @patch(module_path + '.login_in_gitlab')
    @patch.object(GitlabProfileProxyView, 'dispatch')
    def test_generate_content_using_streaming_content(
            self, dispatch_mock, login_in_gitlab_mock, fix_requested_url_mock):

        login_in_gitlab_mock.return_value = None
        fix_requested_url_mock.return_value = 'test'

        self.streaming_http_response.status_code = 200
        dispatch_mock.return_value = self.streaming_http_response

        streaming_content = ["sample ", "streaming ", "string ", "content."]
        self.streaming_http_response.streaming_content = streaming_content
        self.current_request.META['HTTP_COOKIE'] = ''

        params = {'context': {'request': self.current_request}}
        self.profile_widget.generate_content(**params)

        content = ''.join(streaming_content)
        self.assertEquals(content, self.profile_widget.content)

    def test_login_in_gitlab(self):
        cookie = 'test_key'
        self.current_request.META['HTTP_COOKIE'] = '__gitlab_session='+cookie
        self.current_request.COOKIES['__gitlab_session'] = cookie
        self.profile_widget.login_in_gitlab(self.current_request)

        self.assertIn('_gitlab_session',
                      self.current_request.META['HTTP_COOKIE'])
        self.assertIn('_gitlab_session', self.current_request.COOKIES)

        self.assertEquals(cookie,
                          self.current_request.COOKIES['_gitlab_session'])
