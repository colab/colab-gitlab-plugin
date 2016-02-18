from django.contrib.auth.signals import user_logged_in, user_logged_out
from colab_gitlab.tasks import authenticate_user, logout_user
from colab.plugins.utils.apps import ColabPluginAppConfig
from colab.signals.signals import register_signal


class GitlabPluginAppConfig(ColabPluginAppConfig):
    name = 'colab_gitlab'
    verbose_name = 'Gitlab Plugin'
    short_name = 'gitlab'
    namespace = 'gitlab'

    signals_list = ['gitlab_create_project']

    def register_signal(self):
        register_signal(self.short_name, self.signals_list)

    def connect_signal(self):
        user_logged_in.connect(authenticate_user)
        user_logged_out.connect(logout_user)

    def ready(self):
        from . import signals  # noqa
        super(GitlabPluginAppConfig, self).ready()
