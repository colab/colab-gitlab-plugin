from mock import Mock, patch

from django.test import TestCase, Client
from django.forms import ValidationError

from colab_gitlab.signals import create_gitlab_user
from colab_gitlab.password_validators import min_length


class GitlabTest(TestCase):

    fixtures = ['test_gitlab_data']

    def setUp(self):
        self.client = Client()

        super(GitlabTest, self).setUp()

    def tearDown(self):
        pass

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

        error_msg = (u'Error trying to update "%s" password on Gitlab.' +
                     ' Reason: %s')
        LOGGER_error_mock.assert_called_with(error_msg,
                                             user.username, 'Unknown.')

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
        error_msg = (u'Error trying to update "%s" password on Gitlab.' +
                     ' Reason: %s')
        LOGGER_error_mock.assert_called_with(error_msg, user.username, reason)

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

        error_msg = (u'Error trying to update "%s" password on Gitlab.' +
                     ' Reason: %s')
        LOGGER_error_mock.assert_called_with(error_msg,
                                             user.username, 'test password')

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
