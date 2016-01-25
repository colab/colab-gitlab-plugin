from colab_gitlab.views import GitlabProxyView


def authenticate_user(sender, user, request, **kwargs):
    name = user.username
    proxy_view = GitlabProxyView()
    import ipdb; ipdb.set_trace()
    gitlab_response = proxy_view.dispatch(request, 'profile')
    print gitlab_response.status_code

    location = gitlab_response.get('Location')
    request.COOKIES.set('_remote_user', name)
    request.META['HTTP_COOKIE'] += '; _remote_user={}'.format(name)
    location = location.replace('/gitlab/', '')
    gitlab_response = proxy_view.dispatch(request, location)

    location = gitlab_response.get('Location')
    session = gitlab_response.cookies.get('_gitlab_session').value
    request.COOKIES.set('_gitlab_session', session)
    request.META['HTTP_COOKIE'] += '; _gitlab_session={}'.format(session)

    if gitlab_response.status_code == 200:
        request.COOKIES.set('_gitlab_session',
                            gitlab_response.cookies.get('_gitlab_session'))


def logout_user(sender, user, request, **kwargs):
    request.COOKIES.delete('_noosfero_session')
