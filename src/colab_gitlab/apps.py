
from colab.plugins.utils.apps import ColabPluginAppConfig
from colab.signals.signals import register_signal, connect_signal

from colab_gitlab.tasks import handling_method


class GitlabPluginAppConfig(ColabPluginAppConfig):
    name = 'colab_gitlab'
    verbose_name = 'Gitlab Plugin'
    short_name = 'gitlab'
    namespace = 'gitlab'

    signals_list = ['gitlab_create_project']

    def register_signal(self):
        register_signal(self.short_name, self.signals_list)

    def connect_signal(self):
        connect_signal(self.signals_list[0], self.short_name, handling_method)

    def ready(self):
        from . import signals  # noqa
        super(GitlabPluginAppConfig, self).ready()
