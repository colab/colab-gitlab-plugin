
import logging

import requests

from django.conf import settings
from django.dispatch import receiver

from .models import GitlabUser
from colab.accounts.signals import (user_password_changed, user_created,
                                    user_basic_info_updated, delete_user)

LOGGER = logging.getLogger('colab.plugins.gitlab')


@receiver(user_password_changed)
def update_gitlab_password(sender, **kwargs):
    user = kwargs.get('user')
    password = kwargs.get('password')

    app_config = settings.COLAB_APPS.get('colab_gitlab', {})
    private_token = app_config.get('private_token')
    upstream = app_config.get('upstream', '').rstrip('/')
    verify_ssl = app_config.get('verify_ssl', True)

    error_msg = u'Error trying to update "{}" password on Gitlab. Reason: {}'

    users_endpoint = '{}/api/v3/users'.format(upstream)

    params = {'search': user.username, 'private_token': private_token}
    try:
        response = requests.get(users_endpoint, params=params,
                                verify=verify_ssl)
    except Exception as excpt:
        reason = 'Request to API failed ({})'.format(excpt)
        error_msg = error_msg.format(user.username, reason)
        LOGGER.error(error_msg)
        return

    users = []
    try:
        users = response.json()
    except ValueError:
        pass

    if 'message' in users:
        if '401' in users['message']:
            reason = 'Unknown.'
            LOGGER.error(error_msg, user.username, reason)
            return

    for gitlab_user in users:
        if gitlab_user.get('username') == user.username:
            break
    else:
        reason = u'Username not found on Gitlab'
        LOGGER.error(error_msg, user.username, reason)
        return

    params = {'private_token': private_token, 'password': password}
    request_url = '{}/{}'.format(users_endpoint, gitlab_user['id'])
    try:
        response = requests.put(request_url, params=params, verify=verify_ssl)
    except Exception as excpt:
        reason = 'Request to API failed ({})'.format(excpt)
        LOGGER.error(error_msg, user.username, reason)
        return

    if response.status_code != 200:
        reason = 'Unknown.'

        try:
            fail_data = response.json()

            if 'message' in fail_data:
                fail_data_message = fail_data['message']
                if (isinstance(fail_data_message, dict) and
                        'password' in fail_data_message):
                    reason = fail_data['message'].get('password')

        except ValueError as value_error:
            # Some responses do not return a valid json, e.g. 204 and 502
            reason = '{} :: {}'.format(response.status_code,
                                       value_error.message)

        LOGGER.error(error_msg, user.username, reason)
        return

    LOGGER.info('User "%s" password updated on Gitlab.', user.username)


@receiver(user_created)
def create_gitlab_user(sender, **kwargs):
    user = kwargs.get('user')
    password = kwargs.get('password')

    app_config = settings.COLAB_APPS.get('colab_gitlab', {})
    private_token = app_config.get('private_token')
    upstream = app_config.get('upstream', '').rstrip('/')
    verify_ssl = app_config.get('verify_ssl', True)

    users_endpoint = '{}/api/v3/users'.format(upstream)

    params = {
        'email': user.email,
        'password': password,
        'username': user.username,
        'name': user.get_full_name(),
        'extern_uid': user.username,
        'provider': 'remoteuser',
        'confirm': False,
        'private_token': private_token,
    }

    error_msg = u'Error trying to update "{}" password on Gitlab. Reason: {}'
    try:
        response = requests.post(users_endpoint, params=params,
                                 verify=verify_ssl)
    except Exception as excpt:
        reason = 'Request to API failed ({})'.format(excpt)
        error_msg = error_msg.format(user.username, reason)
        LOGGER.error(error_msg)
        return

    if response.status_code != 201:
        reason = 'Unknown.'

        try:
            fail_data = response.json()

            if 'message' in fail_data:
                fail_data_message = fail_data['message']
                if (isinstance(fail_data_message, dict) and
                        'password' in fail_data_message):
                    reason = fail_data['message'].get('password')

        except ValueError as value_error:
            # Some responses do not return a valid json, e.g. 204 and 502
            reason = '{} :: {}'.format(response.status_code,
                                       value_error.message)
        error_msg = error_msg.format(user.username, reason)
        LOGGER.error(error_msg)
        return

    LOGGER.info('Gitlab user "%s" created', user.username)


@receiver(user_basic_info_updated)
def update_basic_info_gitlab_user(sender, **kwargs):
    user = kwargs.get('user')
    update_email = kwargs.get('update_email')

    gitlab_user = GitlabUser.objects.filter(username=user.username).first()

    if not gitlab_user:
        return

    app_config = settings.COLAB_APPS.get('colab_gitlab', {})
    private_token = app_config.get('private_token')
    upstream = app_config.get('upstream', '').rstrip('/')
    verify_ssl = app_config.get('verify_ssl', True)

    users_endpoint = '{}/api/v3/users/{}'.format(upstream, gitlab_user.id)

    params = {
        'name': user.get_full_name(),
        'private_token': private_token,
        'website_url': user.webpage,
        'bio': user.bio,
    }

    if update_email:
        params['email'] = user.email

    error_msg = (u'Error trying to update "{}"\'s basic info on Gitlab.'
                 ' Reason: {}')
    try:
        response = requests.put(users_endpoint,
                                params=params, verify=verify_ssl)

    except Exception as excpt:
        reason = 'Request to API failed ({})'.format(excpt)
        error_msg = error_msg.format(user.username, reason)
        LOGGER.error(error_msg)
        return

    if response.status_code != 200:
        reason = 'Unknown.'

        try:
            fail_data = response.json()

            if 'message' in fail_data:
                fail_data_message = fail_data['message']
                # TODO: take care of gitlab error messages
                if (isinstance(fail_data_message, dict) and
                        'password' in fail_data_message):
                    reason = fail_data['message'].get('password')

        except ValueError as value_error:
            # Some responses do not return a valid json, e.g. 204 and 502
            reason = '{} :: {}'.format(response.status_code,
                                       value_error.message)
        error_msg = error_msg.format(user.username, reason)
        LOGGER.error(error_msg)
        return

    LOGGER.info('Gitlab user\'s basic info "%s" updated', user.username)


@receiver(delete_user)
def delete_user(sender, **kwargs):
    user = kwargs.get('user')

    gitlab_user = GitlabUser.objects.filter(username=user.username).first()

    if not gitlab_user:
        return

    app_config = settings.COLAB_APPS.get('colab_gitlab', {})
    private_token = app_config.get('private_token')
    upstream = app_config.get('upstream', '').rstrip('/')
    verify_ssl = app_config.get('verify_ssl', True)

    users_endpoint = '{}/api/v3/users/{}'.format(upstream, gitlab_user.id)

    params = {
        'private_token': private_token
    }

    error_msg = u'Error trying to delete "{}" on Gitlab. Reason: {}'
    try:
        response = requests.delete(users_endpoint,
                                   params=params, verify=verify_ssl)
    except Exception as excpt:
        reason = 'Request to API failed ({})'.format(excpt)
        error_msg = error_msg.format(user.username, reason)
        LOGGER.error(error_msg)
        return

    if response.status_code != 201:
        reason = 'Unknown.'

        try:
            fail_data = response.json()

            if 'message' in fail_data:
                fail_data_message = fail_data['message']
                # TODO: take care of gitlab error messages
                if (isinstance(fail_data_message, dict) and
                        'password' in fail_data_message):
                    reason = fail_data['message'].get('password')

        except ValueError as value_error:
            # Some responses do not return a valid json, e.g. 204 and 502
            reason = '{} :: {}'.format(response.status_code,
                                       value_error.message)

        error_msg = error_msg.format(user.username, reason)
        LOGGER.error(error_msg)
        return

    gitlab_user.delete()

    msg = 'Gitlab user "{}" deleted'.format(user.username)
    LOGGER.info(msg)
