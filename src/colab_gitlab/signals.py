
import logging

import requests

from django.conf import settings
from django.dispatch import receiver

from colab.accounts.signals import user_password_changed

LOGGER = logging.getLogger('colab.plugins.gitlab')


@receiver(user_password_changed)
def update_gitlab_password(sender, **kwargs):
    user = kwargs.get('user')
    password = kwargs.get('password')

    app_config = settings.COLAB_APPS.get('colab_gitlab', {})
    private_token = app_config.get('private_token')
    upstream = app_config.get('upstream', '').rstrip('/')

    users_endpoint = '{}/api/v3/users'.format(upstream)

    params = {'username': user.username, 'private_token': private_token}
    response = requests.get(users_endpoint, params=params)

    users = response.json()

    error_msg = u'Error trying to update "%s" password on Gitlab. Reason: %s'

    for gitlab_user in users:
        if gitlab_user.get('username') == user.username:
            break
    else:
        reason = u'Username not found on Gitlab'
        LOGGER.error(error_msg, user.username, reason)
        return

    params = {'private_token': private_token, 'password': password}
    response = requests.put('{}/{}'.format(users_endpoint, gitlab_user['id']),
                            params=params)

    if response.status_code != 200:
        fail_data = response.json()
        if 'message' in fail_data:
            reason = fail_data['message'].get('password')
        else:
            reason = 'Unknown.'
        LOGGER.error(error_msg, user.username, reason)
        return

    LOGGER.info('User "%s" password updated on Gitlab.', user.username)
