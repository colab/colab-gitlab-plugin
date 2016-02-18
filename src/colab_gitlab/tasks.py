from colab_gitlab.views import GitlabProxyView
from urllib3.exceptions import MaxRetryError
import logging
import re
logger = logging.getLogger(__name__)


def get_location(response):
    location = response.get('Location')
    return re.sub('(.*)/gitlab/', '', location)


def set_cookies(request, name, value):
    request.COOKIES.set(name, value)
    request.META['HTTP_COOKIE'] += '; {}={}'.format(name, value)


def set_session_as_cookie(response, request, session_key,
                          cookie_key):
    session = response.cookies.get(session_key).value
    set_cookies(request, cookie_key, session)

    return session


def authenticate_user(sender, user, request, **kwargs):
    request.method = 'GET'
    try:
        proxy_view = GitlabProxyView()
        gitlab_response = proxy_view.dispatch(request, 'profile')
    except MaxRetryError:
        logger.info("Couldn't connect to gitlab")
        return

    location = get_location(gitlab_response)
    set_cookies(request, '_remote_user', user.username)
    gitlab_response = proxy_view.dispatch(request, location)

    location = get_location(gitlab_response)
    set_session_as_cookie(gitlab_response, request, '_gitlab_session',
                          '_gitlab_session')
    gitlab_response = proxy_view.dispatch(request, location)

    session = set_session_as_cookie(gitlab_response, request,
                                    '_gitlab_session', '__gitlab_session')
    request.COOKIES.set('_gitlab_session', session, path="/gitlab")

    request.method = 'POST'


def logout_user(sender, user, request, **kwargs):
    request.COOKIES.delete('__gitlab_session')
    request.COOKIES.delete('_gitlab_session', path='/gitlab')
    request.COOKIES.delete('_remote_user')
