from mock import Mock, patch

from django.test import TestCase, Client
from django.forms import ValidationError

from colab_gitlab.signals import (create_gitlab_user,
                                  update_basic_info_gitlab_user,
                                  delete_user)
from colab_gitlab.password_validators import min_length
from colab_gitlab.models import GitlabUser


class GitlabTest(TestCase):

    def setUp(self):
        self.client = Client()

        super(GitlabTest, self).setUp()

    @patch('colab_gitlab.signals.settings.COLAB_APPS')
    @patch('colab_gitlab.signals.requests.post')
    @patch('colab_gitlab.signals.LOGGER.error')
    def test_create_user_with_invalid_token(self, LOGGER_error_mock,
                                            resquests_post_mock,
                                            COLAB_APPS_mock):
        resquests_post_mock.return_value = Mock(
            status_code=500,
            json=lambda: {'message': 'Unauthorized'}
        )

        COLAB_APPS_mock.return_value = {
            'colab_gitlab': {
                'private_token': "TestToken",
                'upstream': "https://testeurl.com/",
                'verify_ssl': True,
            },
        }

        user = Mock(
            email="mail@mail.com",
            username="testuser",
            get_full_name=lambda: "Full Name Test"
        )

        create_gitlab_user(None, user=user, password="password")

        error_msg = (u'Error trying to update "{}" password on Gitlab.' +
                     ' Reason: {}')
        error_msg = error_msg.format(user.username, 'Unknown.')
        LOGGER_error_mock.assert_called_with(error_msg)

    @patch('colab_gitlab.signals.settings.COLAB_APPS')
    @patch('colab_gitlab.signals.requests.post')
    @patch('colab_gitlab.signals.LOGGER.error')
    def test_create_user_with_invalid_request(self, LOGGER_error_mock,
                                              resquests_post_mock,
                                              COLAB_APPS_mock):
        resquests_post_mock.side_effect = Exception()

        COLAB_APPS_mock.return_value = {
            'colab_gitlab': {
                'private_token': "TestToken",
                'upstream': "https://testeurl.com/",
                'verify_ssl': True,
            },
        }

        user = Mock(
            email="mail@mail.com",
            username="testuser",
            get_full_name=lambda: "Full Name Test"
        )

        create_gitlab_user(None, user=user, password="password")

        reason = 'Request to API failed ({})'.format(Exception())
        error_msg = (u'Error trying to update "{}" password on Gitlab.' +
                     ' Reason: {}')
        error_msg = error_msg.format(user.username, reason)
        LOGGER_error_mock.assert_called_with(error_msg)

    @patch('colab_gitlab.signals.settings.COLAB_APPS')
    @patch('colab_gitlab.signals.requests.post')
    @patch('colab_gitlab.signals.LOGGER.error')
    def test_create_user_with_invalid_password(self, LOGGER_error_mock,
                                               resquests_post_mock,
                                               COLAB_APPS_mock):
        resquests_post_mock.return_value = Mock(
            status_code=500,
            json=lambda: {'message': {'password': 'test password'}}
        )

        COLAB_APPS_mock.return_value = {
            'colab_gitlab': {
                'private_token': "TestToken",
                'upstream': "https://testeurl.com/",
                'verify_ssl': True,
            },
        }

        user = Mock(
            email="mail@mail.com",
            username="testuser",
            get_full_name=lambda: "Full Name Test"
        )

        create_gitlab_user(None, user=user, password="password")

        error_msg = (u'Error trying to update "{}" password on Gitlab.' +
                     ' Reason: {}')
        error_msg = error_msg.format(user.username, 'test password')
        LOGGER_error_mock.assert_called_with(error_msg)

    @patch('colab_gitlab.signals.settings.COLAB_APPS')
    @patch('colab_gitlab.signals.requests.post')
    @patch('colab_gitlab.signals.LOGGER.info')
    def test_create_user_with_valid_token(self, LOGGER_info_mock,
                                          resquests_post_mock,
                                          COLAB_APPS_mock):
        resquests_post_mock.return_value = Mock(
            status_code=201,
            json=lambda: {'message': 'Unauthorized'}
        )

        COLAB_APPS_mock.return_value = {
            'colab_gitlab': {
                'private_token': "TestToken",
                'upstream': "https://testeurl.com/",
                'verify_ssl': True,
            },
        }

        user = Mock(
            email="mail@mail.com",
            username="testuser",
            get_full_name=lambda: "Full Name Test"
        )

        create_gitlab_user(None, user=user, password="password")

        msg = ('Gitlab user "%s" created')
        LOGGER_info_mock.assert_called_with(msg, user.username)

    def test_password_validator(self):
        password = "1234567"
        self.assertRaises(ValidationError, min_length, password)
        password = "12345678"
        self.assertEquals(None, min_length(password))


    @patch('colab_gitlab.signals.settings.COLAB_APPS')
    @patch('colab_gitlab.signals.requests.put')
    @patch('colab_gitlab.signals.LOGGER.info')
    def test_update_user_with_valid_token(self, LOGGER_info_mock,
                                          resquests_post_mock,
                                          COLAB_APPS_mock):

        resquests_post_mock.return_value = Mock(
            status_code=200,
            json=lambda: {'message': 'Unauthorized'}
        )

        COLAB_APPS_mock.return_value = {
            'colab_gitlab': {
                'private_token': "TestToken",
                'upstream': "https://testeurl.com/",
                'verify_ssl': True,
            },
        }

        user = Mock(
            email="mail@mail.com",
            username="testuser",
            get_full_name=lambda: "Full Name Test"
        )
        GitlabUser.objects.get_or_create(id=1,username="testuser")

        update_basic_info_gitlab_user(None, user=user, password="password")

        msg = ('Gitlab user\'s basic info "%s" updated')
        LOGGER_info_mock.assert_called_with(msg, user.username)

    @patch('colab_gitlab.signals.settings.COLAB_APPS')
    @patch('colab_gitlab.signals.requests.put')
    @patch('colab_gitlab.signals.LOGGER.error')
    def test_update_user_with_invalid_request(self, LOGGER_error_mock,
                                              resquests_post_mock,
                                              COLAB_APPS_mock):
        resquests_post_mock.side_effect = Exception()

        COLAB_APPS_mock.return_value = {
            'colab_gitlab': {
                'private_token': "TestToken",
                'upstream': "https://testeurl.com/",
                'verify_ssl': True,
            },
        }

        user = Mock(
            email="mail@mail.com",
            username="testuser",
            get_full_name=lambda: "Full Name Test"
        )

        GitlabUser.objects.get_or_create(id=1,username="testuser")

        update_basic_info_gitlab_user(None, user=user)

        error_msg = u'Error trying to update "{}"\'s basic info on Gitlab. Reason: {}'
        reason = 'Request to API failed ({})'.format(Exception())
        error_msg = error_msg.format(user.username,reason)
        LOGGER_error_mock.assert_called_with(error_msg)

    @patch('colab_gitlab.signals.settings.COLAB_APPS')
    @patch('colab_gitlab.signals.requests.put')
    @patch('colab_gitlab.signals.LOGGER.error')
    def test_update_user_with_invalid_token(self, LOGGER_error_mock,
                                            resquests_post_mock,
                                            COLAB_APPS_mock):

        resquests_post_mock.return_value = Mock(
            status_code=500,
            json=lambda: {'message': 'Unauthorized'}
        )

        COLAB_APPS_mock.return_value = {
            'colab_gitlab': {
                'private_token': "TestToken",
                'upstream': "https://testeurl.com/",
                'verify_ssl': True,
            },
        }

        user = Mock(
            email="mail@mail.com",
            username="testuser",
            get_full_name=lambda: "Full Name Test"
        )

        GitlabUser.objects.get_or_create(id=1,username="testuser")

        update_basic_info_gitlab_user(None, user=user)

        error_msg = u'Error trying to update "{}"\'s basic info on Gitlab. Reason: {}'
        error_msg = error_msg.format(user.username,'Unknown.')
        LOGGER_error_mock.assert_called_with(error_msg)

    @patch('colab_gitlab.signals.settings.COLAB_APPS')
    @patch('colab_gitlab.signals.requests.delete')
    @patch('colab_gitlab.signals.LOGGER.info')
    def test_delete_user_with_valid_token(self, LOGGER_info_mock,
                                          resquests_post_mock,
                                          COLAB_APPS_mock):

        resquests_post_mock.return_value = Mock(
            status_code=201,
            json=lambda: {'message': 'Unauthorized'}
        )

        COLAB_APPS_mock.return_value = {
            'colab_gitlab': {
                'private_token': "TestToken",
                'upstream': "https://testeurl.com/",
                'verify_ssl': True,
            },
        }

        user = Mock(
            email="mail@mail.com",
            username="testuser",
            get_full_name=lambda: "Full Name Test"
        )
        GitlabUser.objects.get_or_create(id=1,username="testuser")

        delete_user(None, user=user)

        msg = 'Gitlab user "{}" deleted'.format(user.username)
        LOGGER_info_mock.assert_called_with(msg)
        self.assertEquals(0,len(GitlabUser.objects.filter(id=1)))

    @patch('colab_gitlab.signals.settings.COLAB_APPS')
    @patch('colab_gitlab.signals.requests.delete')
    @patch('colab_gitlab.signals.LOGGER.error')
    def test_delete_user_with_invalid_request(self, LOGGER_error_mock,
                                              resquests_post_mock,
                                              COLAB_APPS_mock):
        resquests_post_mock.side_effect = Exception()

        COLAB_APPS_mock.return_value = {
            'colab_gitlab': {
                'private_token': "TestToken",
                'upstream': "https://testeurl.com/",
                'verify_ssl': True,
            },
        }

        user = Mock(
            email="mail@mail.com",
            username="testuser",
            get_full_name=lambda: "Full Name Test"
        )

        GitlabUser.objects.get_or_create(id=1,username="testuser")

        delete_user(None, user=user)

        error_msg = u'Error trying to delete "{}" on Gitlab. Reason: {}'
        reason = 'Request to API failed ({})'.format(Exception())
        error_msg = error_msg.format(user.username,reason)
        LOGGER_error_mock.assert_called_with(error_msg)

    @patch('colab_gitlab.signals.settings.COLAB_APPS')
    @patch('colab_gitlab.signals.requests.delete')
    @patch('colab_gitlab.signals.LOGGER.error')
    def test_delete_user_with_invalid_token(self, LOGGER_error_mock,
                                            resquests_post_mock,
                                            COLAB_APPS_mock):

        resquests_post_mock.return_value = Mock(
            status_code=500,
            json=lambda: {'message': 'Unauthorized'}
        )

        COLAB_APPS_mock.return_value = {
            'colab_gitlab': {
                'private_token': "TestToken",
                'upstream': "https://testeurl.com/",
                'verify_ssl': True,
            },
        }

        user = Mock(
            email="mail@mail.com",
            username="testuser",
            get_full_name=lambda: "Full Name Test"
        )

        GitlabUser.objects.get_or_create(id=1,username="testuser")

        delete_user(None, user=user)

        error_msg = u'Error trying to delete "{}" on Gitlab. Reason: {}'
        error_msg = error_msg.format(user.username,'Unknown.')
        LOGGER_error_mock.assert_called_with(error_msg)
