class CookiePostHandlerMiddleware(object):
    """
    CookiePostHandlerMiddleware used to avoid gitlab expires cookie
    before the colab cookies
    """

    def process_response(self, request, response):
        colab_session = request.COOKIES.get('sessionid', '')

        if colab_session:
            response.cookies.pop('_gitlab_session', '')

        return response
