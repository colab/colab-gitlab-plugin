class CookiePostHandlerMiddleware(object):
    """
    CookiePostHandlerMiddleware used to avoid gitlab_exipres cookie
    """

    def process_response(self, request, response):
        gitlab_session = response.cookies.get('_gitlab_session', '')
        if gitlab_session:
            gitlab_session['expires'] = None

        return response
