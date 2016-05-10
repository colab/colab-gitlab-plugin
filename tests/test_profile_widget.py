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
        self.current_request.COOKIES['_gitlab_session'] = 'sampleuser'
        self.current_request.method = 'POST'

        self.http_response = HttpResponse()
        self.streaming_http_response = StreamingHttpResponse()

    def test_default_url(self):
        result = self.profile_widget.default_url(self.current_request)
        self.assertEquals(result, '/gitlab/profile/account')

    def create_cookie_handler(self, cookie_name, session):
        cookie = cookie_name
        cookies = CookieHandler()
        cookies.set(session, cookie)

        return cookies

    @patch(module_path + '.add_session_cookie')
    @patch(module_path + '.remove_session_cookie')
    @patch.object(GitlabProfileProxyView, 'dispatch')
    def test_dispatch_with_redirect(self, dispatch_mock,
                                   remove_session_cookie,
                                   add_session_cookie):
        self.http_response.status_code = 302
        self.http_response['Location'] = '/gitlab/test/url'

        content = '<head></head><body></body>'
        self.http_response.content = content

        dispatch_mock.return_value = self.http_response

        url = '/gitlab/url/test'
        self.current_request.GET = {'path': url}
        self.current_request.POST = {'path': '/gitlab/test'}
        params = {'context': {'request': self.current_request}}

        result = self.profile_widget.dispatch(self.current_request, url)

        self.assertEquals(content, result.content)
        self.assertEquals(len(dispatch_mock.mock_calls),2)

    @patch(module_path + '.add_session_cookie')
    @patch(module_path + '.remove_session_cookie')
    @patch.object(GitlabProfileProxyView, 'dispatch')
    def test_dispatch_without_redirect(self, dispatch_mock,
                                       remove_session_cookie,
                                       add_session_cookie):
        self.http_response.status_code = 200

        content = '<head></head><body></body>'
        self.http_response.content = content

        dispatch_mock.return_value = self.http_response

        url = '/gitlab/url/test'
        self.current_request.GET = {'path': url}
        self.current_request.POST = {'path': '/gitlab/test'}
        params = {'context': {'request': self.current_request}}

        result = self.profile_widget.dispatch(self.current_request, url)

        self.assertEquals(content, result.content)
        self.assertEquals(len(dispatch_mock.mock_calls),1)

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
