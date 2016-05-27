from colab_gitlab.views import GitlabProxyView
from colab.settings import SESSION_COOKIE_AGE
from urllib3.exceptions import MaxRetryError
import logging
import re
logger = logging.getLogger(__name__)


def get_location(response):
    location = response.get('Location', '')
    return re.sub('(.*)/gitlab/', '', location)


def set_cookies(request, name, value, expires=None):
    request.COOKIES.set(name, value, expires)
    request.META['HTTP_COOKIE'] += '; {}={}'.format(name, value)


def set_session_as_cookie(response, request, session_key,
                          cookie_key, expires=None):
    session = response.cookies.get(session_key).value
    set_cookies(request, cookie_key, session, expires)

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
    set_cookies(request, '_remote_user', user.username,
                expires=SESSION_COOKIE_AGE)
    gitlab_response = proxy_view.dispatch(request, location)

    location = get_location(gitlab_response)
    if location and gitlab_response.status_code == 302:
        set_session_as_cookie(gitlab_response, request, '_gitlab_session',
                              '_gitlab_session', expires=SESSION_COOKIE_AGE)
        gitlab_response = proxy_view.dispatch(request, location)

        session = set_session_as_cookie(gitlab_response, request,
                                        '_gitlab_session', '__gitlab_session',
                                        expires=SESSION_COOKIE_AGE)
        request.COOKIES.set('_gitlab_session', session, path="/gitlab",
                            expires=SESSION_COOKIE_AGE)

    request.method = 'POST'


def logout_user(sender, user, request, **kwargs):
    request.COOKIES.delete('__gitlab_session')
    request.COOKIES.delete('_gitlab_session', path='/gitlab')
    request.COOKIES.delete('_remote_user')
