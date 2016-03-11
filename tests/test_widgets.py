from mock import patch

from django.test import TestCase
from django.http import HttpRequest, HttpResponse, StreamingHttpResponse

from colab_gitlab.widgets.profile.profile import GitlabProfileWidget
from colab_gitlab.views import GitlabProfileProxyView
from colab.middlewares.cookie_middleware import CookieHandler


class WidgetsTest(TestCase):

    module_path = 'colab_gitlab.widgets.profile.profile.GitlabProfileWidget'

    def setUp(self):
        self.profile_widget = GitlabProfileWidget()
        self.current_request = HttpRequest()
        self.current_request.method = 'POST'

        self.http_response = HttpResponse()
        self.streaming_http_response = StreamingHttpResponse()

    def test_default_url(self):
        self.assertEquals(self.profile_widget.default_url(),
                          '/gitlab/profile/account')

    def create_cookie_handler(self, cookie_name, session):
        cookie = cookie_name
        cookies = CookieHandler()
        cookies.set(session, cookie)

        return cookies

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
    @patch(module_path + '.add_session_cookie')
    @patch(module_path + '.remove_session_cookie')
    @patch('colab_gitlab.widgets.profile.profile.messages.error')
    @patch.object(GitlabProfileProxyView, 'dispatch')
    def test_generate_content(
            self, dispatch_mock, error_mock, remove_session_cookie,
            add_session_cookie, fix_requested_url_mock):
        fix_requested_url_mock.return_value = 'test'

        error_mock.side_effect = lambda request_arg, msg: msg

        self.http_response.status_code = 302
        self.http_response['Location'] = 'test/url'

        content = '<head></head><body></body>'
        self.http_response.content = content

        dispatch_mock.return_value = self.http_response

        self.current_request.POST = {'colab_form': True}
        self.current_request.GET = {'path': '/gitlab/test'}
        self.current_request.META['HTTP_COOKIE'] = ''
        self.current_request.COOKIES = {'_gitlab_session': ''}
        params = {'context': {'request': self.current_request}}

        self.assertEquals('', self.profile_widget.content)

        self.current_request.COOKIES = {'_gitlab_session': 'test_token'}
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
    @patch(module_path + '.add_session_cookie')
    @patch(module_path + '.remove_session_cookie')
    @patch('colab_gitlab.widgets.profile.profile.messages.error')
    @patch.object(GitlabProfileProxyView, 'dispatch')
    def test_generate_content_using_streaming_content(
            self, dispatch_mock, error_mock, remove_session_cookie,
            add_session_cookie, fix_requested_url_mock):

        fix_requested_url_mock.return_value = 'test'
        error_mock.side_effect = lambda request_arg, msg: msg

        self.streaming_http_response.status_code = 200
        dispatch_mock.return_value = self.streaming_http_response

        streaming_content = ["sample ", "streaming ", "string ", "content."]
        self.streaming_http_response.streaming_content = streaming_content
        self.current_request.META['HTTP_COOKIE'] = ''
        self.current_request.COOKIES = {'_gitlab_session': 'test_token'}

        params = {'context': {'request': self.current_request}}
        self.profile_widget.generate_content(**params)

        content = ''.join(streaming_content)
        self.assertEquals(content, self.profile_widget.content)

    def test_add_session_cookie(self):
        cookie_name = 'test_cookie'
        session = '__gitlab_session'

        cookies = self.create_cookie_handler(cookie_name, session)

        self.current_request.META['HTTP_COOKIE'] = session+"="+cookie_name
        self.current_request.COOKIES = cookies
        self.profile_widget.add_session_cookie(self.current_request)

        self.assertIn('_gitlab_session',
                      self.current_request.META['HTTP_COOKIE'])
        self.assertIn('_gitlab_session', self.current_request.COOKIES)

        self.assertEquals(cookie_name,
                          self.current_request.COOKIES['_gitlab_session'])

    def test_remove_session_cookie(self):
        cookie_name = 'test_cookie'
        session = '_gitlab_session'

        cookies = self.create_cookie_handler(cookie_name, session)

        expected_http_cookie = '__gitlab_session='+cookie_name

        self.current_request.COOKIES = cookies
        self.current_request.META['HTTP_COOKIE'] = session+"="+cookie_name

        self.profile_widget.remove_session_cookie(self.current_request)

        self.assertEqual(0,  len(self.current_request.COOKIES))
        self.assertEqual(expected_http_cookie,
                         self.current_request.META['HTTP_COOKIE'])
