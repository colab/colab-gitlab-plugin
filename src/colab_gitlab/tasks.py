from colab_gitlab.views import GitlabProxyView
import re


def get_location(response):
    location = response.get('Location')
    return re.sub('(.*)/gitlab/', '', location)


def set_cookies(request, name, value):
    request.COOKIES.set(name, value, path='/gitlab')
    request.META['HTTP_COOKIE'] += '; {}={}'.format(name, value)


def authenticate_user(sender, user, request, **kwargs):
    request.method = 'GET'
    proxy_view = GitlabProxyView()
    gitlab_response = proxy_view.dispatch(request, 'profile')

    location = get_location(gitlab_response)
    set_cookies(request, '_remote_user', user.username)
    gitlab_response = proxy_view.dispatch(request, location)

    location = get_location(gitlab_response)
    session = gitlab_response.cookies.get('_gitlab_session').value
    set_cookies(request, '_gitlab_session', session)
    gitlab_response = proxy_view.dispatch(request, location)

    session = gitlab_response.cookies.get('_gitlab_session').value
    set_cookies(request, '_gitlab_session', session)

    request.method = 'POST'


def logout_user(sender, user, request, **kwargs):
    request.COOKIES.delete('_gitlab_session', path='/gitlab')
